import os
import sqlite3
import sys

# Résout le chemin de la base de données relative au dossier du script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "analytics.db")

# Si non trouvé, cherche dans le dossier courant
if not os.path.exists(db_path) and os.path.exists("analytics.db"):
    db_path = "analytics.db"

print(f"Connexion à la base SQLite : {db_path}")
con = sqlite3.connect(db_path)
cur = con.cursor()

columns_to_add = [
    ("users", "role", "VARCHAR(20) DEFAULT 'admin' NOT NULL"),
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

# Met à jour le premier admin en superadmin
try:
    cur.execute("UPDATE users SET role = 'superadmin' WHERE username = 'admin'")
    print("✓ Compte 'admin' défini en superadmin")
except Exception as e:
    print("ℹ Mise à jour rôle admin :", e)

con.commit()
con.close()
print("Migration terminée avec succès.")
