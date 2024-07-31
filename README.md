
# 📅 Meetingroom Booker

Welcome to the **Meetingroom Booker**! This project is designed to streamline the process of booking meeting rooms, ensuring that scheduling conflicts are minimized and that everyone has a fair chance to reserve the spaces they need.

## 🚀 Technologies Used

- **🐍 Python**: The core language for backend development.
- **🌐 Django**: The web framework used to build the server and handle database operations.
- **🐘 PostgreSQL**: The database system used for storing booking information.
- **🎨 HTML/CSS**: For the front-end interface.
- **⚡ JavaScript**: For interactive front-end elements.

## 🌟 Features

- **🔒 User Authentication**: Secure login and registration system.
- **🏢 Room Management**: Add, update, and delete meeting rooms.
- **📅 Booking Management**: Book, update, and cancel room reservations.
- **❌ Conflict Detection**: Prevents double booking of rooms.

## 🛠️ Installation

Follow these steps to get the project up and running on your local machine.

### 📥 Clone the Repository

```bash
git clone https://github.com/BaburG/Meetingroom-Booker.git
cd Meetingroom-Booker
```

### 🐍 Create a Virtual Environment

```bash
python -m venv venv
```

### 🔄 Activate the Virtual Environment

- On Windows:

  ```bash
  venv\Scripts\Activate
  ```

- On macOS/Linux:

  ```bash
  source venv/bin/activate
  ```

### 📦 Install the Required Packages

```bash
pip install -r requirements.txt
```

### 🗄️ Set Up PostgreSQL Database

Make sure you have PostgreSQL installed and running. Create a new database and update your `settings.py` with your database credentials.

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 🔄 Apply Migrations

```bash
python manage.py migrate
```

### 👤 Create a Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to set up your admin account.

### ▶️ Run the Server

```bash
python manage.py runserver
```

### 🌐 Access the Application

Open your web browser and go to `http://127.0.0.1:8000` to see the application in action.


