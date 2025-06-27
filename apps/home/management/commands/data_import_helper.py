"""
Helper functions for data import validation and normalization.
Used by the sample data management command to ensure imported data
(from CSV, Google Sheets, or Excel) is clean, normalized, and valid
before being loaded into the database.
"""
import pandas as pd, re, csv
from datetime import datetime

# Validate year is within reasonable range
def validate_year(year_value, row_num):
    """
    Validate that year is a reasonable value between 1900 and current year.
    Returns (is_valid, error_message)
    """
    try:
        if pd.isna(year_value) or year_value == '' or year_value is None:
            return True, None  # Allow empty years (will be handled by missing data logic)
        
        year = int(year_value)
        current_year = datetime.now().year
        
        if year < 1900 or year > current_year:
            return False, f"Row {row_num}: Year '{year}' is outside valid range (1900-{current_year})"
        
        return True, None
    except (ValueError, TypeError):
        return False, f"Row {row_num}: Year '{year_value}' is not a valid integer"

# Validate text fields contain only text values
def validate_text_field(value, field_name, row_num):
    """
    Validate that a field contains only text values.
    Returns (is_valid, error_message)
    """
    if pd.isna(value) or value == '' or value is None:
        return True, None  # Allow empty values (will be handled by missing data logic)
    
    # Check if value is numeric when it shouldn't be
    try:
        float_val = float(value)
        # If it's a number, it's invalid for text fields
        return False, f"Row {row_num}: Field '{field_name}' contains numeric value '{value}', expected text only"
    except (ValueError, TypeError):
        # Not a number, so it's valid text
        return True, None

# Comprehensive data validation function
def validate_data_integrity(csv_rows, missing_data_strategy='error'):
    """
    Comprehensive validation of data integrity including:
    - Year range validation (1900 to current year)
    - Text field validation (type, country, label should be text only)
    - Column structure validation
    
    Returns (is_valid, error_messages)
    """
    errors = []
    current_year = datetime.now().year
    
    for i, row in enumerate(csv_rows, start=2):
        # Validate year
        year_valid, year_error = validate_year(row.get('year'), i)
        if not year_valid:
            errors.append(year_error)
        
        # Validate text fields
        text_fields = ['type', 'country', 'label']
        for field in text_fields:
            field_valid, field_error = validate_text_field(row.get(field), field, i)
            if not field_valid:
                errors.append(field_error)
        
        # Additional validation: check for obvious column shift indicators
        # If genre contains a year-like number, it might indicate column shift
        genre_value = row.get('genre', '')
        if pd.notna(genre_value) and str(genre_value).isdigit():
            year_val = int(genre_value)
            if 1900 <= year_val <= current_year:
                errors.append(f"Row {i}: Genre field contains year-like value '{genre_value}', possible column shift detected")
        
        # If price contains non-numeric value, it might indicate column shift
        price_value = row.get('price', '')
        if pd.notna(price_value):
            try:
                int(price_value)
            except (ValueError, TypeError):
                errors.append(f"Row {i}: Price field contains non-numeric value '{price_value}', possible column shift detected")
    
    # If there are validation errors and strategy is 'error', abort
    if errors and missing_data_strategy == 'error':
        return False, errors
    
    # If strategy is 'skip' or 'fill', log errors but continue
    if errors:
        return True, errors
    
    return True, []

# Handle missing data according to the specified strategy.
def handle_missing_data(csv_rows, strategy='error', stdout=None):
    """
    Handle rows with missing data according to the specified strategy.
    - 'error': Raise an exception on the first missing required field.
    - 'skip': Skip rows with missing required fields, optionally logging them.
    - 'fill': Fill missing fields with sensible defaults.
    """
    required_fields = ['title', 'artist', 'genre', 'year', 'price', 'type', 'country', 'label']
    defaults = {
        'title': 'Unknown Title',
        'artist': 'Unknown Artist',
        'genre': 'Unknown Genre',
        'year': datetime.now().year,
        'price': 0,
        'type': 'Unknown',
        'country': 'Unknown',
        'label': 'Unknown'
    }
    filtered = []
    for i, row in enumerate(csv_rows, start=2):
        missing = []
        for field in required_fields:
            value = row.get(field)
            if value is None or pd.isna(value) or str(value).strip() == '':
                missing.append(field)
        if not missing:
            filtered.append(row)
        else:
            if strategy == 'error':
                raise Exception(f"Row {i}: Missing required field(s) {missing}. Row: {row}")
            elif strategy == 'skip':
                if stdout:
                    stdout.write(f"Skipping row {i} due to missing fields {missing}: {row}")
                continue
            elif strategy == 'fill':
                for field in missing:
                    row[field] = defaults[field]
                if stdout:
                    stdout.write(f"Filling missing fields {missing} in row {i} with defaults.")
                filtered.append(row)
    return filtered

