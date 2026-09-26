🛍️ NovaCart – Modern E-Commerce Store

NovaCart is a modern and responsive e-commerce web application developed using Python Django, HTML, CSS, and JavaScript.

🚀 Features

User Registration

User Login and Logout

Product Listing

Product Details

Product Images

Add to Cart

Update Cart Quantity

Remove Products from Cart

Checkout

Order Processing

Order Confirmation

Django Admin Panel

SQLite Database

Responsive and modern UI

🛠️ Technologies Used

Python

Django

SQLite

HTML5

CSS3

JavaScript

Django Templates

📂 Project Structure

E-commerce site/
│
├── ecommerce/
├── store/
├── media/
│   └── products/
├── db.sqlite3
├── manage.py
├── seed_data.py
└── README.md

⚙️ Installation and Setup

1. Open the project folder

cd "D:\Code alpha Projects\E-commerce site"

2. Install Django

pip install django

3. Run migrations

python manage.py migrate

4. Start the server

python manage.py runserver

Open the website:

http://127.0.0.1:8000/

🔐 Login

Open:

http://127.0.0.1:8000/login/

Register a new account or use an existing account.

👨‍💼 Admin Panel

Open:

http://127.0.0.1:8000/admin/

Create an admin account using:

python manage.py createsuperuser

🛒 Main Pages

Page

URL

Home

/

Login

/login/

Register

/register/

Cart

/cart/

Checkout

/checkout/

Admin

/admin/

🗄️ Database

The project uses SQLite.

Database file:

db.sqlite3

The application stores product, user, order, and order-item information in the database.

🖼️ Product Images

Product images are stored in:

media/products/

Django media configuration:

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

🔄 Application Workflow

Register / Login
       ↓
Browse Products
       ↓
View Product
       ↓
Add to Cart
       ↓
View Cart
       ↓
Checkout
       ↓
Create Order
       ↓
Order Confirmation

🎯 Project Objective

The objective of NovaCart is to demonstrate a complete e-commerce website using Django, including authentication, product management, session-based shopping cart functionality, database operations, and order processing.

🔮 Future Enhancements

Online Payment Integration

Product Search

Categories and Filters

Wishlist

Product Reviews and Ratings

Order Tracking

Email Notifications


📄 License

This project is developed for educational and portfolio purposes.
