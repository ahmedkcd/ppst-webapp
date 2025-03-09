<<<<<<< HEAD
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


### 5️⃣ Start a Django Project - will create a Django project inside ppst-webapp-2 directory
django-admin startproject djangoproject . 


---

### 6️⃣ Apply Migrations & Create Superuser
python manage.py makemigrations

python manage.py migrate

python manage.py shell < fixture.py

python manage.py createsuperuser  # Follow prompts to set up an admin user

---

### 7️⃣ Run the Server (restarts the surver to apply changes)
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

=======
# djangoproject
<h3>Django project template</h3>


**Installation instructions**
  
  <ol>
  <li>Clone this repository: <b>git clone https://github.com/grbaliga/djangostarter.git</b> </li>
  <li>In the folder djangostarter, create a virtual environment: <b>python -m venv venv</b> </li>
  <li>Activate the virtual environment:  <b>source venv/bin/activate</b></li>
  <li>Install dependencies:  <b>pip install django</b></li>
  <li>Perform migrations:  <b>python manage.py makemigrations</b></li> 
  <li>Migrate:  <b>python manage.py migrate</b></li>
  <li>Install the fixture:  <b>python manage.py shell < fixture.py</b></li>
  <li>Run the project (either from the command line using  <b>python manage.py runserver</b>) or from your IDE</li>
  
  </ol>
>>>>>>> djangostarter/Amyr-Final-Prog-Branch
