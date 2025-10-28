import os

# Setting up database connection using environment variables
# This dictionary holds the configuration details for connecting to the database.
# It securely fetches credentials from environment variables with fallback defaults.
db_config = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'Hahalol@29'),
    'database': os.environ.get('DB_DATABASE', 'budget_tracking_web')
}
