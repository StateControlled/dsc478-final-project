###############################################################

# Some code is adapted from
# https://github.com/MengtingWan/goodreads
# according to the terms of the Apache License 2.0 http://www.apache.org/licenses/

###############################################################

import pandas as pd

import argparse
import gzip
import json
import os
import sys

from core import Common

pd.options.display.float_format = '{:,}'.format

def count_interactions(file_name: str) -> tuple[int, int, int, int, int]:
    """
    Extracts some basic statistics from interaction files.
    :param file_name: the file name.
    :return: some numbers.
    """
    n_shelve, n_read, n_rate, n_review = 0, 0, 0, 0
    user_set: set = set()

    with gzip.open(file_name) as file:
        for ln in file:
            d_json = json.loads(ln)

            if n_shelve < 5:
                print(d_json)

            if n_shelve % 1000000 == 0:
                print(n_shelve, end=', ')

            n_shelve += 1
            n_read += int(d_json["is_read"])
            n_rate += int(d_json["rating"] > 0)
            n_review += int(d_json["review_text_incomplete"] != "")
            user_set.add(d_json["user_id"])
    print("Complete")

    return n_shelve, n_read, n_rate, n_review, len(user_set)


def count_lines(file_name: str) -> int:
    """
    Counts the number of records in the input file.
    :param file_name:   the file name.
    :return:    the number of records.
    """

    count: int = 0

    with gzip.open(file_name) as file:
        for _ in file:
            count += 1

    return count


def count_all_genres(input_dir: str, genre_list: list[str]) -> pd.DataFrame:
    """
    Calculate statistics for each data.
    :param input_dir:   the file name.
    :param genre_list: a list of the data names.
    :return:
    """

    res: list[list[int]] = []
    for genre in genre_list:
        item: str = f"goodreads_books_{genre}.json.gz"
        item_path: str = os.path.join(input_dir, item)

        n_book: int = count_lines(item_path)
        print(f"Counted {n_book} entries in file '{item_path}'")

        n_shelve, n_read, n_rate, n_review, n_user = count_interactions(item_path)

        res.append([n_book, n_shelve, n_read, n_rate, n_review, n_user])

    stats_by_genre: pd.DataFrame = pd.DataFrame(res, dtype=float, columns=["# book", "# user", "# shelve", "# read", "# rate", "# review"], index=genre_list)

    return stats_by_genre


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Downloads target data files from the web and saves to local disk.")
    ap.add_argument("--genres", default="data-download/targets.txt", help="A list of genres.")
    ap.add_argument("--input", default="data/", help="Source directory containing data to analyze.")
    ap.add_argument("--out", default="results/", help="Output directory")

    args = ap.parse_args(args=argv)

    genres: str = args.genres
    in_dir: str = args.input
    out_dir: str = args.out

    genre_list = Common.read_file(genres)

    stats_by_genre: pd.DataFrame = count_all_genres(in_dir, genre_list)

    for _t in ["# shelve", "# read", "# rate", "# review"]:
        stats_by_genre[_t + '/' + "book"] = stats_by_genre[_t] / stats_by_genre["# book"]
        stats_by_genre[_t + '/' + "user"] = stats_by_genre[_t] / stats_by_genre["# user"]

    stats = stats_by_genre.round(2).T
    print(stats)

    return 0


if __name__ == '__main__':
    sys.exit(main())
