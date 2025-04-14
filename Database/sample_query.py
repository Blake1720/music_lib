'''
This file is used to print all entries in the Album table with full attributes.
'''
import sqlite3

def print_all_albums(db_path="music_app.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("\n=== Full Contents of Album Table ===\n")

    try:
        # Get column names from Album table
        cursor.execute("PRAGMA table_info(Album);")
        columns = [col[1] for col in cursor.fetchall()]
        print("Columns:", ", ".join(columns))
        print("-" * 80)

        # Fetch all rows from Album table
        cursor.execute("SELECT * FROM Album;")
        rows = cursor.fetchall()

        if not rows:
            print("No albums found in the Album table.")
        else:
            for row in rows:
                for col, val in zip(columns, row):
                    print(f"{col}: {val}")
                print("-" * 80)

    except Exception as e:
        print(f"❌ Error reading Album table: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print_all_albums()
