'''
This file is used to print the contents of the database.
'''
import sqlite3

def print_database_contents(db_path="music_app.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("\n=== Database Contents ===\n")
        
        for table in tables:
            table_name = table[0]
            print(f"\n--- Table: {table_name} ---")
            
            # Get column names
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            print("Columns:", ", ".join(column_names))
            
            # Get all rows
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()
            
            if not rows:
                print("No data in this table")
            else:
                print("\nData:")
                for row in rows:
                    print(row)
            
            print("-" * 50)
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print_database_contents()
