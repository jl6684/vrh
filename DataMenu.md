# Data Handling Menu

## Overview
This document provides instructions for importing, deleting, and exporting vinyl record data in the Django application using management commands. Data can be imported from CSV, Google Sheets, or Excel files stored in the `data-for-import` folder, deleted using the `delete_vinyl_data` command, and exported to Excel format using the `export_vrh_data` command.

## Prerequisites
- Django project is set up and running
- Data files are placed in the `data-for-import` folder
- Data files must have the following column structure:
  - `title` - Album/record title
  - `artist` - Artist or band name
  - `genre` - Music genre
  - `year` - Release year (integer)
  - `price` - Price (integer)
  - `type` - Artist type (male, female, band, Classical, Assortment, etc.)
  - `country` - Artist's country of origin
  - `label` - Record label (can be left blank)

## Python Package Prerequisites

The following Python packages must be installed in your virtual environment to support the three data import methods:

### Required Packages

1. **gspread** - Google Sheets API wrapper
   - **Purpose**: Enables reading data from Google Sheets
   - **Install**: `pip install gspread`
   - **Usage**: Used for METHOD 2 (Google Sheets import)

2. **oauth2client** - Google OAuth 2.0 authentication
   - **Purpose**: Handles authentication for Google Sheets API
   - **Install**: `pip install oauth2client`
   - **Usage**: Required for Google Sheets authentication

3. **openpyxl** - Excel file processing
   - **Purpose**: Reads and processes Excel (.xlsx) files
   - **Install**: `pip install openpyxl`
   - **Usage**: Used for METHOD 3 (Excel file import)

4. **pandas** - Data manipulation and analysis
   - **Purpose**: Handles data processing and Excel export operations
   - **Install**: `pip install pandas`
   - **Usage**: Used for data export functionality

### Installation Command
```bash
pip install gspread oauth2client openpyxl pandas
```

**Note**: These packages are automatically imported by the data import and export systems. If any package is missing, the operation will fail with a clear error message indicating which package needs to be installed.

## Available Data Files
The following files are available in the `data-for-import` folder:

### Main Data Files
- `vinyldata.csv` (default) - 21 records
- `vinyldata1.csv` - 26 records  
- `vinyldata-ex.xlsx` - 21 records
- `vinyldata-ex1.xlsx` - 24 records
- `vinyldata-dup.xlsx` - 14 records (duplicate data for testing)

### Test/Error Files
- `vinyldata1-dup.csv` - 8 records (duplicate data for testing)
- `vinyldata1-error.csv` - 6 records (contains formatting errors for testing)

### Trial Data Subfolder
- `trial-fake-data/test-missing-fields.csv` - 7 records (test data with missing fields)

**Note**: Files with "error" or "dup" in their names are intended for testing error handling and duplicate detection features. Files in the `trial-fake-data` subfolder are for testing specific scenarios like missing data handling.

## Data Import Commands

### Import Data Using `import_vinyl_data`

#### 1. Import Data Using Default CSV File
```sh
python manage.py import_vinyl_data
```

#### 2. Import Data Using a Specific CSV File
```sh
# Short form
python manage.py import_vinyl_data -cs vinyldata1.csv

# Long form
python manage.py import_vinyl_data --csv-file vinyldata1.csv
```

#### 3. Import Data from Google Sheets
```sh
# Short form
python manage.py import_vinyl_data -gs Sheet1

# Long form
python manage.py import_vinyl_data --gs-file Sheet1
```
- You can now use any worksheet name from your Google Sheet. If the worksheet does not exist, the error message will list all available worksheet names in the sheet for your reference. 
**Note**: The Google Sheets feature requires proper Google API credentials set in the `GOOGLE_CREDEN` environment variable. If credentials are missing or invalid, the import will fail with a clear error message.


#### 4. Import Data from Excel File
```sh
# Short form
python manage.py import_vinyl_data -ex vinyldata-ex.xlsx

# Long form
python manage.py import_vinyl_data --ex-file vinyldata-ex.xlsx
```

#### 5. Handle Missing Data (New Feature)
You can now control how missing data is handled using the `-md` or `--missing-data` argument:

