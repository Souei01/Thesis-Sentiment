"""Reset the MariaDB database for fresh migrations."""
import pymysql

try:
    # Connect to MySQL (not a specific database)
    connection = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='',
        port=3306
    )
    
    cursor = connection.cursor()
    
    # Drop and recreate database
    print("Dropping database sentiment_db if it exists...")
    cursor.execute("DROP DATABASE IF EXISTS sentiment_db")
    
    print("Creating fresh sentiment_db database...")
    cursor.execute("CREATE DATABASE sentiment_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    
    print("✓ Database reset successfully!")
    print("Now run: python server\\manage.py migrate")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"Error: {e}")
    print("\nMake sure XAMPP MySQL/MariaDB is running!")
