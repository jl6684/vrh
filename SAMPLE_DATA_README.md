# 🎵 Vinyl House - Simple Data Creator

A user-friendly command for creating sample data for your vinyl record store.

## 🚀 Quick Start

### Interactive Mode (Recommended)
```bash
python manage.py create_sample_data
```
This will guide you through choosing how much sample data to create.

### Quick Options
```bash
# Minimal data (10 records) - perfect for quick testing
python manage.py create_sample_data --minimal

# Quick setup with default amount (25 records)
python manage.py create_sample_data --quick

# Custom amount
python manage.py create_sample_data --records 15
```

## 📊 What Gets Created

The tool creates:
- **Genres**: Rock, Pop, Jazz, Blues, Classical, Electronic, Hip-Hop, R&B, Country, Folk, etc.
- **Labels**: Various record labels with contact information
- **Artists**: Famous musicians from different eras and genres
- **Vinyl Records**: Classic albums with realistic prices and descriptions
- **User Accounts**: Admin and test user accounts

## 🎯 Data Amounts

- **Minimal (10 records)**: Core collection, perfect for testing
- **Standard (25 records)**: Good for development work
- **Large (50+ records)**: Great for demos and showcases

## 🔑 Default Login Credentials

After running the command, you can login with:
- **Admin**: `admin` / `admin123`
- **Test User**: `testuser` / `testpass123`

## 📝 Example Usage

```bash
# Interactive mode - choose your options step by step
python manage.py create_sample_data

# Quick minimal setup
python manage.py create_sample_data --minimal

# Create exactly 15 records
python manage.py create_sample_data --records 15
```

The command is safe to run multiple times - it won't create duplicates.

## 🎵 Features

- ✨ **Interactive**: Friendly step-by-step guidance
- 🎯 **Flexible**: Choose exactly how much data you need
- 🛡️ **Safe**: Won't create duplicate records
- 📊 **Comprehensive**: Creates all related data types
- 🚀 **Fast**: Quick setup for development and testing

Perfect for getting your vinyl shop up and running with realistic sample data!