- `-md error` or `--missing-data error` (default): Abort import and show an error if any required field is missing in a row.
- `-md skip` or `--missing-data skip`: Skip rows with missing required fields and continue importing the rest. Skipped rows will be reported in the output.
- `-md fill` or `--missing-data fill`: Fill missing required fields with sensible defaults and import all rows. Filled fields will be reported in the output.

**Default fill values for missing data:**
- `title`: 'Unknown Title'
- `artist`: 'Unknown Artist'
- `genre`: 'Unknown Genre'
- `year`: current year (e.g., 2024)
- `price`: 0
- `type`: 'Unknown'
- `country`: 'Unknown'
- `label`: 'Unknown'

If the `year` field is missing, the current year will be used (since the database requires an integer). If the `label` field is missing, the value 'Unknown' will be used and a label with that name will be created if it does not exist.

**Data Normalization Features:**
The import process automatically normalizes delimiters in artist, genre, and label fields:
- **Commas** (`,`), **pipes** (`|`), and **"and"** are converted to **"&"** with proper spacing
- **Example**: `"Artist1, Artist2"` → `"Artist1 & Artist2"`
- **Example**: `"Artist1 | Artist2"` → `"Artist1 & Artist2"`
- **Example**: `"Artist1 and Artist2"` → `"Artist1 & Artist2"`
- All fields are automatically stripped of leading/trailing whitespace

#### Examples:
Import and skip rows with missing data:
```sh
# Short form
python manage.py import_vinyl_data -cs vinyldata1.csv -md skip

# Long form
python manage.py import_vinyl_data --csv-file vinyldata1.csv --missing-data skip
```

Import and fill missing data with defaults:
```sh
# Short form
python manage.py import_vinyl_data -cs vinyldata1.csv -md fill

# Long form
python manage.py import_vinyl_data --csv-file vinyldata1.csv --missing-data fill
```

Import from subfolder:
```sh
# Import from trial-fake-data subfolder
python manage.py import_vinyl_data -cs trial-fake-data/test-missing-fields.csv -md fill
```

Get help:
```sh
python manage.py import_vinyl_data --help
```

#### Import Arguments Summary

| Short Form | Long Form | Description | Default |
|------------|-----------|-------------|---------|
| `-cs` | `--csv-file` | CSV file name in data-for-import folder | `vinyldata.csv` |
| `-gs` | `--gs-file` | Google Sheet worksheet name | `None` |
| `-ex` | `--ex-file` | Excel file name in data-for-import folder | `None` |
| `-md` | `--missing-data` | Missing data handling strategy | `error` |

#### Import Method Priority
The command processes arguments in this order:
1. **Excel** (`-ex` or `--ex-file`) - highest priority
2. **Google Sheets** (`-gs` or `--gs-file`) - medium priority  
3. **CSV** (`-cs` or `--csv-file`) - default/fallback

## Data Deletion Commands

### Delete Data Using `delete_vinyl_data`

#### Overview
The `delete_vinyl_data` command allows you to delete vinyl-related data from the database with granular control over which tables are affected.

#### Default Behavior
- **Default action**: Delete all records from `vinyl_vinylrecord` table only
- **Confirmation**: Always prompts for confirmation unless `--force-delete` is used
- **Safety**: Shows what will be deleted before proceeding

#### 1. Delete Only Vinyl Records (Default)
```sh
python manage.py delete_vinyl_data
```
This will delete only vinyl records and prompt for confirmation.

#### 2. Delete Specific Tables
```sh
# Delete vinyl records + artists
python manage.py delete_vinyl_data -artist

# Delete vinyl records + genres
python manage.py delete_vinyl_data -genre

# Delete vinyl records + labels
python manage.py delete_vinyl_data -label

# Delete vinyl records + multiple tables
python manage.py delete_vinyl_data -artist -genre

# Delete all 4 tables (vinyl records, artists, genres, labels)
python manage.py delete_vinyl_data -all
```

#### 3. Test Mode (No Actual Deletion)
```sh
# Test what would be deleted without actually deleting
python manage.py delete_vinyl_data --test-only

# Test with specific tables
python manage.py delete_vinyl_data -artist --test-only
python manage.py delete_vinyl_data -all --test-only
```

#### 4. Force Delete (No Confirmation)
```sh
# Delete without confirmation prompt
python manage.py delete_vinyl_data --force-delete

# Force delete specific tables
python manage.py delete_vinyl_data -artist --force-delete
python manage.py delete_vinyl_data -all --force-delete
```

