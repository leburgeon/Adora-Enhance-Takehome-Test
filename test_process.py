from process_raw_data import (
    format_title,
    format_rating,
    find_title_column,
    find_year_column,
    find_rating_column,
    find_ratings_column,
    transform_title_column,
    transform_year_column,
    read_data_frame_from_csv,
)
import pandas as pd
import pytest


# -- format_title --

def test_format_title():
    """format_title removes bracketed information from a title."""
    assert format_title("The Great Gatsby (Paperback)") == "The Great Gatsby"

def test_format_title_with_trailing_whitespace():
    """format_title removes bracketed information and trailing whitespace."""
    assert format_title("The Great Gatsby (Paperback)   ") == "The Great Gatsby"

def test_format_title_square_brackets():
    """format_title removes square-bracket information."""
    assert format_title("Dune [Special Edition]") == "Dune"

def test_format_title_non_string_returns_na():
    """format_title returns pd.NA for non-string input."""
    assert pd.isna(format_title(42))
    assert pd.isna(format_title(None))


# -- format_rating --

def test_format_rating_comma_decimal():
    """format_rating converts a comma-separated decimal string to a float."""
    assert format_rating("4,25") == pytest.approx(4.25)

def test_format_rating_dot_decimal():
    """format_rating also handles values already using a dot decimal separator."""
    assert format_rating("4.25") == pytest.approx(4.25)

def test_format_rating_non_string_returns_na():
    """format_rating returns pd.NA for non-string input."""
    assert pd.isna(format_rating(4.5))
    assert pd.isna(format_rating(None))

def test_format_rating_invalid_string_returns_na():
    """format_rating returns pd.NA for strings that cannot be converted to float."""
    assert pd.isna(format_rating("not-a-number"))


# -- find_*_column --

def test_find_title_column_returns_correct_column():
    """find_title_column identifies a column whose name contains 'title'."""
    assert find_title_column(["Book_Title", "author_id", "year"]) == "Book_Title"

def test_find_title_column_raises_when_missing():
    """find_title_column raises RuntimeError when no title column exists."""
    with pytest.raises(RuntimeError):
        find_title_column(["author_id", "year", "rating"])

def test_find_year_column_returns_correct_column():
    """find_year_column identifies a column whose name contains 'year'."""
    assert find_year_column(["title", "publication_year", "rating"]) == "publication_year"

def test_find_year_column_raises_when_missing():
    """find_year_column raises RuntimeError when no year column exists."""
    with pytest.raises(RuntimeError):
        find_year_column(["title", "author", "rating"])

def test_find_rating_column_returns_correct_column():
    """find_rating_column identifies a column whose name contains 'rating'."""
    assert find_rating_column(["title", "avg_rating", "ratings"]) == "avg_rating"

def test_find_rating_column_raises_when_missing():
    """find_rating_column raises RuntimeError when no rating column exists."""
    with pytest.raises(RuntimeError):
        find_rating_column(["title", "author", "year"])

def test_find_ratings_column_returns_correct_column():
    """find_ratings_column identifies a column whose name contains 'ratings'."""
    assert find_ratings_column(["title", "ratings_count", "year"]) == "ratings_count"

def test_find_ratings_column_raises_when_missing():
    """find_ratings_column raises RuntimeError when no ratings count column exists."""
    with pytest.raises(RuntimeError):
        find_ratings_column(["title", "author", "year"])


# -- transform_title_column --

def test_transform_title_column_creates_new_column():
    """transform_title_column adds a cleaned title column to the data frame."""
    df = pd.DataFrame({"book_title": ["Dune (Paperback)", "1984 [Hardcover]"]})
    result = transform_title_column(df, "title")
    assert "title" in result.columns
    assert result["title"].tolist() == ["Dune", "1984"]


# -- transform_year_column --

def test_transform_year_column_coerces_non_numeric():
    """transform_year_column converts non-numeric year values to NaN."""
    df = pd.DataFrame({"publication_year": ["2001", "unknown", "1999"]})
    result = transform_year_column(df, "year")
    assert result["year"].iloc[0] == 2001.0
    assert pd.isna(result["year"].iloc[1])
    assert result["year"].iloc[2] == 1999.0


# -- read_data_frame_from_csv --

def test_read_data_frame_from_csv_raises_for_missing_file():
    """read_data_frame_from_csv raises RuntimeError when the file does not exist."""
    with pytest.raises(RuntimeError):
        read_data_frame_from_csv("nonexistent_file.csv")
