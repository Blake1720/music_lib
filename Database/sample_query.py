'''
This file prints insights from the music_app database: totals, top artists/albums, etc.
'''
import sqlite3

def print_database_insights(db_path="music_app.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("\n=== 🎵 Music Database Insights ===\n")

    try:
        # 1. Total counts
        cursor.execute("SELECT COUNT(*) FROM Artist;")
        artist_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Album;")
        album_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Song;")
        song_count = cursor.fetchone()[0]

        print(f"👤 Total Artists: {artist_count}")
        print(f"💿 Total Albums: {album_count}")
        print(f"🎶 Total Songs: {song_count}")
        print("-" * 60)

        # 2. Songs with analyzed features
        print("📊 Songs with Analyzed Features:")
        cursor.execute("SELECT COUNT(*) FROM Song WHERE duration IS NOT NULL;")
        analyzed_count = cursor.fetchone()[0]
        print(f"🔬 Analyzed Songs: {analyzed_count}")
        print("-" * 60)

        # 3. Top 5 artists with most albums
        print("🏆 Top 5 Artists with Most Albums:")
        cursor.execute("""
            SELECT Artist.name, COUNT(Album.album_id) AS album_count
            FROM Artist
            JOIN Album ON Artist.artist_id = Album.artist_id
            GROUP BY Artist.artist_id
            ORDER BY album_count DESC
            LIMIT 5;
        """)
        for name, count in cursor.fetchall():
            print(f"{name}: {count} album(s)")
        print("-" * 60)

        # 4. Top 5 albums with most songs
        print("📚 Top 5 Albums with Most Songs:")
        cursor.execute("""
            SELECT Album.name, Artist.name, COUNT(Song.song_id) AS song_count
            FROM Album
            JOIN Song ON Album.album_id = Song.album_id
            JOIN Artist ON Album.artist_id = Artist.artist_id
            GROUP BY Album.album_id
            ORDER BY song_count DESC
            LIMIT 5;
        """)
        for album, artist, count in cursor.fetchall():
            print(f"{album} by {artist}: {count} song(s)")
        print("-" * 60)

        # 5. Albums with no songs
        print("🛑 Albums with No Songs:")
        cursor.execute("""
            SELECT Album.name, Artist.name
            FROM Album
            JOIN Artist ON Album.artist_id = Artist.artist_id
            LEFT JOIN Song ON Album.album_id = Song.album_id
            WHERE Song.song_id IS NULL
            LIMIT 5;
        """)
        rows = cursor.fetchall()
        if not rows:
            print("✅ All albums have at least one song.")
        else:
            for album, artist in rows:
                print(f"{album} by {artist}")
        print("-" * 60)

        # 6. Artists with no albums
        print("🎤 Artists with No Albums:")
        cursor.execute("""
            SELECT name FROM Artist
            WHERE artist_id NOT IN (
                SELECT DISTINCT artist_id FROM Album
            )
            LIMIT 5;
        """)
        rows = cursor.fetchall()
        if not rows:
            print("✅ All artists have at least one album.")
        else:
            for (artist,) in rows:
                print(artist)
        print("-" * 60)

        # 7. Most recently analyzed song
        print("🎧 Most Recently Analyzed Song:")
        cursor.execute("""
            SELECT s.name, al.name, ar.name,
                   s.duration, s.tempo, s.spectral_centroid,
                   s.spectral_rolloff, s.spectral_contrast,
                   s.chroma_mean, s.chroma_std,
                   s.onset_strength, s.zero_crossing_rate, s.rms_energy
            FROM Song s
            JOIN Album al ON s.album_id = al.album_id
            JOIN Artist ar ON al.artist_id = ar.artist_id
            WHERE s.duration IS NOT NULL
            ORDER BY s.song_id DESC
            LIMIT 1;
        """)
        row = cursor.fetchone()
        if row:
            (song, album, artist,
             duration, tempo, centroid, rolloff, contrast,
             chroma_mean, chroma_std,
             onset_strength, zero_crossing, rms_energy) = row
            print(f"\n🎵 {song} by {artist} from '{album}':")
            print(f"   Duration: {duration:.2f}s")
            print(f"   Tempo: {tempo:.2f} BPM")
            print(f"   Spectral Centroid: {centroid:.2f}")
            print(f"   Spectral Rolloff: {rolloff:.2f}")
            print(f"   Spectral Contrast: {contrast:.2f}")
            print(f"   Chroma Mean: {chroma_mean:.2f}, Std: {chroma_std:.2f}")
            print(f"   Onset Strength: {onset_strength:.2f}")
            print(f"   Zero Crossing Rate: {zero_crossing:.4f}")
            print(f"   RMS Energy: {rms_energy:.6f}")
        else:
            print("No analyzed songs found.")
        print("-" * 60)

    except Exception as e:
        print(f"❌ Error querying database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print_database_insights()
