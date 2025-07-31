#imports
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash



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
    return "<h1>Dashboard Page</h1><p>page under construction!</p>"   #update this to render the actual dashboard template when ready
    # Uncomment the line below when the dashboard template is ready 
    # return render_template("dashboard.html")
    
    
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

if __name__ == "__main__":
    app.run(debug=True)