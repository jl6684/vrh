# Vinyl Record House (VRH)

A full-featured e-commerce platform for vinyl record enthusiasts built with Django 5.2. This application allows users to browse, search, and purchase vinyl records, manage their wishlist, leave reviews, and more.

![VRH Logo](/images/VRHlogo.png)

## Features

- **Product Catalog**: Browse and search vinyl records with filtering by artist, genre, release year, and more
- **User Authentication**: 
  - Custom user profiles
  - Social login integration (Google, GitHub, Microsoft)
  - Session management for both authenticated and anonymous users
- **Shopping Cart**: 
  - Add/remove items
  - Persistent cart across sessions
  - Quantity management
- **Checkout System**:
  - Stripe payment integration
  - Option to place orders without payment
  - Order tracking
- **Wishlist**: Save favorite vinyl records for later
- **Reviews & Ratings**: Leave reviews and ratings for purchased vinyl records
- **Admin Interface**: Enhanced with Django JET for better management
- **Responsive Design**: Mobile-friendly interface using Bootstrap 4

## Technology Stack

- **Backend**: Django 5.2 / Python 3.10+
- **Database**: PostgreSQL
- **Frontend**: 
  - Bootstrap 4.6.2
  - FontAwesome 6.7.2
  - jQuery 3.7.1
  - Popper 1.16.1
- **Payment Processing**: Stripe API
- **Authentication**: Django Allauth with social login providers
- **Admin Interface**: Django JET

## Project Structure

```
vrhp1/                  # Main Django project folder
apps/                   # Custom Django applications
├── accounts/          # User authentication and profiles
├── cart/              # Shopping cart functionality
├── home/              # Landing pages and site info
├── orders/            # Order processing and history
├── reviews/           # Product reviews and ratings
├── vinyl/             # Vinyl record catalog and details
└── wishlist/          # User wishlist functionality
templates/              # HTML templates
static/                 # Static files (CSS, JS, images)
media/                  # User-uploaded content
├── vinyl_covers/      # Album covers
├── audio_samples/     # Preview audio clips
└── profile_pics/      # User profile pictures
```

## Installation

### Prerequisites

- Python 3.10+
- PostgreSQL
- Git

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd vrh
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   pyenv-virtualenv
   pyenv virtualenv 2.7.10 my-virtual-env-2.7.10
   current version:
   pyenv virtualenv my-virtual-env
   python activate myvirtual-env
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (create a `.env` file in the root directory):
   ```
   SITE_SECRET_KEY=your_secret_key
   DB_PASSWORD=your_database_password
   STRIPE_PUBLISHABLE_KEY=your_stripe_public_key
   STRIPE_SECRET_KEY=your_stripe_secret_key
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

8. Access the application at http://127.0.0.1:8000/

## Data Management

The application includes management commands for importing and managing vinyl record data:
- `create_sample_data`: Create data
- `manage_data`: interactive CLI to do CRUD
- `import_vinyl_data`: Import vinyl records from JSON data
- `match_vinyl_covers`: Match cover images to vinyl records
- `cleanup_cover_duplicates`: Remove duplicate cover images

Example usage:
```bash
python manage.py import_vinyl_data --file data_exports/vinyldata.json
python manage.py match_vinyl_covers
```

## Payment Integration

The application uses Stripe for payment processing. To test payments, use Stripe's test credit cards:

- Card Number: `4242 4242 4242 4242`
- Expiration: Any future date
- CVC: Any 3 digits
- ZIP: Any 5 digits





## Credits

- Frontend design inspired by: https://github.com/codrkai/codrkai.github.io
- Icons from FontAwesome