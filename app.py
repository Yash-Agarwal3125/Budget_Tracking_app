#imports
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
# MODIFIED: Import psycopg2 for Postgres instead of mysql.connector
import psycopg2
import psycopg2.extras # Needed for dictionary cursor
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
import os


# MODIFIED: Database connection function for Postgres
def get_db_connection():
    # Render provides the database connection URL in an environment variable
    conn_string = os.environ.get('DATABASE_URL')
    try:
        # Establishes a connection to the Postgres database
        conn = psycopg2.connect(conn_string)
        return conn
    except psycopg2.Error as err:
        # Handles connection errors
        print(f"Database Connection Error: {err}")
        return None


# Initialize Flask app
app=Flask(__name__)
CORS(app) # Enable Cross-Origin Resource Sharing



# Define routes
# Route for the index page main login/signup page
@app.route("/")
def index():
    return render_template("index.html")


# Route for the dashboard page
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


#registering new users
@app.route("/api/register",methods=["POST"])
def register_user():
    data=request.get_json()  #getting data from the index.html
    username=data.get("username")
    email=data.get("email")
    password=data.get("password")

    if not username or not email or not password:  #checking if all the data is correctly entered
        return jsonify({'error':'Missing required fields'}),400

    hashed_password=generate_password_hash(password)  #hashing the password

    conn=get_db_connection()
    if conn is None:  #checking if the db is connected
        return jsonify({'error':'DB Failed to connect'}),500

    # MODIFIED: Use dictionary cursor for psycopg2 to access columns by name
    cursor=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:    #trying to insert data in the db
        # NOTE: "User" is a reserved keyword in Postgres, so it must be in double quotes.
        query="insert into \"User\"(user_name,email,password)values(%s,%s,%s)"
        cursor.execute(query,(username,email,hashed_password))
        conn.commit() # Save the changes to the database
        return jsonify({'message':'user registered successfully!'}),201
    # MODIFIED: Catch psycopg2 Error for database-specific issues
    except psycopg2.Error as err:  #throwing the error if not
        return jsonify({'error':str(err)}),500
    finally:
        # Ensure the connection is always closed
        cursor.close()
        conn.close()



#logging in new users
@app.route("/api/login",methods=['POST'])
def login_user():
    data=request.get_json()  #requesting data
    email=data.get('email')
    password=data.get('password')
    if not email or not password:   #checking for valid data
        return jsonify({'error':'Missing the required fields'}),400

    conn=get_db_connection()
    if conn is None:    #checking if db is connected
        return jsonify({'error':'Filed to connect the DB'}),500

    cursor=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        #query for finding the user by the email provided
        query="select * from \"User\" where email=%s"
        cursor.execute(query,(email,))
        user=cursor.fetchone()
        #checking if the user exists and the password hash matches
        if user and check_password_hash(user['password'],password):
            return jsonify({
                'message':'Login Successful',
                'user_id':user['user_id'],
                'username':user['user_name']
            }),200
        else:
            return jsonify({'error':'Invalid email or password'}),401   #error checking
    except psycopg2.Error as err:
        return jsonify({'error':str(err)}),500   #error handling
    finally:
        cursor.close()
        conn.close()



#getting data for dashboard
@app.route("/api/dashboard_data", methods=['GET'])
def get_dashboard_data():
    user_id = request.args.get('user_id')         #getting data from table using user_id
    if not user_id:
        return jsonify({'error':'User ID is required'}), 400   #checking if data is received
    conn=get_db_connection()
    if not conn:
        return jsonify({'error':'Connection to DB failed'}), 500   #checking if there is a problem with the connection
    cursor=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        #query for getting all transactions for the user, ordered by most recent
        query = "SELECT * FROM transaction WHERE user_id = %s ORDER BY date DESC"
        cursor.execute(query,(user_id,))
        transactions=cursor.fetchall()
        
        #calculating income, spend, payable and receivable for the summary cards
        total_income=sum(t['amount'] for t in transactions if t['type']=='Income')
        total_spend=sum(t['amount'] for t in transactions if t['type']=='Expense')
        total_payable=sum(t['amount'] for t in transactions if t['type']=='Payable' and t['status'] == 'Pending')
        total_receivable=sum(t['amount'] for t in transactions if t['type']=='Receivable' and t['status'] == 'Pending')
        current_balance=total_income-total_spend
        
        #a single dictionary of the summary data
        summary={
            'current_balance':float(current_balance),
            'total_income':float(total_income),
            'total_spend':float(total_spend),
            'total_payable':float(total_payable),
            'total_receivable':float(total_receivable)
        }
        # Convert decimal and date objects for JSON serialization
        for tx in transactions:
            tx['amount'] = float(tx['amount'])
            if isinstance(tx['date'], date):
                tx['date'] = tx['date'].isoformat()
        return jsonify({'summary':summary,'transactions':transactions})              #for showing on the website
    except psycopg2.Error as err:
        return jsonify({'error':str(err)}), 500         #error handling
    finally:
        cursor.close()
        conn.close()


