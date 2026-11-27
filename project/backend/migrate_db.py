import sqlite3

con = sqlite3.connect('C:/Users/fayom/Downloads/analytics/project/backend/analytics.db')
cur = con.cursor()

columns_to_add = [
    ("users", "role", "VARCHAR(20) DEFAULT 'admin' NOT NULL"),
    ("users", "created_by", "VARCHAR(36)"),
    ("insights", "evidence", "TEXT")
]

for table, col, col_type in columns_to_add:
    try:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
        print(f"Added {col} to {table}")
    except Exception as e:
        print(f"{table}.{col}: {e}")

# Update first admin to superadmin
try:
    cur.execute("UPDATE users SET role = 'superadmin' WHERE username = 'admin'")
    print("Updated admin to superadmin")
except Exception as e:
    print("Error updating admin role:", e)

con.commit()
con.close()
print("Migration script finished successfully.")
