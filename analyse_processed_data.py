"""A script to analyse book data."""
import argparse
import logging
import pandas as pd
import altair as alt

logging.basicConfig(
    filename="data_analysis.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


def generate_argument_parser() -> argparse.ArgumentParser:
    """Generate an argument parser for the script. This parser takes a single argument, the path to the processed data file."""
    parser = argparse.ArgumentParser(description="Analyse processed book data.")
    parser.add_argument(
        "input_file",
        type=str,
        help="The path to the processed data CSV file.",
    )
    return parser


# -- Load --

def read_processed_data(path_to_csv: str) -> pd.DataFrame:
    """Read the processed data from a CSV file. Raises a RuntimeError if no file is found."""
    logger.info(f"Reading processed data from: {path_to_csv}")
    try:
        data_frame = pd.read_csv(path_to_csv)
        logger.info(f"Successfully read {len(data_frame)} rows from {path_to_csv}")
        return data_frame
    except FileNotFoundError:
        logger.error(f"Processed data file not found: {path_to_csv}")
        raise RuntimeError(f"No file found at {path_to_csv}")


# -- Plot functions --

def plot_decade_releases(data_frame: pd.DataFrame, output_path: str) -> None:
    """Produce a pie chart showing the proportion of books released in each decade and save it to output_path."""
    logger.info("Generating decade releases pie chart.")
    df = data_frame.dropna(subset=["year"]).copy()
    df["decade"] = (df["year"] // 10 * 10).astype(int).astype(str) + "s"

    decade_counts = (
        df["decade"]
        .value_counts()
        .reset_index()
        .rename(columns={"decade": "decade", "count": "count"})
    )

    chart = (
        alt.Chart(decade_counts)
        .mark_arc()
        .encode(
            theta=alt.Theta("count:Q"),
            color=alt.Color("decade:N", legend=alt.Legend(title="Decade")),
            tooltip=["decade:N", "count:Q"],
        )
        .properties(title="Proportion of Books Released per Decade", width=400, height=400)
    )

    chart.save(output_path)
    logger.info(f"Saved decade releases pie chart to {output_path}")


def plot_top_authors(data_frame: pd.DataFrame, output_path: str) -> None:
    """Produce a sorted bar chart of the total ratings for the ten most-rated authors and save it to output_path."""
    logger.info("Generating top authors bar chart.")
    top_authors = (
        data_frame.groupby("author_name")["ratings"]
        .sum()
        .nlargest(10)
        .reset_index()
        .rename(columns={"ratings": "total_ratings"})
    )

    chart = (
        alt.Chart(top_authors)
        .mark_bar(color="steelblue")
        .encode(
            x=alt.X("total_ratings:Q", title="Total Ratings"),
            y=alt.Y("author_name:N", sort="-x", title="Author"),
            tooltip=["author_name:N", "total_ratings:Q"],
        )
        .properties(title="Top 10 Most-Rated Authors (Total Ratings)", width=500, height=300)
    )

    chart.save(output_path)
    logger.info(f"Saved top authors bar chart to {output_path}")


# -- Main --

def analyse_data(input_file: str) -> None:
    """Load the processed data and produce the required visualisations."""
    logger.info(f"Starting analysis on: {input_file}")
    data_frame = read_processed_data(input_file)
    plot_decade_releases(data_frame, "decade_releases.png")
    plot_top_authors(data_frame, "top_authors.png")
    logger.info("Analysis complete.")


if __name__ == "__main__":
    parser = generate_argument_parser()
    input_file = parser.parse_args().input_file
    print(f"Input file: {input_file}")
    analyse_data(input_file)
