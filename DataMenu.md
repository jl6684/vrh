# Data Handling Menu

## Overview
This document provides instructions for importing vinyl record data into the Django application using the `import_vinyl_data` management command. Data can be imported from CSV, Google Sheets, or Excel files stored in the `data-for-import` folder.

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
- `df-comma-error.csv`
- `vinyldata-ex.xlsx`
- `vinyldata-ex1.xlsx`
- `vinyldata-dup.xlsx`

## Usage Instructions

### 1. Import Data Using Default CSV File
```sh
python manage.py import_vinyl_data
```

### 2. Import Data Using a Specific CSV File
```sh
python manage.py import_vinyl_data --csv-file vinyldata1.csv
```

### 3. Import Data from Google Sheets
```sh
python manage.py import_vinyl_data --gs-file Sheet1
```
- The worksheet name must be one of: `Sheet1`, `Sheet2`, `dupSheet2`.

### 4. Import Data from Excel File
```sh
python manage.py import_vinyl_data --ex-file vinyldata-ex.xlsx
```

### 5. Get Help
```sh
python manage.py import_vinyl_data --help
```

1. **Create Admin Users** (if they don't exist):
   - Admin user: `admin` / `admin123`
   - Test user: `testuser` / `testpass123`

When you run the `import_vinyl_data` command, it will:

1. **Read Data**:
   - Load the specified file (CSV, Google Sheet, or Excel)
   - Extract unique genres, labels, artists, and vinyl records
   - Display the number of records loaded

2. **Create Database Records**:
   - Create Genre objects from unique genres
   - Create Label objects from unique labels
   - Create Artist objects with type and country information
   - Create VinylRecord objects with all details

3. **Provide Feedback**:
   - Show which records were created
   - Display summary statistics
   - List any errors encountered

## Error Handling

If the specified file doesn't exist, the command will:
- Display an error message
- Show the full path where it looked for the file
- List all available files in the `data-for-import` folder

## Example Output

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

To clear and recreate data, use: python manage.py import_vinyl_data --clear
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

## Troubleshooting

### Common Issues:
1. **File Not Found**: Check that the file exists in the `data-for-import` folder
2. **Permission Errors**: Ensure the Django application has read access to the file
3. **Data Format Errors**: Verify that `year` and `price` columns contain valid integers
4. **Encoding Issues**: Make sure the file is saved with UTF-8 encoding

### Getting Help:
- Use `python manage.py import_vinyl_data --help` for command options
- Check the console output for specific error messages
- Verify file format matches the required structure 