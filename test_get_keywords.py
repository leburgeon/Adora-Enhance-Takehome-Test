"""Tests for get_keywords.py"""
from collections import Counter

import pytest

from get_keywords import (
    tokenize,
    remove_stopwords,
    count_keywords,
    top_n_keywords,
    read_titles,
    DEFAULT_STOPWORDS,
)


# ---------------------------------------------------------------------------
# tokenize
# ---------------------------------------------------------------------------

def test_tokenize_returns_lowercase_words():
    assert tokenize("The Great Gatsby") == ["the", "great", "gatsby"]

def test_tokenize_strips_punctuation():
    assert tokenize("Never Never: Part Two") == ["never", "never", "part", "two"]

def test_tokenize_non_string_returns_empty_list():
    assert tokenize(None) == []
    assert tokenize(42) == []


# ---------------------------------------------------------------------------
# remove_stopwords
# ---------------------------------------------------------------------------

def test_remove_stopwords_filters_stopwords():
    tokens = ["the", "love", "of", "steel"]
    result = remove_stopwords(tokens, DEFAULT_STOPWORDS)
    assert result == ["love", "steel"]

def test_remove_stopwords_filters_short_tokens():
    tokens = ["ok", "hi", "love"]
    result = remove_stopwords(tokens, DEFAULT_STOPWORDS)
    assert result == ["love"]

def test_remove_stopwords_with_empty_input_returns_empty():
    assert remove_stopwords([], DEFAULT_STOPWORDS) == []


# ---------------------------------------------------------------------------
# count_keywords
# ---------------------------------------------------------------------------

def test_count_keywords_counts_correctly():
    titles = ["Love in Paris", "Paris is Beautiful", "The Love Story"]
    counter = count_keywords(titles, DEFAULT_STOPWORDS)
    assert counter["love"] == 2
    assert counter["paris"] == 2
    assert counter["beautiful"] == 1
    assert "the" not in counter
    assert "is" not in counter

def test_count_keywords_returns_counter_type():
    assert isinstance(count_keywords(["Hello World"], DEFAULT_STOPWORDS), Counter)


# ---------------------------------------------------------------------------
# top_n_keywords
# ---------------------------------------------------------------------------

def test_top_n_keywords_limits_results():
    counter = Counter({"love": 10, "dark": 8, "night": 6, "kiss": 4})
    df = top_n_keywords(counter, n=2)
    assert len(df) == 2

def test_top_n_keywords_returns_sorted_by_count_descending():
    counter = Counter({"love": 10, "dark": 8, "night": 6})
    df = top_n_keywords(counter, n=3)
    assert df.iloc[0]["keyword"] == "love"
    assert df.iloc[0]["count"] == 10

def test_top_n_keywords_has_correct_columns():
    df = top_n_keywords(Counter({"love": 5}), n=1)
    assert list(df.columns) == ["keyword", "count"]


# ---------------------------------------------------------------------------
# read_titles
# ---------------------------------------------------------------------------

def test_read_titles_raises_for_missing_file():
    with pytest.raises(RuntimeError):
        read_titles("nonexistent.csv")