#### 5. Combined Options
```sh
# Test what would be deleted for all tables
python manage.py delete_vinyl_data -all --test-only

# Force delete all tables without confirmation
python manage.py delete_vinyl_data -all --force-delete
```

Get help:
```sh
python manage.py delete_vinyl_data --help
```

#### Delete Arguments Summary

| Argument | Description | Default |
|----------|-------------|---------|
| `-all` | Delete all data in all 4 tables | `False` |
| `-artist` | Delete all data in vinyl_artist table | `False` |
| `-genre` | Delete all data in vinyl_genre table | `False` |
| `-label` | Delete all data in vinyl_label table | `False` |
| `--test-only` | Show what would be deleted without actually deleting | `False` |
| `--force-delete` | Delete without prompting for confirmation | `False` |

#### Delete Command Behavior

**Default Behavior (without --test-only and --force-delete):**
1. Shows what will be deleted (record counts for each table)
2. Prompts for confirmation: `Are you sure you want to continue? (yes/no):`
3. Waits for user input (requires `yes` or `y` to proceed)
4. Executes deletion if confirmed

**Safety Features:**
- Always shows what will be deleted before proceeding
- Requires explicit confirmation unless `--force-delete` is used
- `--test-only` allows safe testing without any data loss
- Foreign key constraints are respected (vinyl records deleted first)

## Data Export Commands

### Export Data Using `export_vrh_data`

#### Overview
The `export_vrh_data` command exports all VRH database data to an Excel file with multiple worksheets, combining related data from different tables into comprehensive datasets.

#### Features
- **5 Worksheets**: vinyl, orders, cart, reviews, wishlist
- **Combined Data**: Each worksheet contains related data from multiple tables
- **Timezone Handling**: Automatically converts timezone-aware datetimes to naive format for Excel compatibility
- **Custom Filenames**: Specify custom output filenames
- **Automatic Directory Creation**: Creates `data-export` directory if it doesn't exist
- **Overwrite Protection**: Warns when overwriting existing files

#### 1. Export Data Using Default Filename
```sh
python manage.py export_vrh_data
```
This exports data to `data-export/vrh_export.xlsx`

#### 2. Export Data Using Custom Filename
```sh
python manage.py export_vrh_data custom_name.xlsx
```
This exports data to `data-export/custom_name.xlsx`

#### 3. Get Help
```sh
python manage.py export_vrh_data --help
```

#### Export Arguments Summary

| Argument | Description | Default |
|----------|-------------|---------|
| `filename` | Output Excel filename | `vrh_export.xlsx` |

#### Export Worksheet Structure

**1. vinyl Worksheet**
- Combines data from: `vinyl_vinylrecord`, `vinyl_artist`, `vinyl_genre`, `vinyl_label`
- One row per vinyl record with all related artist, genre, and label information
- Fields include: vinyl details, artist information, genre details, label information

**2. orders Worksheet**
- Combines data from: `auth_user`, `orders_order`, `orders_orderitem`
- One row per order item with repeated order and user data
- Fields include: user details, order information, order item details

**3. cart Worksheet**
- Combines data from: `auth_user`, `cart_cart`, `cart_cartitem`
- One row per cart item with repeated cart and user data
- Handles anonymous carts (user data may be None)
- Fields include: user details, cart information, cart item details

**4. reviews Worksheet**
- Combines data from: `auth_user`, `reviews_review`
- One row per review with user data
- Fields include: user details, review information

**5. wishlist Worksheet**
- Combines data from: `auth_user`, `wishlist_wishlist`, `wishlist_wishlistitem`
- One row per wishlist item with repeated wishlist and user data
- Fields include: user details, wishlist information, wishlist item details

#### Export Process
When you run the `export_vrh_data` command, it will:

1. **Setup**:
   - Create `data-export` directory if it doesn't exist
   - Check for existing files and warn about overwriting
   - Initialize Excel writer with openpyxl engine

2. **Data Processing**:
   - Query each data type with optimized database queries
   - Combine related data from multiple tables
   - Convert timezone-aware datetimes to naive format
   - Handle null values and missing relationships

