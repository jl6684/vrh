# Data Handling Menu

## Overview
This document provides instructions for importing and deleting vinyl record data in the Django application using management commands. Data can be imported from CSV, Google Sheets, or Excel files stored in the `data-for-import` folder, and deleted using the `delete_vinyl_data` command.

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

## Available Data Files
The following files are available in the `data-for-import` folder:
- `vinyldata.csv` (default)
- `vinyldata1.csv`
- `data-error.csv`
- `vinyldata-ex.xlsx`
- `vinyldata-ex1.xlsx`
- `vinyldata-dup.xlsx`
- `pop-test-data.csv` (new test data)

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

## Example Usage with Mixed Arguments

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

## User Management

1. **Create Admin Users** (if they don't exist):
   - Admin user: `admin` / `admin123`
   - Test user: `testuser` / `testpass123`

## Data Processing Workflow

### Import Process
When you run the `import_vinyl_data` command, it will:

1. **Read Data**:
   - Load the specified file (CSV, Google Sheet, or Excel)
   - Extract unique genres, labels, artists, and vinyl records
   - Display the number of records loaded

2. **Detect Duplicates**:
   - Check which vinyl records already exist in the database
   - Display list of existing records that won't be recreated
   - Show count of new records that will be created

3. **Create Database Records**:
   - Create Genre objects from unique genres
   - Create Label objects from unique labels
   - Create Artist objects with type and country information
   - Create VinylRecord objects with all details (only new records)

4. **Provide Feedback**:
   - Show which records were created
   - Display summary statistics
   - List any errors encountered
   - Report skipped or filled rows if using `-md skip` or `-md fill`

### Delete Process
When you run the `delete_vinyl_data` command, it will:

1. **Analyze Data**:
   - Count records in tables to be deleted
   - Show summary of what will be deleted

2. **Confirm Action** (unless `--force-delete` or `--test-only`):
   - Display warning message with record counts
   - Prompt for user confirmation

3. **Execute Deletion**:
   - Delete vinyl records first (to respect foreign keys)
   - Delete other specified tables
   - Show deletion results

## Error Handling

### Import Errors
If the specified file doesn't exist, the command will:
- Display an error message
- Show the full path where it looked for the file
- List all available files in the `data-for-import` folder

If you specify a worksheet name for Google Sheets that does not exist, the error message will show all available worksheet names in the sheet so you can correct your input.

If missing data is encountered:
- With `-md error` or `--missing-data error` (default), the import will stop and show a detailed error message for the first problematic row.
- With `-md skip` or `--missing-data skip`, the import will continue, and each skipped row will be reported in the output.
- With `-md fill` or `--missing-data fill`, the import will continue, and each row with filled fields will be reported in the output.

### Delete Errors
- **No records found**: Command will warn if no records are found to delete
- **Database errors**: Any database errors will be displayed with details
- **Cancellation**: User can cancel deletion at confirmation prompt

## Example Output

### Import Output
```
Creating sample data from vinyldata1.csv...
Successfully loaded 25 records from vinyldata1.csv
Created admin user: admin/admin123
Created test user: testuser/testpass123
Created genre: Rock
Created genre: Pop
Created genre: Jazz
Created artist: The Beatles (band)
Created artist: Bob Dylan (male)
Created vinyl: Abbey Road by The Beatles
Created vinyl: Highway 61 Revisited by Bob Dylan

Sample data created successfully!
- 8 genres
- 5 labels
- 15 artists
- 25 vinyl records

Login credentials:
Admin: admin / admin123
User: testuser / testpass123

To delete vinyl data, please use: python manage.py delete_vinyl_data
Details information please refer to DataMenu.md
```

### Import Output with Duplicate Detection
```
Creating sample data from Excel file: vinyldata-dup.xlsx...
Successfully loaded 3 records from vinyldata-dup.xlsx
Duplicate detection: 3 records already exist in database:
  - "天才與白痴" by 許冠傑
  - "賣身契" by 許冠傑
  - "財神到" by 許冠傑
  0 new records will be created.

Sample data created successfully!
- 11 genres
- 35 labels
- 43 artists
- 61 vinyl records (total in database)
- 5 users
- 5 user profiles

Login credentials:
Admin: admin / admin123
User: testuser / testpass123

To delete vinyl data, please use: python manage.py delete_vinyl_data
Details information please refer to DataMenu.md
```

### Delete Output
```
About to delete:
- 68 vinyl records
- 49 artists
- 11 genres
- 40 labels

This action cannot be undone!
Are you sure you want to continue? (yes/no): yes
Deleted 68 vinyl records
Deleted 49 artists
Deleted 11 genres
Deleted 40 labels

Successfully deleted vinyl data!
Total records deleted: 168
```

### Test-Only Output
```
TEST ONLY - Would delete:
- 68 vinyl records
- 49 artists
- 11 genres
- 40 labels
Total: 168 records
```

## Tips for Data File Preparation

1. **Column Headers**: Ensure your file has the exact column names shown above
2. **Data Format**: 
   - `year` and `price` should be integers
   - `title`, `artist`, `genre`, `type`, `country` should be text
   - `label` can be left blank (empty string)
3. **Encoding**: Use UTF-8 encoding for proper handling of special characters
4. **Quotes**: Use double quotes around text values if they contain commas
5. **Field Separation**: Each row must have exactly 8 fields separated by commas
6. **Missing Data Handling**: Use the `-md` or `--missing-data` option to control how missing or incomplete rows are processed during import.

## Common Data Input Errors and Solutions

### Error: "Expected 8 fields in line X, saw Y"
**Cause**: A field contains unquoted commas, causing the parser to split it into multiple fields.

**Solution**: Quote fields that contain commas:
```
"Beethoven-Violin Concerto","Salvatore Accardo, Gewandhausorchester Leipzig, Kurt Masur",Classical,1981,117,Classical,Italy,Philips
```

### How to Handle Fields with Commas

1. **Wrap the entire field in double quotes**
2. **Use consistent quoting style**
   - You can quote all text fields for consistency
   - Example: `"Album Title","Artist Name","Rock",1970,25,"band","Country","Label"`

3. **Check for trailing commas**

### Validation Features

The import command includes:
- **Automatic structure validation**
- **Detailed error messages** for problematic rows
- **Multiple parsing attempts** for CSVs
- **Column count verification** for each row
- **Configurable missing data handling** via `-md` or `--missing-data` argument
- **Dynamic worksheet validation** for Google Sheets: if a worksheet is not found, the error will list all available worksheet names.

## Troubleshooting

### Common Issues:
1. **File Not Found**: Check that the file exists in the `data-for-import` folder
2. **Permission Errors**: Ensure the Django application has read access to the file
3. **Data Format Errors**: Verify that `year` and `price` columns contain valid integers
4. **Encoding Issues**: Make sure the file is saved with UTF-8 encoding
5. **Missing Data**: Use `-md skip` or `-md fill` to avoid import failures due to incomplete rows
6. **Worksheet Not Found**: If you get an error about a missing worksheet, check the list of available worksheet names in the error message and use one of those.
7. **Deletion Confirmation**: Use `--test-only` to preview what will be deleted before actually deleting
8. **Force Deletion**: Use `--force-delete` to skip confirmation prompts (use with caution)

### Getting Help:
- Use `python manage.py import_vinyl_data --help` for import command options
- Use `python manage.py delete_vinyl_data --help` for delete command options
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

**Original problematic file** (`data-error.csv`):
```csv
title,artist,genre,year,price,type,country,label
Beethoven-Violin Concerto,Salvatore Accardo,Gewandhausorchester Leipzig, Kurt Masur,Classical,1981,117,Classical,Italy,Philips
```

**Issues detected**:
- Unquoted commas in artist field cause column shift
- Year 1981 appears in genre column
- Price 117 appears in year column
- Validation errors: year range, text field validation

**Corrected file** (`data-error-fixed.csv`):
```csv
title,artist,genre,year,price,type,country,label
"Beethoven-Violin Concerto","Salvatore Accardo,Gewandhausorchester Leipzig, Kurt Masur",Classical,1981,117,Classical,Italy,Philips
```

### Validation Error Messages

When validation fails, you'll see messages like:
```
Data validation failed. Please fix the following issues:
  - Row 3: Year '390' is outside valid range (1900-2025)
  - Row 3: Genre field contains year-like value '1976', possible column shift detected
  - Row 4: Price field contains non-numeric value 'United Kingdom', possible column shift detected

To bypass validation errors, use: -md skip or -md fill
``` 