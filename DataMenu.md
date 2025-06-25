# Data Handling Menu - JL6684_VRH2

## Overview
This document provides instructions for importing vinyl record data into the Django application using CSV files stored in the `data-for-import` folder.

## Prerequisites
- Django project is set up and running
- CSV files are placed in the `data-for-import` folder
- CSV files must have the following column structure:
  - `title` - Album/record title
  - `artist` - Artist or band name
  - `genre` - Music genre
  - `year` - Release year
  - `price` - Price in integer format
  - `type` - Artist type (male, female, band, Classical, Assortment, etc.)
  - `country` - Artist's country of origin
  - `label` - Record label (can be left blank)

## Available CSV Files
The following CSV files are available in the `data-for-import` folder:
- `vinyldata.csv` (default)
- `vinyldata1.csv`
- `vinyldata2.csv`
- `vinyldata_gsheet_template.csv` (template for Google Sheets)

## Usage Instructions

### 1. Import Data Using Default CSV File
To import data from the default CSV file (`vinyldata.csv`):
```project folder on terminal
python manage.py create_sample_data
```

### 2. Import Data Using Specific CSV File
To import data from a specific CSV file:
```project folder on terminal
python manage.py create_sample_data --csv-file vinyldata1.csv
```

### 3. Get Help
To see all available options and help information:
```project folder on terminal
python manage.py create_sample_data --help
```

## What the Command Does

When you run the `create_sample_data` command, it will:

1. **Create Admin Users** (if they don't exist):
   - Admin user: `admin` / `admin123`
   - Test user: `testuser` / `testpass123`

2. **Read CSV Data**:
   - Load the specified CSV file
   - Extract unique genres, labels, artists, and vinyl records
   - Display the number of records loaded

3. **Create Database Records**:
   - Create Genre objects from unique genres
   - Create Label objects from unique labels
   - Create Artist objects with type and country information
   - Create VinylRecord objects with all details

4. **Provide Feedback**:
   - Show which records were created
   - Display summary statistics
   - List any errors encountered

## Error Handling

If the specified CSV file doesn't exist, the command will:
- Display an error message
- Show the full path where it looked for the file
- List all available CSV files in the `data-for-import` folder

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
```

## Tips for CSV File Preparation

1. **Column Headers**: Ensure your CSV file has the exact column names shown above
2. **Data Format**: 
   - `year` and `price` should be integers
   - `title`, `artist`, `genre`, `type`, `country` should be text
   - `label` can be left blank (empty string)
3. **Encoding**: Use UTF-8 encoding for proper handling of special characters
4. **Quotes**: Use double quotes around text values if they contain commas
5. **Field Separation**: Each row must have exactly 8 fields separated by commas

## Common Data Input Errors and Solutions

### Error: "Expected 8 fields in line X, saw Y"
**Cause**: A field contains unquoted commas, causing the CSV parser to split it into multiple fields.

**Example of Problematic Data**:
```
Beethoven-Violin Concerto,Salvatore Accardo,Gewandhausorchester Leipzig, Kurt Masur,Classical,1981,117,Classical,Italy,Philips
```

**Solution**: Quote fields that contain commas:
```
"Beethoven-Violin Concerto","Salvatore Accardo, Gewandhausorchester Leipzig, Kurt Masur",Classical,1981,117,Classical,Italy,Philips
```

### How to Handle Fields with Commas

1. **Wrap the entire field in double quotes**
   - Wrong: `Artist Name, Band Name`
   - Correct: `"Artist Name, Band Name"`

2. **Use consistent quoting style**
   - You can quote all text fields for consistency
   - Example: `"Album Title","Artist Name","Rock",1970,25,"band","Country","Label"`

3. **Check for trailing commas**
   - Ensure no extra commas at the end of lines
   - Each row should have exactly 8 fields

### Validation Features

The import command now includes:
- **Automatic CSV structure validation**
- **Detailed error messages** pointing to specific problematic rows
- **Multiple parsing attempts** with different quote handling
- **Column count verification** for each row

## Troubleshooting

### Common Issues:
1. **File Not Found**: Check that the CSV file exists in the `data-for-import` folder
2. **Permission Errors**: Ensure the Django application has read access to the CSV file
3. **Data Format Errors**: Verify that `year` and `price` columns contain valid integers
4. **Encoding Issues**: Make sure the CSV file is saved with UTF-8 encoding

### Getting Help:
- Use `python manage.py create_sample_data --help` for command options
- Check the console output for specific error messages
- Verify CSV file format matches the required structure 