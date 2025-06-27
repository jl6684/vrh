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
    """Read CSV using pandas with better error handling."""
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
        return df.to_dict(orient='records')
    except pd.errors.ParserError as e:
        # Try with different parsing options
        try:
            df = pd.read_csv(csv_path, encoding='utf-8', quoting=csv.QUOTE_ALL)
            return df.to_dict(orient='records')
        except pd.errors.ParserError:
            # If still failing, provide detailed error information
            raise Exception(f"CSV parsing error in {csv_path}. Please check:\n"
                f"1. All fields with commas are properly quoted\n"
                f"2. Each row has exactly 8 columns\n"
                f"3. No extra commas in data fields\n"
                f"Original error: {str(e)}")
    except FileNotFoundError:
        raise Exception(f"CSV file not found: {csv_path}")
    except Exception as e:
        raise Exception(f"Error reading CSV file: {str(e)}")

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