"""
Data import methods for sample data management command.
Supports CSV, Google Sheets, and Excel file imports with error handling.
"""
import os, json, csv, pandas as pd, gspread
from oauth2client.service_account import ServiceAccountCredentials

# ============================================================================
# METHOD 1: CSV FILE IMPORT FUNCTIONS
# ============================================================================

def read_csv_data(csv_path):
    """Read CSV using pandas with better error handling and column shift detection."""
    try:
        # First attempt: standard reading
        df = pd.read_csv(csv_path, encoding='utf-8')
        return df.to_dict(orient='records')
    except pd.errors.ParserError as e:
        # Try with different parsing options
        try:
            df = pd.read_csv(csv_path, encoding='utf-8', quoting=csv.QUOTE_ALL)
            return df.to_dict(orient='records')
        except pd.errors.ParserError:
            # If still failing, try to detect the issue and provide specific guidance
            try:
                # Read raw file to analyze the problem
                with open(csv_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                if len(lines) < 2:
                    raise Exception(f"CSV file {csv_path} appears to be empty or has insufficient data")
                
                # Check first few lines for obvious issues
                header_line = lines[0].strip()
                expected_columns = ['title', 'artist', 'genre', 'year', 'price', 'type', 'country', 'label']
                header_columns = [col.strip() for col in header_line.split(',')]
                
                if len(header_columns) != len(expected_columns):
                    raise Exception(f"CSV header has {len(header_columns)} columns, expected {len(expected_columns)}. "
                        f"Header: {header_line}")
                
                # Check for unquoted commas in data
                problematic_lines = []
                for i, line in enumerate(lines[1:], start=2):
                    if line.count(',') > len(expected_columns) - 1:
                        problematic_lines.append(f"Line {i}: {line.strip()}")
                
                if problematic_lines:
                    error_msg = f"CSV parsing error in {csv_path}. The following lines contain unquoted commas:\n"
                    for line in problematic_lines[:5]:  # Show first 5 problematic lines
                        error_msg += f"  {line}\n"
                    if len(problematic_lines) > 5:
                        error_msg += f"  ... and {len(problematic_lines) - 5} more lines\n"
                    error_msg += "\nTo fix this issue:\n"
                    error_msg += "1. Quote fields that contain commas: \"Artist Name, Band Name\"\n"
                    error_msg += "2. Or escape commas with backslashes: Artist Name\\, Band Name\n"
                    error_msg += "3. Or use a different delimiter in your CSV file\n"
                    raise Exception(error_msg)
                
                # If we get here, it's a different parsing issue
                raise Exception(f"CSV parsing error in {csv_path}. Please check:\n"
                    f"1. All fields with commas are properly quoted\n"
                    f"2. Each row has exactly {len(expected_columns)} columns\n"
                    f"3. No extra commas in data fields\n"
                    f"Original error: {str(e)}")
                    
            except Exception as analysis_error:
                # If analysis fails, return the original error
                raise Exception(f"CSV parsing error in {csv_path}. Please check:\n"
                    f"1. All fields with commas are properly quoted\n"
                    f"2. Each row has exactly 8 columns\n"
                    f"3. No extra commas in data fields\n"
                    f"Original error: {str(e)}")
    except FileNotFoundError:
        raise Exception(f"CSV file not found: {csv_path}")
    except Exception as e:
        raise Exception(f"Error reading CSV file: {str(e)}")

def read_csv_data_with_skip(csv_path, missing_data_strategy='error', expected_columns=8, stdout=None):
    """
    Read CSV and skip rows with column count mismatch if missing_data_strategy is 'skip'.
    For other strategies, abort on first mismatch.
    Returns a list of dicts (like pandas read_csv).
    """
    valid_rows = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader, None)
        if header is None:
            raise Exception("CSV file is empty or missing header row.")
        for i, row in enumerate(reader, start=2):
            if len(row) != expected_columns:
                msg = (
                    f"Row {i} has {len(row)} fields, expected {expected_columns}. "
                    f"Check for unquoted commas or formatting errors in: {row}"
                )
                if missing_data_strategy == 'skip':
                    if stdout:
                        stdout.write(f"Skipping row {i} due to column count mismatch: {row}")
                    continue
                else:
                    raise Exception(msg + "\nImport aborted due to column count mismatch.")
            valid_rows.append(row)
    # Convert valid_rows to list of dicts
    result = []
    for row in valid_rows:
        result.append(dict(zip(header, row)))
    return result

# ============================================================================
# METHOD 2: GOOGLE SHEETS IMPORT FUNCTIONS
# ============================================================================

DEFAULT_SHEET_ID = "1VmJAB5tM0mok7j5ma15qw8Ozshlp-kBnPKG5oa-D1rM"
VALID_WORKSHEETS = ["Sheet1", "Sheet2", "dupSheet2"]

def read_gsheet_data(sheet_id, worksheet_name='Sheet1'):
    """Read Google Sheet data with error handling."""
    cred_json = os.getenv('GOOGLE_CREDEN')
    if not cred_json:
        raise Exception("Environment variable 'GOOGLE_CREDEN' is not set.")
    try:
        cred_dict = json.loads(cred_json)
    except json.JSONDecodeError:
        raise Exception("GOOGLE_CREDEN does not contain valid JSON.")

    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(cred_dict, scope)
    try:
        client = gspread.authorize(creds)
        sheet = client.open_by_key(sheet_id)
        worksheet = sheet.worksheet(worksheet_name)
        rows = worksheet.get_all_records()
        return rows
    except FileNotFoundError:
        raise Exception("Google Credentials information file not found. Please ensure Google Sheets credentials are properly configured.")
    except gspread.SpreadsheetNotFound:
        raise Exception(f"Google Sheet with ID '{sheet_id}' not found or not accessible.")
    except gspread.WorksheetNotFound:
        available = [ws.title for ws in sheet.worksheets()]
        raise Exception(f"Worksheet '{worksheet_name}' not found in the Google Sheet. Available worksheets: {available}")
    except Exception as e:
        raise Exception(f"Error accessing Google Sheet: {str(e)}")

# ============================================================================
# METHOD 3: EXCEL FILE IMPORT FUNCTIONS
# ============================================================================

def read_excel_data(excel_path):
    """Read Excel file with error handling."""
    try:
        df = pd.read_excel(excel_path)
        return df.to_dict(orient='records')
    except FileNotFoundError:
        raise Exception(f"Excel file not found: {excel_path}")
    except Exception as e:
        raise Exception(f"Error reading Excel file: {str(e)}") 