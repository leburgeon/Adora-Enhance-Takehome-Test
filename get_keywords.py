"""Generates `top_keywords.png` — a bar chart of the 20 most common keywords
across all book titles in PROCESSED_DATA.csv.

Run:
    python3 get_keywords.py PROCESSED_DATA.csv
"""
import argparse
import logging
import re
from collections import Counter
from typing import List, Set

import altair as alt
import pandas as pd

logging.basicConfig(
    filename="data_analysis.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


DEFAULT_STOPWORDS: Set[str] = {
    "a", "an", "the",
    "and", "or", "but", "nor",
    "of", "in", "on", "at", "to", "for", "by", "from", "with",
    "is", "are", "was", "were", "be",
    "it", "its", "this", "that", "these", "those",
    "me", "my", "you", "your", "he", "she", "we", "our",
    "not", "no", "so", "do",
}


def read_titles(path: str) -> List[str]:
    """Read the processed CSV and return the title column as a list of strings."""
    logger.info(f"Reading titles from: {path}")
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        logger.error(f"File not found: {path}")
        raise RuntimeError(f"No file found at {path}")
    titles = df["title"].dropna().tolist()
    logger.info(f"Read {len(titles)} titles from {path}")
    return titles


def tokenize(title: str) -> List[str]:
    """Split a title into lowercase alphabetic words.

    Non-string input returns an empty list.
    """
    if not isinstance(title, str):
        return []
    return re.findall(r"[a-z]+", title.lower())


def remove_stopwords(tokens: List[str], stopwords: Set[str]) -> List[str]:
    """Return tokens that are not stopwords and are at least 3 characters long."""
    return [token for token in tokens if token not in stopwords and len(token) >= 3]


def count_keywords(titles: List[str], stopwords: Set[str]) -> Counter:
    """Count every meaningful word across all titles."""
    logger.info(f"Counting keywords across {len(titles)} titles.")
    counter: Counter = Counter()
    for title in titles:
        tokens = tokenize(title)
        keywords = remove_stopwords(tokens, stopwords)
        counter.update(keywords)
    logger.info(f"Found {len(counter)} unique keywords.")
    return counter


def top_n_keywords(counter: Counter, n: int) -> pd.DataFrame:
    """Return a DataFrame of the top n keywords ordered by count descending."""
    logger.info(f"Selecting top {n} keywords.")
    most_common = counter.most_common(n)
    return pd.DataFrame(most_common, columns=["keyword", "count"])


def plot_keywords(df: pd.DataFrame, output_path: str) -> None:
    """Save a sorted horizontal bar chart of keywords to output_path."""
    logger.info(f"Generating keywords bar chart with {len(df)} keywords.")
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("count:Q", title="Count"),
            y=alt.Y("keyword:N", sort="-x", title="Keyword"),
            tooltip=["keyword:N", "count:Q"],
        )
        .properties(title="Top Keywords in Book Titles", width=600, height=500)
    )
    chart.save(output_path)
    logger.info(f"Saved keywords bar chart to {output_path}")


def generate_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract top keywords from book titles.")
    parser.add_argument("input_file", type=str, help="Path to PROCESSED_DATA.csv")
    return parser


if __name__ == "__main__":
    args = generate_argument_parser().parse_args()
    logger.info(f"Starting keyword extraction from: {args.input_file}")
    titles = read_titles(args.input_file)
    counter = count_keywords(titles, DEFAULT_STOPWORDS)
    df = top_n_keywords(counter, n=20)
    plot_keywords(df, "top_keywords.png")
    logger.info("Keyword extraction complete.")
    print("Saved top_keywords.png")
