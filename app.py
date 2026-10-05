from flask import Flask, jsonify, render_template, request
import pymysql

app = Flask(__name__)


def get_db_connection():
    # Define the SSL configuration matching your CLI flags
    ssl_config = {
        'ca': './global-bundle.pem',
        'check_hostname': True  # Enforces VERIFY_IDENTITY behavior
    }

    connection = pymysql.connect(
        host='mydb.c3qws26ka630.eu-central-1.rds.amazonaws.com', # Updated RDS Host
        port=3306,                                               # Added Port
        user='dbuser',                                           # Your database user
        password='dbpassword',                                   # Replace with your actual password
        db='devprojdb',                                          # Replace with your actual database name
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        ssl=ssl_config                                           # Added SSL configuration
    )

    return connection


@app.route('/health')
def health():
    return "Up & Running"

@app.route('/create_table')
def create_table():
    connection = get_db_connection()
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
    cursor = connection.cursor()
    insert_query = "INSERT INTO example_table (name) VALUES (%s)"
    cursor.execute(insert_query, (name,))
    connection.commit()
    connection.close()
    return "Record inserted successfully"

@app.route('/data')
def data():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM example_table')
    result = cursor.fetchall()
    connection.close()
    return jsonify(result)

# UI route
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
