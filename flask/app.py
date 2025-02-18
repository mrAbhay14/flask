from flask import Flask, render_template, request, redirect, url_for, flash
# import pymysql
import mysql.connector
from datetime import datetime

app = Flask(__name__)
# app.secret_key = "supersecretkey"

# Database connection function
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="Abhay143.mysql.pythonanywhere-services.com",
            user="Abhay143",
            password="abhay-is-good",
            database="Abhay143$waffle_credit",
            # cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

# Admin Page
@app.route('/admin', methods=['GET', 'POST'])
def admin_page():
    if request.method == 'POST':
        name = request.form['name']
        credits = int(request.form['credits'])
        action = request.form['action']
        
        conn = get_db_connection()
        if conn is None:
            return "Database connection failed"
        
        with conn.cursor() as cursor:
            cursor.execute("SELECT credits FROM customers WHERE name = %s", (name,))
            result = cursor.fetchone()
            
            if result:
                if action == "add":
                    cursor.execute("UPDATE customers SET credits = credits + %s WHERE name = %s", (credits, name))
                    transaction_type = "Credit Added"
                elif action == "deduct":
                    if result['credits'] >= credits:
                        cursor.execute("UPDATE customers SET credits = credits - %s WHERE name = %s", (credits, name))
                        transaction_type = "Credit Deducted"
                    else:
                        flash("Not enough credits to deduct!", "danger")
                        return redirect(url_for('admin_page'))
                
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute("INSERT INTO transactions (name, amount, type, timestamp) VALUES (%s, %s, %s, %s)",
                               (name, credits, transaction_type, timestamp))
                
                conn.commit()
                flash("Transaction successful!", "success")
            else:
                flash("User not found!", "danger")
        
        conn.close()
    
    return render_template('admin.html')

# Greeting Page
@app.route('/greeting')
def greeting():
    name = request.args.get('name')
    credits = request.args.get('credits')
    return render_template('greeting.html', name=name, credits=credits)

# User Page
@app.route('/user', methods=['GET', 'POST'])
def user_page():
    if request.method == 'POST':
        name = request.form['name']
        
        conn = get_db_connection()
        if conn is None:
            return "Database connection failed"
        
        with conn.cursor() as cursor:
            cursor.execute("SELECT credits FROM customers WHERE name = %s", (name,))
            result = cursor.fetchone()
        
        conn.close()
        
        if result:
            credits = result['credits']
            return redirect(url_for('greeting', name=name, credits=credits))
        else:
            flash("User not found!", "danger")
            return redirect(url_for('user_page'))
    
    return render_template('user.html')

# View Users Page
@app.route('/users')
def view_users():
    conn = get_db_connection()
    if conn is None:
        return "Database connection failed"
    
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM customers")
        users = cursor.fetchall()
    
    conn.close()
    return render_template('view_users.html', users=users)

# Transactions Page
@app.route('/transactions/<string:name>')
def transaction_history(name):
    conn = get_db_connection()
    if conn is None:
        return "Database connection failed"
    
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM transactions WHERE name = %s ORDER BY timestamp DESC", (name,))
        transactions = cursor.fetchall()
    
    conn.close()
    return render_template('transactions.html', transactions=transactions, name=name)

# Delete User
@app.route('/admin/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    conn = get_db_connection()
    if conn is None:
        return "Database connection failed"
    
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM customers WHERE id = %s", (user_id,))
        conn.commit()
    
    conn.close()
    flash("User deleted successfully!", "success")
    return redirect(url_for('view_users'))

if __name__ == "__main__":
    app.run(debug=True)
