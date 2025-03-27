# ppst-webapp

A webapp created for Senior Project Spring 2025

By: Matt Cossari, Atilla Turan, Alvaro Ibarra, Tanner Dodge, Govinda Avinesh Muthuselvam, Amy'r Smith and Adam Mahrous

## 🚀 Getting Started

Follow these steps to set up and run the project locally.

### 1️⃣ Prerequisites
Ensure you have the following installed:
- [Python (>=3.10)](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)
---

### 2️⃣ Clone the Repository
git clone https://github.com/ahmedkcd/ppst-webapp.git

cd ppst-webapp

---

### 3️⃣ Set Up a Virtual Environment
Using **venv**:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


---

### 4️⃣ Install Django
pip install django

---


### 5️⃣ Apply Migrations & Create Superuser
python manage.py makemigrations

python manage.py migrate

python manage.py shell < fixture.py

python manage.py createsuperuser  # Follow prompts to set up an admin user

---

### 6️⃣ Run the Server
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

- **ModuleNotFoundError?**  
  - Ensure you activated the virtual environment before running Django commands:
    source venv/bin/activate  # On Windows: venv\Scripts\activate

