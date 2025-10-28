#  Flask Web Application – Admin & Dashboard Management System

A full-featured Flask web application designed with a secure authentication system, database integration, and modern UI for managing users, transactions, and admin operations.  
It includes a responsive dashboard, well-structured routes, and modular backend logic — making it easy to extend and deploy.

---

## 📁 Project Structure

```
.
├── app.py                # Main application entry point
├── app2.py               # Additional Flask configuration or version
├── auth.py               # Handles user authentication & sessions
├── admin_routes.py       # Admin-related views and logic
├── database.py           # Database connection and ORM logic
├── config.py             # Application configuration variables
├── transactions.py       # Transaction management logic
├── views.py              # Page rendering and routing
├── extention.py          # Flask extensions and helpers
├── requirements.txt      # All dependencies
├── templates/            # HTML templates for Flask
│   ├── index.html
│   ├── dashboard.html
│   ├── admin.html
│   └── reset_password.html
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── ER DIAGRAM.pdf        # Database structure documentation
└── Sql scrip.sql         # SQL script to initialize the database
```

---

## 🚀 Features

- 🔐 **User Authentication** — Login, signup, and password reset features.  
- 🧑‍💼 **Admin Panel** — Manage users, view system stats, and access transaction data.  
- 📊 **Dashboard** — Interactive data visualization and quick summaries.  
- 💾 **Database Integration** — SQL-based backend with proper ER design.  
- 🧩 **Modular Codebase** — Clear separation of routes, models, and views.  
- 🎨 **Responsive Frontend** — Built with custom CSS and JavaScript for smooth UI/UX.  
- ⚙️ **Configurable Settings** — Centralized configuration via `config.py`.  

---

## 🧰 Tech Stack

| Layer | Technology |
|:------|:------------|
| Backend | Python 3, Flask |
| Frontend | HTML5, CSS3, JavaScript |
| Database | SQL (compatible with MySQL/PostgreSQL/SQLite) |
| Authentication | Flask-Login / JWT (based on code) |
| Tools | Jinja2 Templates, Flask Extensions |

---

## 🏗️ Installation & Setup

Follow these steps to run the project locally:

### 1️⃣ Clone the repository
```bash
git clone https://github.com/yourusername/flask-admin-dashboard.git
cd flask-admin-dashboard
```

### 2️⃣ Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate      # On macOS/Linux
venv\Scripts\activate       # On Windows
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Set up the database
Import the SQL script provided:
```bash
mysql -u root -p < "Sql scrip.sql"
```

### 5️⃣ Run the application
```bash
python app.py
```

Now open your browser and visit:  
👉 **http://127.0.0.1:5000/**

---

## 📘 Configuration

You can modify environment variables or configurations in `config.py`:

```python
class Config:
    SECRET_KEY = "your_secret_key"
    SQLALCHEMY_DATABASE_URI = "mysql://user:password@localhost/dbname"
```

---

## 🧩 Key Modules

| File | Description |
|------|--------------|
| `app.py` | Initializes the Flask app and routes |
| `auth.py` | Manages user login, logout, and registration |
| `admin_routes.py` | Handles all admin dashboard operations |
| `transactions.py` | Controls and tracks financial/user transactions |
| `database.py` | Database connection and ORM setup |
| `views.py` | Renders templates and handles HTTP requests |

---

## 📸 Screenshots

*(Add screenshots of your dashboard and admin pages here)*  
You can place them in `/static/images` and reference like:  
```markdown
![Dashboard Screenshot](static/images/2.png)
```

---

## 🧪 Testing

To run tests (if added):
```bash
pytest
```

---

## 🤝 Contributing

Contributions are welcome!  
1. Fork the repo  
2. Create a new branch (`feature/my-feature`)  
3. Commit changes  
4. Push and open a Pull Request  

---



## 🧠 Authors

**Developed by Yash Agarwal and Kanav Bhardwaj**  
💌 Contact: yashagarwal3125@gmail.com    
🌍 GitHub: [@yashagarwal](https://github.com/Yash-Agarwal3125)  
🌍 GitHub: [@kanavbhardwaj](https://github.com/kanav29)

---

⭐ *If you like this project, don’t forget to star the repository!*