#adding new transaction to the table
@app.route('/api/transactions',methods=["POST"])
def add_transaction():
    data=request.get_json()   #getting data from the webpage
    user_id=data.get('user_id')
    tx_type=data.get('type')
    amount=data.get('amount')
    description=data.get('description')
    person_involved=data.get('person_involved')
    # Set a default value for category_name if it's not provided
    category_name = data.get('category_name') or 'Uncategorized'

    # Validation check no longer requires category_name
    if not all([user_id,tx_type,amount,description]):
        return jsonify({'error':'Missing required fields'}),400
        
    # Set status based on transaction type
    status = 'Pending' if tx_type in ['Payable', 'Receivable'] else 'Completed'
    conn=get_db_connection()
    if not conn:
        return jsonify({'error':'Failed to connect DB'}),500
    cursor=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        #query for adding new record and posting it
        query="insert into transaction(user_id,type,amount,category_name,description,date,person_involved,status) values (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query,(user_id,tx_type,amount,category_name,description,date.today(),person_involved,status))
        conn.commit()
        return jsonify({'message':'New transaction added'}), 201
    except psycopg2.Error as err:
        return jsonify({'error':str(err)}), 500    #error handling
    finally:
        cursor.close()
        conn.close()

#make payable as payed
@app.route("/api/pay_debt",methods=["POST"])
def pay_dept():
    data=request.get_json()
    transaction_id=data.get('transaction_id')    #getting transaction id
    if not transaction_id:
        return jsonify({'error':'Transaction ID is required'}),400    #checking if transaction id received
    conn=get_db_connection()
    if not conn:
        return jsonify({'error':'Failed to connect to DB'}),500     #checking if db is connected
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        #query to find the transaction from id
        cursor.execute("SELECT * FROM transaction WHERE transaction_id = %s", (transaction_id,))
        payable_tx = cursor.fetchone()
        if not payable_tx:
            return jsonify({'error':'Payable transaction not found'}), 404      #error if the transaction is not found
        
        # Update the original payable transaction to 'Paid'
        cursor.execute("UPDATE transaction SET status = 'Paid' WHERE transaction_id = %s", (transaction_id,))
        
        # Create a new 'Expense' transaction to reflect the payment
        expense_description = f"Paid debt to {payable_tx['person_involved']}: {payable_tx['description']}"
        query = """
            INSERT INTO transaction (user_id, type, amount, category_name, description, date, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (payable_tx['user_id'], 'Expense', payable_tx['amount'], 'Debt Payment', expense_description, date.today(), 'Completed'))
        conn.commit()
        return jsonify({'message':'Debt marked as paid!'}),200       #giving the message that the debt is paid
    except psycopg2.Error as err:
        conn.rollback() # Rollback changes if an error occurs
        return jsonify({'error':str(err)}), 500      #error handling
    finally:
        cursor.close()
        conn.close()

# Route to reset all transactions for a user
@app.route("/api/reset_transactions", methods=['DELETE'])
def reset_transactions():
    data = request.get_json()
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        # Deletes all transactions for the given user_id
        query = "DELETE FROM transaction WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        conn.commit()
        # Returns the number of rows deleted, which can be useful for logging
        return jsonify({'message': f'{cursor.rowcount} transactions have been reset.'}), 200
    except psycopg2.Error as err:
        conn.rollback() # Rollback changes if an error occurs
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()
