'''
This script deletes all songs from the database that do not have analyzed features (i.e., duration is NULL).
'''
import sqlite3

def delete_unanalyzed_songs(db_path="music_app.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("\n🧹 Deleting songs with no analyzed data (NULL duration)...")

        # Count how many will be deleted
        cursor.execute("SELECT COUNT(*) FROM Song WHERE duration IS NULL;")
        count = cursor.fetchone()[0]
        print(f"Found {count} song(s) to delete.")

        if count == 0:
            print("✅ No unanalyzed songs to delete.")
        else:
            cursor.execute("DELETE FROM Song WHERE duration IS NULL;")
            conn.commit()
            print(f"🗑️ Deleted {count} unanalyzed song(s).")

    except Exception as e:
        print(f"❌ Error deleting unanalyzed songs: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    delete_unanalyzed_songs()