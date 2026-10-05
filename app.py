import os
import boto3  # 💥 ADD THIS: AWS SDK to talk to Parameter Store
from flask import Flask, jsonify, render_template, request
import pymysql

app = Flask(__name__)

def get_db_connection():
    """
    Fetches the dynamic RDS hostname from AWS SSM Parameter Store 
    and establishes a secure connection.
    """
    # Configure SSL parameters to match your CLI --ssl-mode flags
    ssl_config = {
        'ca': './global-bundle.pem',
        'check_hostname': True  
    }

    try:
        # 1. Initialize the AWS SSM client
        # It automatically resolves credentials using the EC2 instance's IAM role!
        ssm_client = boto3.client('ssm', region_name='eu-central-1')
        
        # 2. Fetch the parameter we created with Terraform
        print("Fetching RDS host endpoint from AWS Parameter Store...")
        response = ssm_client.get_parameter(
            Name='/dev/db/host',
            WithDecryption=False  # Set to True if you ever upgrade this to a SecureString
        )
        
        # Extract the string value
        rds_host = response['Parameter']['Value']
        print(f"Successfully retrieved RDS host!")

        # 3. Establish the PyMySQL connection using the fetched host
        connection = pymysql.connect(
            host=rds_host,                                           
            port=3306,                                               
            user='dbuser',                                           
            password='dbpassword',                                   
            db='devprojdb',                                          
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            ssl=ssl_config                                           
        )
        return connection

    except Exception as e:
        print(f"🚨 DATABASE OR AWS PARAMETER ERROR: {e}")
        return None

@app.route('/health')
def health():
    return "Up & Running"

@app.route('/create_table')
def create_table():
    connection = get_db_connection()
    if not connection:
        return "Database connection failed", 500
    cursor = connection.cursor()
    create_table_query = """
        CREATE TABLE IF NOT EXISTS example_table (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        )
    """
    cursor.execute(create_table_query)
    connection.commit()
    connection.close()
    return "Table created successfully"

@app.route('/insert_record', methods=['POST'])
def insert_record():
    name = request.json['name']
    connection = get_db_connection()
    if not connection:
        return "Database connection failed", 500
    cursor = connection.cursor()
    insert_query = "INSERT INTO example_table (name) VALUES (%s)"
    cursor.execute(insert_query, (name,))
    connection.commit()
    connection.close()
    return "Record inserted successfully"

@app.route('/data')
def data():
    connection = get_db_connection()
    if not connection:
        return "Database connection failed", 500
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM example_table')
    result = cursor.fetchall()
    connection.close()
    return jsonify(result)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

