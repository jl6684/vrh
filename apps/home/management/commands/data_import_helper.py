import pandas as pd
import re

def normalize_field_delimiters(csv_rows):
    """
    Normalize delimiters in artist, genre, and label fields:
    - Replace ",", "|", "and" with "&"
    - Keep existing "&" unchanged
    - Ensure single space before and after "&"
    """
    normalized_rows = []
    for i, row in enumerate(csv_rows):
        normalized_row = row.copy()
        fields_to_normalize = ['artist', 'genre', 'label']
        for field in fields_to_normalize:
            if field in normalized_row and pd.notna(normalized_row[field]):
                value = str(normalized_row[field]).strip()
                if not value:
                    continue
                value = re.sub(r'\s*(,|\||\\band\\b)\s*', ' & ', value, flags=re.IGNORECASE)
                value = re.sub(r'\s*&\s*', ' & ', value)
                value = re.sub(r'\s+', ' ', value)
                value = value.strip()
                normalized_row[field] = value
        normalized_rows.append(normalized_row)
    return normalized_rows

def validate_normalized_data(csv_rows):
    """
    Validate that normalized data meets the formatting requirements.
    """
    for i, row in enumerate(csv_rows, start=2):
        for field in ['artist', 'genre', 'label']:
            if field in row and pd.notna(row[field]):
                value = str(row[field]).strip()
                if '&' in value:
                    if not re.match(r'^[^&]+( & [^&]+)+$', value):
                        raise Exception(
                            f"Row {i}: Field '{field}' has improper spacing around '&': '{value}'. "
                            f"Expected format: 'Artist1 & Artist2 [ & Artist3 ...]'"
                        )
                if ',' in value or '|' in value or re.search(r'\band\b', value, re.IGNORECASE):
                    raise Exception(
                        f"Row {i}: Field '{field}' still contains unnormalized delimiters: '{value}'. "
                        f"Expected only '&' as delimiter."
                    )

def validate_and_normalize_data(csv_rows):
    """
    Comprehensive data validation and normalization:
    1. Validate structure and data types
    2. Normalize delimiters in artist, genre, and label fields
    3. Validate normalized data
    """
    validate_csv_structure(csv_rows)
    validate_data_types(csv_rows)
    normalized_rows = normalize_field_delimiters(csv_rows)
    validate_normalized_data(normalized_rows)
    return normalized_rows

def validate_csv_structure(csv_rows):
    """Validate that CSV has the expected structure and provide helpful error messages."""
    expected_columns = ['title', 'artist', 'genre', 'year', 'price', 'type', 'country', 'label']
    if not csv_rows:
        raise Exception("CSV file is empty or could not be parsed")
    first_row = csv_rows[0]
    missing_columns = [col for col in expected_columns if col not in first_row]
    if missing_columns:
        raise Exception(f"Missing required columns: {missing_columns}")
    for i, row in enumerate(csv_rows, start=2):
        if len(row) != len(expected_columns):
            raise Exception(f"Row {i} has {len(row)} fields, expected {len(expected_columns)}. "
                f"Check for unquoted commas in: {row}")
    return True

def validate_data_types(csv_rows):
    """Validate that all required fields contain string data, not NaN/float."""
    for i, row in enumerate(csv_rows, start=2):
        for field in ['title', 'artist', 'genre', 'type', 'country', 'label']:
            if pd.isna(row.get(field)) or not isinstance(row.get(field), str):
                raise Exception(f"Row {i}: Field '{field}' contains invalid data: {row.get(field)}. "
                    f"Expected string, got {type(row.get(field)).__name__}. "
                    f"This indicates commas appeared in data fields but unquoted. Please review the CSV file.")

def extract_genres_data(csv_rows):
    """Extract unique genres from CSV rows."""
    return list({str(row['genre']).strip() for row in csv_rows if row.get('genre') and pd.notna(row.get('genre'))})

def extract_labels_data(csv_rows):
    """Extract unique labels from CSV rows."""
    return list({str(row['label']).strip() for row in csv_rows if row.get('label') and pd.notna(row.get('label'))})

def extract_artists_data(csv_rows):
    """Extract artist info as list of dicts from CSV rows."""
    seen = set()
    artists = []
    for row in csv_rows:
        artist_name = str(row['artist']).strip() if pd.notna(row.get('artist')) else ''
        artist_type = str(row['type']).strip() if pd.notna(row.get('type')) else ''
        artist_country = str(row['country']).strip() if pd.notna(row.get('country')) else ''
        if artist_name and artist_type and artist_country:
            key = (artist_name, artist_type, artist_country)
            if key not in seen:
                artists.append({
                    'name': artist_name,
                    'type': artist_type,
                    'country': artist_country,
                })
                seen.add(key)
    return artists

def extract_vinyl_records_data(csv_rows):
    """Extract vinyl record info as list of dicts from CSV rows."""
    records = []
    for row in csv_rows:
        title = str(row['title']).strip() if pd.notna(row.get('title')) else ''
        artist = str(row['artist']).strip() if pd.notna(row.get('artist')) else ''
        genre = str(row['genre']).strip() if pd.notna(row.get('genre')) else ''
        try:
            year = int(row['year']) if pd.notna(row.get('year')) else 0
            price = int(row['price']) if pd.notna(row.get('price')) else 0
        except (ValueError, TypeError):
            continue
        if title and artist and genre and year > 0 and price > 0:
            records.append({
                'title': title,
                'artist': artist,
                'genre': genre,
                'year': year,
                'price': price,
            })
    return records 