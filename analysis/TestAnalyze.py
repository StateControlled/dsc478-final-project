import pandas as pd

import argparse
import gzip
import json
import os
import sys

from core import Common

# columns in interactions
# "user_id",
# "book_id",
# "review_id",
# "is_read",
# "rating",
# "review_text_incomplete",
# "date_added",
# "date_updated",
# "read_at",
# "started_at"

def get_reviews(input_dir: str, genre: str) -> pd.DataFrame:
    reviews: str = os.path.join(input_dir, f"goodreads_reviews_{genre}.json.gz")
    df: pd.DataFrame = pd.read_json(reviews, lines=True)
    return df

def get_books(input_dir: str, genre: str) -> pd.DataFrame:
    books: str = os.path.join(input_dir, f"goodreads_books_{genre}.json.gz")
    df: pd.DataFrame = pd.read_json(books, lines=True)
    return df

def get_interactions(input_dir: str, genre: str) -> pd.DataFrame:
    """

    :param input_dir: directory containing the zip files.
    :param genre: the genre
    :return: a DataFrame containing interaction data that has had some preliminary cleaning.
    """
    # Interactions are the most important for what I want to do
    interactions: str = os.path.join(input_dir, f"goodreads_interactions_{genre}.json.gz")

    # each file consists of Json objects, one on each line
    df: pd.DataFrame = pd.read_json(interactions, lines=True)

    # drop unnecessary columns
    df.drop(["date_added", "date_updated", "read_at", "started_at"], axis=1, inplace=True)

    # This column may contain an empty string ("") or a string (a review of a book).
    # I'm not concerned with the content of the review for this project, so I will
    # replace empty strings with 0 and non-empty strings with 1
    df["review_text_incomplete"] = df["review_text_incomplete"].ne("").astype(int)
    df.rename(columns={"review_text_incomplete": "is_reviewed"}, inplace=True)

    # Convert from boolean to integer
    df["is_read"] = df["is_read"].astype(int)

    return df


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Downloads target data files from the web and saves to local disk.")
    ap.add_argument("--genres", default="../data-download/targets.txt", help="A list of genres.")
    ap.add_argument("--input", default="../data/archive", help="Source directory containing data to analyze.")
    ap.add_argument("--out", default="../data/raw/", help="Output directory")

    args = ap.parse_args(args=argv)

    genres: str = args.genres
    in_dir: str = args.input
    out_dir: str = args.out

    genre_list = Common.read_file(genres)

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    ################################################
    genre0 = "young_adult_short"
    frame = get_interactions(in_dir, genre0)
    file_name = os.path.join(out_dir, f"{genre0}_interactions.csv")
    frame.to_csv(file_name, index=False)

    print(frame.head(30))
    print()

    ################################################
    frame = get_books(in_dir, genre0)
    file_name = os.path.join(out_dir, f"{genre0}_books.csv")
    frame.to_csv(file_name, index=False)

    print(frame.head(30))
    print()

    ################################################
    frame = get_reviews(in_dir, genre0)
    file_name = os.path.join(out_dir, f"{genre0}_reviews.csv")
    frame.to_csv(file_name, index=False)

    print(frame.head(30))
    print()

    # for genre in genre_list:
    #     frame = get(in_dir, genre)
    #     file_name = os.path.join(out_dir, f"{genre}_interactions.csv")
    #     frame.to_csv(file_name)
    #
    #     print(frame.head(10))

    print("Complete!")
    return 0

if __name__ == "__main__":
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)

    sys.exit(main())
