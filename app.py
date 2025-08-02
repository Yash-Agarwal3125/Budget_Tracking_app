# #imports
# from flask import Flask, render_template, request, jsonify
# from flask_cors import CORS
# import mysql.connector
# from werkzeug.security import generate_password_hash, check_password_hash
# from datetime import date


# #setting up database connection
# db_config = {
#     'host': 'localhost',
#     'user': 'root',
#     'password': 'mysql_123', 
#     'database': 'budget_tracking_web' 
# }



# #checking database connection
# def get_db_connection():
#     try:
#         conn = mysql.connector.connect(**db_config)
#         return conn
#     except mysql.connector.Error as err:
#         print(f"Database Connection Error: {err}")
#         return None


# # Initialize Flask app
# app=Flask(__name__)
# CORS(app)



# # Define routes
# # Route for the index page main login/signup page
# @app.route("/")
# def index():  
#     return render_template("index.html")


# # Route for the dashboard page
# @app.route("/dashboard")
# def dashboard():
#     # return "<h1>Dashboard Page</h1><p>page under construction!</p>"   #update this to render the actual dashboard template when ready
#     # Uncomment the line below when the dashboard template is ready 
#     return render_template("dashboard.html")
    
    
# #registering new users
# @app.route("/api/register",methods=["POST"])
# def register_user():
#     data=request.get_json()  #getting data from the index.html
#     username=data.get("username")
#     email=data.get("email")
#     password=data.get("password")
    
#     if not username or not email or not password:  #checking is all the data is correctly entered
#         return jsonify({'error':'Missing required fields'}),400
    
#     hashed_password=generate_password_hash(password)  #hashing the passowrd
    
#     conn=get_db_connection()
#     if conn is None:  #checking is the db is connected
#         return jsonify({'error':'DB Failed to connect'}),500
    
#     cursor=conn.cursor()   
#     try:    #trying to insert data in the db
#         query="insert into User(user_name,email,password)values(%s,%s,%s)"
#         cursor.execute(query,(username,email,hashed_password))
#         conn.commit()
#         return jsonify({'message':'user registered successfully!'}),201
#     except mysql.connector.Error as err:  #throwing the error if not
#         return jsonify({'error':str(err)}),500
#     finally:   
#         cursor.close()
#         conn.close()
    
    

# #logging in new users
# @app.route("/api/login",methods=['POST'])  
# def login_user():
#     data=request.get_json()  #requesting data 
#     email=data.get('email')
#     password=data.get('password')
#     if not email or not password:   #checking for valid data like email and password hash
#         return jsonify({'error':'Missing the required fields'}),400
    
#     conn=get_db_connection()
#     if conn is None:    #checking if db is connected
#         return jsonify({'error':'Filed to connect the DB'}),500
    
#     cursor=conn.cursor(dictionary=True)
#     try:
#         query="select * from User where email=%s"    #query for finding the password of the email provided
#         cursor.execute(query,(email,))
#         user=cursor.fetchone()
#         if user and check_password_hash(user['password'],password):   #checking if the password match
#             return jsonify({   
#                 'message':'Login Successful',
#                 'user_id':user['user_id'],
#                 'username':user['user_name']
#             }),200
#         else:
#             return jsonify({'error':'Invalid email or passowrd'}),401   #error checking 
#     except mysql.connector.Error as err:
#         return jsonify({'error':str(err)}),500   #error handling
#     finally:
#         cursor.close()
#         conn.close()
        
        

# #getting data for dashboard
# @app.route("/api/dashboard_data", methods=['GET'])
# def get_dashboard_data():
#     user_id = request.args.get('user_id')         #getting data from table using user_id
#     if not user_id:
#         return jsonify({'error':'User ID is required'})   #checking if data is recived
#     conn=get_db_connection()
#     if not conn:
#         return jsonify({'error':'Connection to DB failed'})   #checking if there is a problem with the connection 
#     cursor=conn.cursor(dictionary=True)
#     try:
#         query = "SELECT * FROM transaction WHERE user_id = %s ORDER BY date DESC"    #query for getting data from table 
#         cursor.execute(query,(user_id,))
#         transactions=cursor.fetchall()
#         total_income=sum(t['amount'] for t in transactions if t['type']=='Income')        #calculating income, spend, payable and recivable
#         total_spend=sum(t['amount'] for t in transactions if t['type']=='Expense')
#         total_payable=sum(t['amount'] for t in transactions if t['type']=='Payable')
#         total_receivable=sum(t['amount'] for t in transactions if t['type']=='Receivable')
#         current_balance=total_income-total_spend
#         summary={                                    #a single row of the dta just fetched 
#             'current_balance':float(current_balance),
#             'total_income':float(total_income),
#             'total_spend':float(total_spend),
#             'total_payable':float(total_payable),
#             'total_recivable':float(total_receivable)
#         }
#         # Convert decimal and date objects for JSON
#         for tx in transactions:
#             tx['amount'] = float(tx['amount'])
#             tx['date'] = tx['date'].isoformat()
#         return jsonify({'summary':summary,'transactions':transactions})              #for showing in the website
#     except mysql.connector.Error as err:
#         return jsonify({'error':str(err)})         #error handling
#     finally:
#         cursor.close()
#         conn.close()


