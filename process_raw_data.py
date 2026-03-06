"""A script to process book data."""
import argparse
import pandas as pd
import sqlite3
import logging
import re

logging.basicConfig(
    filename="data_analysis.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

def generate_argument_parser()-> argparse.ArgumentParser:
    """Generate an argument parser for the script. This parser takes a single argument, the path to the processed data file."""
    parser = argparse.ArgumentParser(description="Analyse book data.")
    parser.add_argument(
        "input_file",
        type=str,
        help="The path to the input file containing the processed book data.",
    )
    return parser

# -- Extract functions --

def read_data_frame_from_csv(path_to_csv: str) -> pd.DataFrame:
    """ A function that takes a file path as an argument, and reads the CSV file at that location. 
    Raises a runtime exception if no file is found at that location."""
    logger.info(f"Reading CSV file from: {path_to_csv}")
    try:
        data_frame = pd.read_csv(path_to_csv)
        logger.info(f"Successfully read {len(data_frame)} rows from {path_to_csv}")
        return data_frame
    except FileNotFoundError:
        logger.error(f"CSV file not found: {path_to_csv}")
        raise RuntimeError(f"No file found at {path_to_csv}")
    
def read_dimension_table_from_database(db_path: str, table_name: str) -> pd.DataFrame:
    """ A function that takes a file path as an argument, and reads the dimensions data from the database at that location. 
    Raises a runtime exception if no database is found at that location."""
    logger.info(f"Reading dimension table '{table_name}' from database: {db_path}")
    try:
        conn = sqlite3.connect(db_path)
        dimensions_data_frame = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        conn.close()
        logger.info(f"Successfully read {len(dimensions_data_frame)} rows from table '{table_name}'")
        return dimensions_data_frame
    except sqlite3.OperationalError:
        logger.error(f"Failed to read table '{table_name}' from database: {db_path}")
        raise RuntimeError(f"No database found at {db_path}")
    finally:
        if 'conn' in locals():
            conn.close()

# -- Transform functions --

def find_title_column(column_names: list) -> str:
    """ A function that takes a list of column names as an argument, and returns the name of the column that contains the title data. 
    Raises a runtime exception if no column is found that contains the title data."""
    for column_name in column_names:
        if "title" in column_name.lower():
            return column_name
    raise RuntimeError("No column found that contains the title data.")

def format_title(title: str) -> str:
    """ A function that takes a title as an argument, and formats it by removing any information in brackets and trailing whitespace."""
    if not isinstance(title, str):
        return pd.NA
    formatted_title = re.sub(r'[\(\[\{].*?[\)\]\}]', '', title).rstrip()
    return formatted_title

def transform_title_column(data_frame: pd.DataFrame, new_column_name: str) -> pd.DataFrame:
    """ A function that takes a data frame as an argument and transforms the title column, renaming it to the new column name.
     In the raw data, many book titles also contain series or format information. To handle this, all titles should be cleaned to remove any information in brackets.
     Titles of unexpected types like floats or integers should be coerced to NaN, and the number of coerced values should be logged. The cleaned title column should be returned as a new column in the data frame."""
    title_column = find_title_column(data_frame.columns)

    data_frame[new_column_name] = data_frame[title_column].apply(format_title)

    num_coerced_values = data_frame[new_column_name].isna().sum()
    logger.info(f"Coerced {num_coerced_values} values to NaN in the title column.")

    return data_frame

def enrich_author_name(books_data: pd.DataFrame, authors_dimension: pd.DataFrame, new_author_column_name: str) -> pd.DataFrame:
    """ A function which takes the books data and the authors dimension data as arguments, and enriches the author name in the books data by joining it with the authors dimension data. 
    It first converts the author_id in the books data to an integer, and then performs a left join with the authors dimension data on the author_id column.
     Finally, it drops the author_id column from the enriched books data."""
    logger.info("Enriching author names from dimension table.")
    books_data["author_id"] = books_data["author_id"].astype(int, errors="ignore")

    enriched_books_data = books_data.merge(authors_dimension, left_on="author_id", right_on="id", how="left")

    enriched_books_data.rename(columns={"name": new_author_column_name}, inplace=True)

    enriched_books_data.drop(columns=["author_id"], inplace=True)
    logger.info(f"Author enrichment complete. {enriched_books_data[new_author_column_name].notna().sum()} authors resolved.")

    return enriched_books_data

def find_year_column(column_names: list) -> str:
    """ A function that takes a list of column names as an argument, and returns the name of the column that contains the year data. 
    Raises a runtime exception if no column is found that contains the year data."""
    for column_name in column_names:
        if "year" in column_name.lower():
            return column_name
    raise RuntimeError("No column found that contains the year data.")

def transform_year_column(data_frame: pd.DataFrame, new_column_name: str) -> pd.DataFrame:
    """ A function that takes a data frame as an argument and transforms the year column, renaming it to the new column name. 
    In the raw data, the year column contains some non-numeric values. To handle this, all non-numeric values should be removed from the year column.
    The number of removed values should be logged, and the cleaned year column should be returned as a new column in the data frame."""
    year_column = find_year_column(data_frame.columns)

    data_frame[new_column_name] = pd.to_numeric(data_frame[year_column], errors="coerce")

    num_removed_values = data_frame[new_column_name].isna().sum()
    logger.info(f"Removed {num_removed_values} non-numeric values from the year column.")

    return data_frame

def find_rating_column(column_names: list) -> str:
    """ A function that takes a list of column names as an argument, and returns the name of the column that contains the rating data. 
    Raises a runtime exception if no column is found that contains the rating data."""
    for column_name in column_names:
        if "rating" in column_name.lower():
            return column_name
    raise RuntimeError("No column found that contains the rating data.")

def format_rating(rating: str) -> float:
    """ A function that takes a rating as an argument, and formats it by converting it to a numeric value with the decimal separator as a dot. 
    If the rating is not a string, it should be coerced to NaN."""
    if not isinstance(rating, str):
        return pd.NA
    formatted_rating = rating.replace(",", ".")
    try:
        return float(formatted_rating)
    except ValueError:
        return pd.NA

def transform_rating_column(data_frame: pd.DataFrame, new_column_name: str) -> pd.DataFrame:
    """ A function that takes a data frame as an argument and transforms the rating column, renaming it to the new column name. 
    In the raw data, the rating column values are stored as strings, with the decimal separator as a comma. To handle this, all values in the rating column should be converted to numeric values, with the decimal separator as a dot."""
    rating_column = find_rating_column(data_frame.columns)
    data_frame[new_column_name] = data_frame[rating_column].apply(format_rating)
    num_coerced_values = data_frame[new_column_name].isna().sum()
    logger.info(f"Coerced {num_coerced_values} values to NaN in the rating column.")
    return data_frame

def find_ratings_column(column_names: list) -> str:
    """ A function that takes a list of column names as an argument, and returns the name of the column that contains the ratings count data. 
    Raises a runtime exception if no column is found that contains the ratings count data."""
    for column_name in column_names:
        if "ratings" in column_name.lower() or "ratings" in column_name.lower():
            return column_name
    raise RuntimeError("No column found that contains the ratings count data.")

def transform_ratings_column(data_frame: pd.DataFrame, new_column_name: str) -> pd.DataFrame:
    """ A function that takes a data frame as an argument and transforms the ratings count column, renaming it to the new column name. 
    In the raw data, the ratings are stored as `ratings` with some non-numeric values. To handle this, all values in the ratings count column should have the (`) removed, be converted to numeric values, and all non-numeric values should be removed.
    """
    ratings_count_column = find_ratings_column(data_frame.columns)
    data_frame[new_column_name] = pd.to_numeric(data_frame[ratings_count_column].str.replace("`", ""), errors="coerce")

    num_removed_values = data_frame[new_column_name].isna().sum()
    logger.info(f"Removed {num_removed_values} non-numeric values from the ratings count column.")

    return data_frame

def transform_data(books_data: pd.DataFrame, authors_dimension: pd.DataFrame) -> pd.DataFrame:
    """ A function that takes the books data and the authors dimension data as arguments, and transforms the books data by cleaning the title, author name, year, rating, and ratings. """
    logger.info(f"Starting data transformation on {len(books_data)} rows.")
    cleaned = transform_title_column(books_data, "title")

    cleaned = enrich_author_name(books_data, authors_dimension, "author_name")

    cleaned = transform_year_column(cleaned, "year")

    cleaned = transform_rating_column(cleaned, "rating")

    cleaned = transform_ratings_column(cleaned, "ratings")

    cleaned = cleaned[["title", "author_name", "year", "rating", "ratings"]].dropna()
    logger.info(f"Data transformation complete. {len(cleaned)} rows retained after dropping nulls.")

    return cleaned

def save_data_frame_to_csv(data_frame: pd.DataFrame, path_to_csv: str) -> None:
    """ A function that takes a data frame and a file path as arguments, and saves the data frame to a CSV file at the specified location.
    If a file already exists at that location, it will be overwritten.
    If the data frame is empty, a warning will be logged and no file will be saved."""
    if data_frame.empty:
        logger.warning("The data frame is empty. No file will be saved.")
        return
    data_frame.to_csv(path_to_csv, index=False)
    logger.info(f"Saved {len(data_frame)} rows to {path_to_csv}")

# -- Main function --

def process_data(input_file: str, db_path: str, table_name: str, output_file: str) -> None:
    """ A function that takes the input file path, database path, table name, and output file path as arguments, and processes the data by reading the raw data and dimensions data, transforming the data, and saving the processed data to a new CSV file."""
    logger.info(f"Starting process_data: input='{input_file}', db='{db_path}', table='{table_name}', output='{output_file}'")

    # Read the data into a pandas dataframe
    data_frame_to_transform = read_data_frame_from_csv(input_file)

    # Read the dimensions data from the database
    dimensions_data_frame = read_dimension_table_from_database(db_path, table_name)

    # Transform the data
    processed_data_frame = transform_data(data_frame_to_transform, dimensions_data_frame)

    # Sort by descending order of rating and then by descending order of ratings count
    processed_data_frame.sort_values(by=["rating", "ratings"], ascending=[False, False], inplace=True)
    logger.info("Sorted processed data by rating and ratings count (descending).")

    # Save the transformed data to a new CSV file
    save_data_frame_to_csv(processed_data_frame, output_file)
    logger.info("process_data completed successfully.")

if __name__ == "__main__":
    # Get the argument from the user 
    parser = generate_argument_parser()
    input_file = parser.parse_args().input_file
    print(f"Input file: {input_file}")

    process_data(input_file, "data/authors.db", "author", "PROCESSED_DATA.csv")