# Check for existing vinyl records in database
def check_existing_vinyl_records(vinyl_records_data, stdout=None):
    """
    Check which vinyl records already exist in the database.
    Returns information about existing records for user feedback.
    """
    from apps.vinyl.models import VinylRecord, Artist
    
    existing_records = []
    new_records = []
    
    for record_data in vinyl_records_data:
        try:
            # Check if artist exists
            artist = Artist.objects.get(name=record_data['artist'])
            # Check if vinyl record with same title and artist exists
            existing_vinyl = VinylRecord.objects.filter(
                title=record_data['title'],
                artist=artist
            ).first()
            
            if existing_vinyl:
                existing_records.append({
                    'title': record_data['title'],
                    'artist': record_data['artist'],
                    'existing_id': existing_vinyl.id
                })
            else:
                new_records.append({
                    'title': record_data['title'],
                    'artist': record_data['artist']
                })
        except Artist.DoesNotExist:
            # Artist doesn't exist, so record is new
            new_records.append({
                'title': record_data['title'],
                'artist': record_data['artist']
            })
    
    return existing_records, new_records

def data_normalization(csv_rows):
    """
    Normalize delimiters and strip whitespace in artist, genre, and label fields for all rows.
    Returns a new list of normalized rows.
    """
    normalized_rows = []
    for row in csv_rows:
        normalized_row = row.copy()
        fields_to_normalize = ['artist', 'genre', 'label']
        for field in fields_to_normalize:
            if field in normalized_row and pd.notna(normalized_row[field]):
                value = str(normalized_row[field]).strip()
                if not value:
                    continue
                value = re.sub(r'\s*(,|\||\band\b)\s*', ' & ', value, flags=re.IGNORECASE)
                value = re.sub(r'\s*&\s*', ' & ', value)
                value = re.sub(r'\s+', ' ', value)
                value = value.strip()
                normalized_row[field] = value
        # Also strip whitespace from all string fields
        for key in normalized_row:
            if isinstance(normalized_row[key], str):
                normalized_row[key] = normalized_row[key].strip()
        normalized_rows.append(normalized_row)
    return normalized_rows

# Validate that normalized data meets formatting requirements.
def validate_normalized_data(csv_rows):
    """
    Ensure only '&' is used as a delimiter and spacing is correct.
    Raises Exception if unnormalized delimiters or bad spacing found.
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

def validate_full_data(csv_rows):
    """
    Run all validation and normalization steps on imported data:
    - Structure validation
    - Data type validation
    - Data normalization
    - Delimiter validation
    Returns normalized rows if all checks pass.
    """
    validate_csv_structure(csv_rows)
    validate_data_types(csv_rows)
    normalized_rows = data_normalization(csv_rows)
    validate_normalized_data(normalized_rows)
    return normalized_rows

# Ensure CSV has required columns and correct row length.
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

# Ensure all required fields are strings, not NaN/float.
def validate_data_types(csv_rows):
    """
    Check that all required fields are strings and not NaN/float.
    """
    for i, row in enumerate(csv_rows, start=2):
        for field in ['title', 'artist', 'genre', 'type', 'country', 'label']:
            if pd.isna(row.get(field)) or not isinstance(row.get(field), str):
                raise Exception(f"Row {i}: Field '{field}' contains invalid data: {row.get(field)}. "
                    f"Expected string, got {type(row.get(field)).__name__}. "
                    f"This indicates commas appeared in data fields but unquoted. Please review the CSV file.")

# Extract unique genres from rows.
def extract_genres_data(csv_rows):
    """Return a sorted list of unique genres."""
    return sorted({str(row['genre']).strip() for row in csv_rows if row.get('genre') and pd.notna(row.get('genre'))})

# Extract unique labels from rows.
def extract_labels_data(csv_rows):
    """Return a sorted list of unique labels."""
    return sorted({str(row['label']).strip() for row in csv_rows if row.get('label') and pd.notna(row.get('label'))})

# Extract artist info as list of dicts.
def extract_artists_data(csv_rows):
    """Return a list of unique artist dicts (name, type, country)."""
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

# Extract vinyl record info as list of dicts.
def extract_vinyl_records_data(csv_rows):
    """Return a list of vinyl record dicts (title, artist, genre, year, price)."""
    records = []
    for i, row in enumerate(csv_rows, start=1):
        title = str(row['title']).strip() if pd.notna(row.get('title')) else ''
        artist = str(row['artist']).strip() if pd.notna(row.get('artist')) else ''
        genre = str(row['genre']).strip() if pd.notna(row.get('genre')) else ''
        
        # Handle year and price with better validation
        try:
            year_value = row.get('year')
            if pd.isna(year_value) or year_value == '' or year_value is None:
                year = 0
            else:
                year = int(year_value)
        except (ValueError, TypeError):
            year = 0
            
        try:
            price_value = row.get('price')
            if pd.isna(price_value) or price_value == '' or price_value is None:
                price = 0
            else:
                price = int(price_value)
        except (ValueError, TypeError):
            price = 0
        
        # Check if we have the minimum required data
        if title and artist and genre:
            # Allow year and price to be 0 (filled defaults)
            records.append({
                'title': title,
                'artist': artist,
                'genre': genre,
                'year': year,
                'price': price,
            })
    
    return records

def precheck_csv_column_count(csv_path, expected_columns=8):
    """
    Read the CSV as raw rows and abort if any row does not have the expected number of columns.
    """
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader, None)
        if header is None:
            raise Exception("CSV file is empty or missing header row.")
        for i, row in enumerate(reader, start=2):
            if len(row) != expected_columns:
                raise Exception(
                    f"Row {i} has {len(row)} fields, expected {expected_columns}. "
                    f"Check for unquoted commas or formatting errors in: {row}\n"
                    f"Import aborted due to column count mismatch."
                )
    return True 