3. **Export**:
   - Create pandas DataFrames for each data type
   - Export to separate worksheets in the Excel file
   - Display progress messages for each worksheet

4. **Completion**:
   - Show success message with file path
   - Display record counts for each worksheet

#### Example Export Output
```
Creating new file: /path/to/data-export/vrh_export.xlsx
Starting VRH data export to /path/to/data-export/vrh_export.xlsx...
Exporting vinyl records data...
  - Exported 68 vinyl records
Exporting orders data...
  - Exported 45 order records
Exporting cart data...
  - Exported 23 cart records
Exporting reviews data...
  - Exported 12 review records
Exporting wishlist data...
  - Exported 8 wishlist records
Successfully exported VRH data to /path/to/data-export/vrh_export.xlsx
```

#### Export Command Behavior

**Default Behavior:**
1. Creates `data-export` directory if it doesn't exist
2. Warns if output file already exists
3. Exports all data types to separate worksheets
4. Shows progress for each worksheet
5. Displays final success message

**Features:**
- **Efficient Queries**: Uses `select_related` and `prefetch_related` for optimal database performance
- **Data Integrity**: Maintains relationships between tables in combined datasets
- **Excel Compatibility**: Handles timezone conversion and data formatting
- **Error Handling**: Graceful handling of missing relationships and null values
- **Progress Feedback**: Real-time updates during export process

## Example Usage with All Commands

### Import Examples
```bash
# Using short forms
python manage.py import_vinyl_data -cs vinyldata1.csv -md skip

# Using long forms
python manage.py import_vinyl_data --csv-file vinyldata1.csv --missing-data skip

# Mixed short and long forms
python manage.py import_vinyl_data -cs vinyldata1.csv --missing-data fill

# Google Sheets with short form
python manage.py import_vinyl_data -gs Sheet2 -md skip

# Excel with short form
python manage.py import_vinyl_data -ex vinyldata-ex1.xlsx -md fill

# Import from subfolder
python manage.py import_vinyl_data -cs trial-fake-data/test-missing-fields.csv -md fill
```

### Delete Examples
```bash
# Test what would be deleted
python manage.py delete_vinyl_data --test-only

# Delete only vinyl records with confirmation
python manage.py delete_vinyl_data

# Delete all tables with confirmation
python manage.py delete_vinyl_data -all

# Force delete without confirmation
python manage.py delete_vinyl_data -artist --force-delete

# Test deletion for specific tables
python manage.py delete_vinyl_data -genre -label --test-only
```

### Export Examples
```bash
# Export with default filename
python manage.py export_vrh_data

# Export with custom filename
python manage.py export_vrh_data my_export.xlsx

# Export with descriptive filename
python manage.py export_vrh_data vrh_data_$(date +%Y%m%d).xlsx
```

## Complete Data Workflow

### Typical Data Management Workflow
1. **Import Data**: Use `import_vinyl_data` to populate the database
2. **Verify Data**: Check the application to ensure data is correctly imported
3. **Export Data**: Use `export_vrh_data` to create backup or analysis files
4. **Clean Data**: Use `delete_vinyl_data` when needed to clear data
5. **Re-import**: Import fresh data as needed

### Data Backup Strategy
```bash
# Create daily backup
python manage.py export_vrh_data vrh_backup_$(date +%Y%m%d).xlsx

# Create weekly backup
python manage.py export_vrh_data vrh_weekly_$(date +%Y%m%d).xlsx

# Create before major changes
python manage.py export_vrh_data vrh_before_changes.xlsx
```

## Troubleshooting

### Common Issues:
1. **File Not Found**: Check that the file exists in the `data-for-import` folder or its subfolders
2. **Permission Errors**: Ensure the Django application has read/write access to the directories
3. **Data Format Errors**: Verify that `year` and `price` columns contain valid integers
4. **Encoding Issues**: Make sure the file is saved with UTF-8 encoding
5. **Missing Data**: Use `-md skip` or `-md fill` to avoid import failures due to incomplete rows
6. **Worksheet Not Found**: If you get an error about a missing worksheet, check the list of available worksheet names in the error message and use one of those.
7. **Deletion Confirmation**: Use `--test-only` to preview what will be deleted before actually deleting
8. **Force Deletion**: Use `--force-delete` to skip confirmation prompts (use with caution)
9. **Subfolder Files**: Files in subfolders (like `trial-fake-data/`) can be imported by specifying the full path relative to the `data-for-import` folder
10. **Export Directory**: The export command automatically creates the `data-export` directory if it doesn't exist
11. **Excel Compatibility**: Export automatically handles timezone conversion for Excel compatibility

