'''
This script removes:
1. Albums with no songs
2. Artists with no albums
'''
import sqlite3

def cleanup_orphaned_data(db_path="music_app.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("\n🧹 Cleaning up orphaned albums and artists...\n")

        # Delete albums with no songs
        cursor.execute("""
            DELETE FROM Album
            WHERE album_id NOT IN (
                SELECT DISTINCT album_id FROM Song
            );
        """)
        deleted_albums = cursor.rowcount
        print(f"🗑️ Deleted {deleted_albums} album(s) with no songs.")

        # Delete artists with no albums
        cursor.execute("""
            DELETE FROM Artist
            WHERE artist_id NOT IN (
                SELECT DISTINCT artist_id FROM Album
            );
        """)
        deleted_artists = cursor.rowcount
        print(f"🗑️ Deleted {deleted_artists} artist(s) with no albums.")

        conn.commit()
        print("\n✅ Cleanup complete.\n")

    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    cleanup_orphaned_data()