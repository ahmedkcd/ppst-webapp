import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_URL = "static/"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "basic/static"),  # Ensure this path matches your structure
]

# settings.py
LOGIN_URL = '/basic/login/'  # Redirect unauthenticated users to the login page
LOGIN_REDIRECT_URL = '/basic/dashboard/'  # Redirect authenticated users to the dashboard
LOGOUT_REDIRECT_URL = '/basic/login/'  # Redirect users to login page after logout
