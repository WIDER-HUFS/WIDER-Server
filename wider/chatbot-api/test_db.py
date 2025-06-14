import os
import sys
import mysql.connector
from dotenv import load_dotenv

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

# Database configuration
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE')
}

def test_db_connection():
    try:
        # Connect to database
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        print("Database connection successful!")
        
        # Create cursor
        cursor = conn.cursor(dictionary=True)
        
        # Test session ID
        session_id = 'f4d36e33-d1bb-437a-b7c5-dc2499d8af4b'
        
        # Get session info
        cursor.execute('SELECT * FROM session_logs WHERE session_id = %s', (session_id,))
        session_info = cursor.fetchone()
        print("\nSession Info:", session_info)
        
        # Get conversation history
        cursor.execute('SELECT * FROM conversation_history WHERE session_id = %s ORDER BY timestamp ASC', (session_id,))
        messages = cursor.fetchall()
        print("\nMessages:", messages)
        
        # Close cursor and connection
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    test_db_connection() 