# #adding new transaction to the table
# @app.route('/api/transactions',methods=["POST"])
# def add_transaction():
#     data=request.get_json()   #getting data from the webpage
#     user_id=data.get('user_id')
#     tx_type=data.get('type')
#     amount=data.get('amount')
#     category_name=data.get('category_name')
#     description=data.get('description')
#     person_involved=data.get('person_involved')
#     if not all([user_id,tx_type,amount,category_name,description]):  #checking the data is recived
#         return ({'error':'Missing required fields'}),400
#     status = 'Pending' if tx_type in ['Payable', 'Receivable'] else 'Completed'     #setting up status 
#     conn=get_db_connection()
#     if not conn:
#         return jsonify({'error':'Failed to connect DB'}),500        #checking the DB connection
#     cursor=conn.cursor()
#     try:
#         query="insert into transaction(user_id,type,amount,category_name,description,date,person_involved,status) values (%s, %s, %s, %s, %s, %s, %s, %s)"
#         cursor.execute(query,(user_id,tx_type,amount,category_name,description,date.today(),person_involved,status))
#         conn.commit() 
#         return jsonify({'message':'New transaction added'})   #query for adding new record and posting it 
#     except mysql.connector.Error as err:
#         return jsonify({'error':str(err)})    #error handling
#     finally:
#         cursor.close()
#         conn.close()

# #make payable as payed
# @app.route("/api/pay_debt",methods=["POST"])
# def pay_dept():
#     data=request.get_json()
#     transaction_id=data.get('transaction_id')    #getting transaction id
#     if not transaction_id:
#         return jsonify({'error':'Transaction _id is required'}),400    #checking if transaction id recived
#     conn=get_db_connection()
#     if not conn:
#         return jsonify({'error':'Failed to connect to DB'}),500     #checking if db is connected
#     cursor = conn.cursor(dictionary=True)
#     try:
#         cursor.execute("SELECT * FROM transaction WHERE transaction_id = %s", (transaction_id,))          #query to find the transaction from id 
#         payable_tx = cursor.fetchone()
#         if not payable_tx:
#             return jsonify({'error':'Payable transaction not found'})      #error if the transaction is not found
#         cursor.execute("UPDATE transaction SET status = 'Paid' WHERE transaction_id = %s", (transaction_id,))
#         expense_description = f"Paid debt to {payable_tx['person_involved']}: {payable_tx['description']}"
#         query = """
#             INSERT INTO transaction (user_id, type, amount, category_name, description, date, status)      
#             VALUES (%s, %s, %s, %s, %s, %s, %s)
#         """         #setting the record that the record is payed
#         cursor.execute(query, (payable_tx['user_id'], 'Expense', payable_tx['amount'], 'Debt Payment', expense_description, date.today(), 'Completed'))
#         conn.commit()
#         return jsonify({'message':'Debt maked as payed!'}),200       #giving the message that the debt is payed
#     except mysql.connector.Error as err:
#         conn.rollback()
#         return jsonify({'error':str(err)})      #error handling
#     finally: 
#         cursor.close()
#         conn.close()
    

# if __name__ == "__main__":
#     app.run(debug=True)













#imports
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date


#setting up database connection
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'mysql_123',
    'database': 'budget_tracking_web'
}



#checking database connection
def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Database Connection Error: {err}")
        return None


# Initialize Flask app
app=Flask(__name__)
CORS(app)



# Define routes
# Route for the index page main login/signup page
@app.route("/")
def index():
    return render_template("index.html")


# Route for the dashboard page
@app.route("/dashboard")
def dashboard():
    # return "<h1>Dashboard Page</h1><p>page under construction!</p>"   #update this to render the actual dashboard template when ready
    # Uncomment the line below when the dashboard template is ready
    return render_template("dashboard.html")


#registering new users
@app.route("/api/register",methods=["POST"])
def register_user():
    data=request.get_json()  #getting data from the index.html
    username=data.get("username")
    email=data.get("email")
    password=data.get("password")

    if not username or not email or not password:  #checking is all the data is correctly entered
        return jsonify({'error':'Missing required fields'}),400

    hashed_password=generate_password_hash(password)  #hashing the passowrd

    conn=get_db_connection()
    if conn is None:  #checking is the db is connected
        return jsonify({'error':'DB Failed to connect'}),500

    cursor=conn.cursor()
    try:    #trying to insert data in the db
        query="insert into User(user_name,email,password)values(%s,%s,%s)"
        cursor.execute(query,(username,email,hashed_password))
        conn.commit()
        return jsonify({'message':'user registered successfully!'}),201
    except mysql.connector.Error as err:  #throwing the error if not
        return jsonify({'error':str(err)}),500
    finally:
        cursor.close()
        conn.close()



