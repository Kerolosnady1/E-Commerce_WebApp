import sqlite3

db_path = 'db.sqlite3'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='core_securitylog';")
table_exists = cursor.fetchone() is not None

print("Table exists:", table_exists)

if table_exists:
    # Count records
    cursor.execute("SELECT COUNT(*) FROM core_securitylog;")
    count = cursor.fetchone()[0]
    print(f"Total records: {count}")
    
    if count > 0:
        # Get last 5 records
        cursor.execute("""
            SELECT id, username, action_type, status, timestamp 
            FROM core_securitylog 
            ORDER BY timestamp DESC 
            LIMIT 5
        """)
        
        print("\nLast 5 records:")
        for row in cursor.fetchall():
            print(f"  ID: {row[0]}, User: {row[1]}, Action: {row[2]}, Status: {row[3]}, Time: {row[4]}")
    else:
        print("No records found (table is empty)")

conn.close()
