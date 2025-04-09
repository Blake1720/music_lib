import sqlite3

def query_music_app_db(db_path="databases/music_app.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        query = """  # Add your SQL query here
        SELECT * FROM Song WHERE popularity > 75
        """
        cursor.execute(query)
        results = cursor.fetchall()
        for row in results:
            print(row)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    query_music_app_db()
