# 🎵 Vinyl House - Data Management

Simple and convenient data management for your Django vinyl shop project.

## 🚀 Quick Start

The fastest way to get started:

```bash
# Set up a complete demo vinyl shop
python manage.py manage_data
# Then choose option 1: "Quick Start"

# Or use the shortcut command
python manage.py quickstart
```

## 📋 Main Features

### ⚡ Quick Start
- One-click setup for complete demo shop
- Creates genres, labels, artists, vinyl records, users, reviews, and orders
- Perfect for testing, demos, or development

### ✨ Create Sample Data
- Generate realistic sample data for any model
- Choose specific models or create all at once
- Configurable quantity (1-200 records per model)
- Prevents duplicates automatically

### 🗑️ Clear Data (Safe Deletion)
- Automatic backup before deletion
- Choose specific models or reset everything
- Maintains referential integrity
- Backups saved in `data_exports/backup_*` folders

### 📤 Export Data
- Export to CSV, JSON, or Excel formats
- Single models or complete database
- Timestamped files for version control
- Exports saved in `data_exports/export_*` folders

### 📥 Import Data
- Import from previously exported files
- JSON format (Django serialized) - full support
- CSV format - basic implementation
- Automatic error handling and reporting

### 🧹 Format & Clean Data
- Clean up existing data inconsistencies
- Remove extra spaces, generate missing slugs
- Standardize data formats
- Non-destructive formatting
- 🧹 Artist Formatting: Name capitalization, biography cleaning, country formatting
🏠 Profile Formatting: Address capitalization, phone cleaning
🎵 Vinyl Formatting: Title capitalization, price validation, description cleaning
👤 User Formatting: Name capitalization, email lowercase
⭐ Review Formatting: Rating validation (1-5), comment cleaning
🛒 Order Formatting: Name/address capitalization, email lowercase
🎵 Genre/Label Formatting: Name and description cleaning

### 📊 Statistics
- Detailed database overview
- Record counts for all models
- Additional insights (average prices, etc.)
- Real-time data analysis

## 🎯 Usage Examples

### Development Setup
```bash
# Start fresh
python manage.py manage_data
# Choose: Clear data → Reset Everything
# Choose: Quick Start

# Or create specific data
python manage.py manage_data
# Choose: Create sample data
# Select models: vinyl, artist, review
# Enter count: 50
```

### Backup & Export
```bash
python manage.py manage_data
# Choose: Export data
# Select: All models
# Format: Excel
```

### Data Cleaning
```bash
python manage.py manage_data
# Choose: Format & clean data
# Select models to clean
```

## 📁 File Structure

```
data_exports/
├── export_20241226_151527/     # Export folders (timestamped)
│   ├── artist_*.csv
│   ├── vinyl_*.json
│   └── ...
├── backup_20241226_153022/     # Backup folders (before deletion)
│   ├── artist_*.json
│   └── ...
└── ...
```

## 🛠️ Available Commands

| Command | Description |
|---------|-------------|
| `python manage.py manage_data` | Full interactive data manager |
| `python manage.py quickstart` | Quick access to data manager |
| `python manage.py help manage_data` | Show detailed help |

## 💡 Tips

- **Testing**: Use Quick Start for instant test data
- **Development**: Create 20-50 records per model for realistic testing
- **Demos**: Use 50-100 records for impressive demonstrations
- **Backup First**: Always backup before clearing production data
- **Export Regularly**: Export data before major changes

## 🔧 Models Supported

- **🎵 Genre** - Music genres (Rock, Pop, Jazz, etc.)
- **🏷️ Label** - Record labels (Atlantic, Columbia, etc.)
- **🎤 Artist** - Musicians and bands
- **💿 Vinyl** - Vinyl records with full details
- **👤 User** - Customer accounts
- **📋 Profile** - User profiles and preferences
- **⭐ Review** - Customer reviews and ratings
- **🛒 Order** - Purchase orders and history

## 🎨 Features

- **Interactive Menus** - Easy navigation with numbered options
- **Emojis & Colors** - Visual feedback and clear status messages
- **Error Handling** - Graceful failure with helpful messages
- **Safety Features** - Confirmation prompts for destructive operations
- **Smart Defaults** - Sensible default values for quick setup
- **Progress Feedback** - Real-time status updates during operations

---

*This data manager makes it incredibly simple to set up, maintain, and manage data for your vinyl shop Django project. Perfect for developers, testers, and anyone who needs quick, reliable data management.*
