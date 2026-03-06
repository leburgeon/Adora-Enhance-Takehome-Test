# Book Data Pipeline

A three-script pipeline for processing, analysing, and extracting keywords from book data.

## What it does

| Script | Input | Output | Description |
|---|---|---|---|
| `process_raw_data.py` | Raw CSV + `data/authors.db` | `PROCESSED_DATA.csv` | Cleans titles, enriches author names, coerces numeric fields, and removes invalid rows. |
| `analyse_processed_data.py` | `PROCESSED_DATA.csv` | `decade_releases.png`, `top_authors.png` | Produces a pie chart of books per decade and a bar chart of the 10 most-rated authors. |
| `get_keywords.py` | `PROCESSED_DATA.csv` | `top_keywords.png` | Counts and charts the 20 most common meaningful words across all book titles. |

All scripts append structured log entries to `data_analysis.log`.

## Setup

```bash
pip install -r requirements.txt
```

## Running

```bash
# 1. Process a raw data file
python process_raw_data.py <path_to_data>.csv

# 2. Analyse the processed data
python analyse_processed_data.py <path_to_data>.csv

# 3. Extract top keywords from titles
python get_keywords.py <path_to_data>.csv
```

## Tests

```bash
pytest
```
