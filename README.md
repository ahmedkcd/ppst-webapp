# ppst-webapp
A webapp created for Senior Project Spring 2025

By: Matt Cossari, Atilla Turan, Alvaro Ibarra


Test:

# Django Project

This is a Django-based web application that manages test sessions, responses, and statistics. The project uses PostgreSQL as its database and supports user authentication.

---

## 🚀 Getting Started

Follow these steps to set up and run the project locally.

### 1️⃣ Prerequisites
Ensure you have the following installed:
- [Python (>=3.10)](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/download/)
- [Git](https://git-scm.com/)
- [Pipenv](https://pipenv.pypa.io/en/latest/) *(optional but recommended)*

---

### 2️⃣ Clone the Repository
git clone https://github.com/ahmedkcd/ppst-webapp.git
cd ppst-webapp

---

### 3️⃣ Set Up a Virtual Environment
Using **venv**:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Or using **pipenv** (recommended):
pip install pipenv
pipenv shell

---

### 4️⃣ Install Dependencies
pip install -r requirements.txt

---

### 5️⃣ Configure Database
Make sure **PostgreSQL** is installed and running. Then, create a database:
psql -U postgres
CREATE DATABASE your_database_name;
GRANT ALL PRIVILEGES ON DATABASE your_database_name TO your_database_user;
\q

Update your `settings.py` with your database credentials:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_database_name',
        'USER': 'your_database_user',
        'PASSWORD': 'your_database_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

---

### 6️⃣ Apply Migrations & Create Superuser
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # Follow prompts to set up an admin user

---

### 7️⃣ Run the Server
python manage.py runserver
Visit **http://127.0.0.1:8000/** in your browser.

---

## 🛠 Development
- Collect static files:
  python manage.py collectstatic

- Run tests:
  python manage.py test

- Access Django admin:
  python manage.py runserver
  Then go to **http://127.0.0.1:8000/admin/** and log in with your superuser credentials.

---

## 🐛 Troubleshooting
- **Database connection errors?**  
  - Ensure PostgreSQL is running:  
    sudo service postgresql start  # Linux/Mac
  
  - Check if the database exists using:
    psql -U your_database_user -d your_database_name

- **ModuleNotFoundError?**  
  - Ensure you activated the virtual environment before running Django commands:
    source venv/bin/activate  # On Windows: venv\Scripts\activate
