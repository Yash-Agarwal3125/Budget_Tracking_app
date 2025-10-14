# Personal Budget Tracker

A full-stack web application designed to help users gain control over their personal finances through a clean, intuitive, and responsive interface. This application provides a clear overview of financial health by tracking income, expenses, and debts in real-time.

## Table of Contents
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Local Installation](#local-installation)
- [Deployment](#deployment)
- [API Endpoints](#api-endpoints)
- [Future Improvements](#future-improvements)

## Key Features

- **Secure User Authentication:** Ensures user data is private with a robust registration and login system.
- **Dynamic Financial Dashboard:** At-a-glance overview of key financial metrics:
    - **Current Balance:** The real-time difference between total income and expenses.
    - **Financial Summaries:** Cards displaying total income, expenses, and pending debts.
- **Comprehensive Transaction Management:**
    - **Log Transactions:** Easily add income, expenses, payables (money you owe), and receivables (money owed to you).
    - **Categorize Spending:** Assign categories to expenses for better financial analysis (this feature is optional per entry).
- **Integrated Debt Tracking:**
    - **Unified View:** A dedicated table shows all pending debts and loans in one place.
    - **One-Click Settlement:** Mark a "Payable" as paid, which automatically creates a corresponding expense transaction, keeping your books balanced.
- **User-Centric Interface:**
    - **Data Reset:** A secure "Reset All Data" option to clear the account for a fresh start.
    - **Responsive Design:** A seamless experience across desktop, tablet, and mobile devices.
    - **Infinite Scroll Tables:** Transaction tables are scrollable, preventing page clutter and ensuring a smooth user experience even with extensive data.
- **Localization:** All currency is displayed in Indian Rupees (Rs.).

## Tech Stack

| Category      | Technology                                                                                                                              |
|---------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| **Backend** | ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?logo=flask&logoColor=white) ![Gunicorn](https://img.shields.io/badge/Gunicorn-499848?logo=gunicorn&logoColor=white) |
| **Frontend** | ![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black) |
| **Database** | ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)                                             |
| **Deployment**| ![Render](https://img.shields.io/badge/Render-46E3B7?logo=render&logoColor=white) ![Neon](https://img.shields.io/badge/Neon-0A5653?logo=neon&logoColor=white)                                                     |

## Project Structure


.
├── app.py              # Main Flask application with all backend logic and API routes.
├── requirements.txt    # Python dependencies for the project.
├── Sql scrip.sql       # SQL script for initial database schema setup.
├── static/             # Contains all static assets (CSS, JavaScript).
│   ├── css/
│   │   └── dashboard.css
│   └── js/
│       ├── dashboard.js
│       └── index.js
└── templates/          # Contains all HTML templates rendered by Flask.
├── dashboard.html
└── index.html


## Getting Started

Follow these instructions to set up a local development environment.

### Prerequisites

- Python 3.10+
- A database management tool that supports PostgreSQL (e.g., DBeaver, TablePlus).
- A free account on [Neon](https://neon.tech/) for a cloud-hosted database.

### Local Installation

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
    cd your-repo-name
    ```

2.  **Set up the Database (Neon):**
    - Create a new project on Neon to get a free Postgres database.
    - Connect to this database using your management tool and the provided **External Connection URL**.
    - Run the SQL commands from `Sql scrip.sql` to create the `User` and `transaction` tables.
    - Copy the **Database Connection URL** (the one that starts with `postgres://...`).

3.  **Create a Virtual Environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
    ```

4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Set Environment Variables:**
    - Create a file named `.env` in the root of your project.
    - Add the following line, pasting the URL you copied from Neon:
      ```
      DATABASE_URL='postgres://user:password@host/dbname'
      ```

6.  **Run the Application:**
    - You will need to temporarily add the development server back to `app.py`. Add these lines to the end of the file:
      ```python
      if __name__ == "__main__":
          app.run(debug=True, port=5000)
      ```
    - Start the Flask server:
      ```bash
      python app.py
      ```
    - The application will be available at `http://127.0.0.1:5000`.

## Deployment

This application is deployed on Render with a Neon database.

1.  **Database (Neon):** Follow the "Database Setup" steps in the Local Installation section.
2.  **Application (Render):**
    - Create a new **Web Service** on Render and connect it to your GitHub repository.
    - **Configuration:**
        - **Build Command:** `pip install -r requirements.txt`
        - **Start Command:** `gunicorn app:app`
    - **Environment Variables:**
        - **Key:** `DATABASE_URL`
        - **Value:** Paste the Connection URL from your Neon database.
    - Deploy the service.

## API Endpoints

The application exposes the following RESTful API endpoints.

| Method   | Endpoint                  | Description                                            |
|----------|---------------------------|--------------------------------------------------------|
| `POST`   | `/api/register`           | Registers a new user.                                  |
| `POST`   | `/api/login`              | Authenticates a user and returns a user object.        |
| `GET`    | `/api/dashboard_data`     | Fetches all transaction and summary data for a user.   |
| `POST`   | `/api/transactions`       | Adds a new transaction.                                |
| `POST`   | `/api/pay_debt`           | Marks a payable as paid and creates an expense.        |
| `DELETE` | `/api/reset_transactions` | Deletes all transactions for the authenticated user.   |

## Future Improvements

- [ ] **Data Visualization:** Add charts (e.g., pie chart for expenses by category) to the dashboard.
- [ ] **Edit/Delete Transactions:** Allow users to modify or remove individual transactions.
- [ ] **Date Filtering:** Implement filters to view financial data for specific date ranges (e.g., monthly, yearly).
- [ ] **Category Management:** Allow users to create, edit, and delete their own custom spending categories.