#logging in new users
@app.route("/api/login",methods=['POST'])
def login_user():
    data=request.get_json()  #requesting data
    email=data.get('email')
    password=data.get('password')
    if not email or not password:   #checking for valid data like email and password hash
        return jsonify({'error':'Missing the required fields'}),400

    conn=get_db_connection()
    if conn is None:    #checking if db is connected
        return jsonify({'error':'Filed to connect the DB'}),500

    cursor=conn.cursor(dictionary=True)
    try:
        query="select * from User where email=%s"    #query for finding the password of the email provided
        cursor.execute(query,(email,))
        user=cursor.fetchone()
        if user and check_password_hash(user['password'],password):   #checking if the password match
            return jsonify({
                'message':'Login Successful',
                'user_id':user['user_id'],
                'username':user['user_name']
            }),200
        else:
            return jsonify({'error':'Invalid email or passowrd'}),401   #error checking
    except mysql.connector.Error as err:
        return jsonify({'error':str(err)}),500   #error handling
    finally:
        cursor.close()
        conn.close()



#getting data for dashboard
@app.route("/api/dashboard_data", methods=['GET'])
def get_dashboard_data():
    user_id = request.args.get('user_id')         #getting data from table using user_id
    if not user_id:
        return jsonify({'error':'User ID is required'}), 400   #checking if data is recived
    conn=get_db_connection()
    if not conn:
        return jsonify({'error':'Connection to DB failed'}), 500   #checking if there is a problem with the connection
    cursor=conn.cursor(dictionary=True)
    try:
        query = "SELECT * FROM transaction WHERE user_id = %s ORDER BY date DESC"    #query for getting data from table
        cursor.execute(query,(user_id,))
        transactions=cursor.fetchall()
        total_income=sum(t['amount'] for t in transactions if t['type']=='Income')        #calculating income, spend, payable and recivable
        total_spend=sum(t['amount'] for t in transactions if t['type']=='Expense')
        total_payable=sum(t['amount'] for t in transactions if t['type']=='Payable' and t['status'] == 'Pending')
        total_receivable=sum(t['amount'] for t in transactions if t['type']=='Receivable' and t['status'] == 'Pending')
        current_balance=total_income-total_spend
        summary={                                    #a single row of the dta just fetched
            'current_balance':float(current_balance),
            'total_income':float(total_income),
            'total_spend':float(total_spend),
            'total_payable':float(total_payable),
            'total_receivable':float(total_receivable)
        }
        # Convert decimal and date objects for JSON
        for tx in transactions:
            tx['amount'] = float(tx['amount'])
            if isinstance(tx['date'], date):
                tx['date'] = tx['date'].isoformat()
        return jsonify({'summary':summary,'transactions':transactions})              #for showing in the website
    except mysql.connector.Error as err:
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
    category_name=data.get('category_name')
    description=data.get('description')
    person_involved=data.get('person_involved')
    if not all([user_id,tx_type,amount,category_name,description]):  #checking the data is recived
        return jsonify({'error':'Missing required fields'}),400
    status = 'Pending' if tx_type in ['Payable', 'Receivable'] else 'Completed'     #setting up status
    conn=get_db_connection()
    if not conn:
        return jsonify({'error':'Failed to connect DB'}),500        #checking the DB connection
    cursor=conn.cursor()
    try:
        query="insert into transaction(user_id,type,amount,category_name,description,date,person_involved,status) values (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query,(user_id,tx_type,amount,category_name,description,date.today(),person_involved,status))
        conn.commit()
        return jsonify({'message':'New transaction added'}), 201   #query for adding new record and posting it
    except mysql.connector.Error as err:
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
        return jsonify({'error':'Transaction _id is required'}),400    #checking if transaction id recived
    conn=get_db_connection()
    if not conn:
        return jsonify({'error':'Failed to connect to DB'}),500     #checking if db is connected
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM transaction WHERE transaction_id = %s", (transaction_id,))          #query to find the transaction from id
        payable_tx = cursor.fetchone()
        if not payable_tx:
            return jsonify({'error':'Payable transaction not found'}), 404      #error if the transaction is not found
        cursor.execute("UPDATE transaction SET status = 'Paid' WHERE transaction_id = %s", (transaction_id,))
        expense_description = f"Paid debt to {payable_tx['person_involved']}: {payable_tx['description']}"
        query = """
            INSERT INTO transaction (user_id, type, amount, category_name, description, date, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """         #setting the record that the record is payed
        cursor.execute(query, (payable_tx['user_id'], 'Expense', payable_tx['amount'], 'Debt Payment', expense_description, date.today(), 'Completed'))
        conn.commit()
        return jsonify({'message':'Debt maked as payed!'}),200       #giving the message that the debt is payed
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({'error':str(err)}), 500      #error handling
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    app.run(debug=True)






