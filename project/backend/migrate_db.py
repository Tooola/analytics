import os
import sqlite3
import sys

# Try multiple locations to find analytics.db
candidate_dirs = [
    os.path.dirname(os.path.abspath(__file__)),
    os.getcwd(),
    "/home/jolasun/api.ainalytics.j-ola-sun.com",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "project", "backend"),
]

db_path = None
for d in candidate_dirs:
    p = os.path.join(d, "analytics.db")
    if os.path.exists(p):
        db_path = p
        break

if not db_path:
    db_path = "/home/jolasun/api.ainalytics.j-ola-sun.com/analytics.db"

print(f"Using database: {db_path}")
con = sqlite3.connect(db_path)
cur = con.cursor()

# Ensure users table has all required columns
columns_to_add = [
    ("users", "role", "VARCHAR(20) DEFAULT 'superadmin' NOT NULL"),
    ("users", "created_by", "VARCHAR(36)"),
    ("insights", "evidence", "TEXT"),
    ("analysis_runs", "operator_username", "VARCHAR(100)")
]

for table, col, col_type in columns_to_add:
    try:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
        print(f"✓ Colonne ajoutée : {table}.{col}")
    except Exception as e:
        print(f"ℹ Colonne déjà présente ou ignorée ({table}.{col}): {e}")

# Promote ALL existing users to superadmin so the current admin user gets full rights
try:
    cur.execute("UPDATE users SET role = 'superadmin'")
    print("✓ Tous les utilisateurs existants ont été promus au rôle 'superadmin' !")
except Exception as e:
    print(f"ℹ Mise à jour rôle : {e}")

# Display users
try:
    cur.execute("SELECT id, username, role, is_active FROM users")
    rows = cur.fetchall()
    print("\n--- Liste des Utilisateurs dans la Base ---")
    for r in rows:
        print(f"👤 Username: {r[1]} | Rôle: {r[2]} | Actif: {r[3]}")
    print("------------------------------------------")
except Exception as e:
    print("ℹ Erreur lecture users:", e)

con.commit()
con.close()
print("\nMigration terminée avec succès.")
