import sqlite3

# Connect to database
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("\n" + "="*50)
print("DATABASE TABLES")
print("="*50 + "\n")

for i, table in enumerate(tables, 1):
    table_name = table[0]
    print(f"{i}. {table_name}")
    
    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"   Rows: {count}")
    
    # Get columns
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    print(f"   Columns: {', '.join([col[1] for col in columns])}")
    print()

conn.close()