### Getting Help:
- Use `python manage.py import_vinyl_data --help` for import command options
- Use `python manage.py delete_vinyl_data --help` for delete command options
- Use `python manage.py export_vrh_data --help` for export command options
- Check the console output for specific error messages
- Verify file format matches the required structure

## Data Validation and Error Handling

### Data Validation Rules

The import command now includes comprehensive data validation to ensure data quality:

#### 1. Year Validation
- Years must be between 1900 and the current year
- Invalid years will cause validation errors

#### 2. Text Field Validation
- Fields `type`, `country`, and `label` must contain text values only
- Numeric values in these fields will cause validation errors

#### 3. Column Structure Validation
- Detects column shifts caused by unquoted commas
- Validates that each row has exactly 8 columns
- Checks for proper CSV formatting

#### 4. Missing Data Handling
- Required fields: `title`, `artist`, `genre`, `year`, `price`, `type`, `country`, `label`
- Missing data is handled according to the `-md` strategy
- **Default fill values:**
    - `year`: current year (e.g., 2024)
    - `label`: 'Unknown'
    - All other fields: see above

### Common CSV Formatting Issues

#### 1. Unquoted Commas in Data Fields
**Problem**: Fields containing commas without quotes cause column shifts
```
❌ Incorrect: Herbert von Karajan,Berlin Philharmonic,Classical
✅ Correct: "Herbert von Karajan,Berlin Philharmonic",Classical
```

**Solution**: Quote fields that contain commas
```csv
title,artist,genre,year,price,type,country,label
"Album Title","Artist Name, Band Name",Pop,1980,25,band,USA,Label Name
```

#### 2. Column Shift Detection
The system detects when data appears in wrong columns due to unquoted commas:
- Years appearing in genre fields
- Text values appearing in numeric fields
- Missing required fields

#### 3. Validation Error Handling
- **Default behavior** (`-md error`): Abort import and show all validation errors
- **Skip strategy** (`-md skip`): Skip problematic rows and continue
- **Fill strategy** (`-md fill`): Fill missing fields with defaults and continue

### Example: Fixing a Problematic CSV File

**Original problematic file** (`vinyldata1-error.csv`):
```csv
title,artist,genre,year,price,type,country,label
Beethoven-Violin Concerto,Salvatore Accardo,Gewandhausorchester Leipzig, Kurt Masur,Classical,1981,117,Classical,Italy,Philips
```

**Issues detected**:
- Unquoted commas in artist field cause column shift
- Year 1981 appears in genre column
- Price 117 appears in year column
- Validation errors: year range, text field validation

**Corrected file** (properly formatted):
```csv
title,artist,genre,year,price,type,country,label
"Beethoven-Violin Concerto","Salvatore Accardo,Gewandhausorchester Leipzig, Kurt Masur",Classical,1981,117,Classical,Italy,Philips
```

### Advanced Validation Functions

The import system includes several specialized validation functions:

#### 1. `validate_data_integrity()`
- Comprehensive validation of all data fields
- Checks year ranges (1900 to current year)
- Validates text fields contain only text values
- Detects column shifts from unquoted commas
- Returns detailed error messages for each issue

#### 2. `precheck_csv_column_count()`
- Validates CSV structure before processing
- Checks that each row has exactly 8 columns
- Provides specific error messages for column count mismatches
- Helps identify unquoted commas in data fields

#### 3. `read_csv_data_with_skip()`
- Alternative CSV reading function for skip strategy
- Skips rows with column count mismatches
- Reports skipped rows in output
- Used when `-md skip` is specified

### Validation Error Messages

When validation fails, you'll see messages like:
```
Data validation failed. Please fix the following issues:
  - Row 3: Year '390' is outside valid range (1900-2025)
  - Row 3: Genre field contains year-like value '1976', possible column shift detected
  - Row 4: Price field contains non-numeric value 'United Kingdom', possible column shift detected

To bypass validation errors, use: -md skip or -md fill
```