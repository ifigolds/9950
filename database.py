import sqlite3

DB_NAME = "warehouse.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        quantity REAL NOT NULL,
        unit TEXT NOT NULL,
        location TEXT NOT NULL,
        minimum REAL NOT NULL DEFAULT 0,
        notes TEXT DEFAULT ''
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def add_log(action):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO logs (action) VALUES (?)", (action,))
    conn.commit()
    conn.close()


def seed_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM inventory")
    count = cursor.fetchone()["count"]

    seeded = False

    if count == 0:
        items = [
            ("חלב", 10, "ליטר", "מקרר 1", 5, ""),
            ("טונה", 2, "קופסאות", "ארון יבש", 5, ""),
            ("ביצים", 30, "יחידות", "מקרר 2", 10, ""),
        ]

        cursor.executemany("""
        INSERT INTO inventory (name, quantity, unit, location, minimum, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """, items)

        seeded = True

    conn.commit()
    conn.close()

    if seeded:
        add_log("נוצרו נתוני התחלה")

def get_all_inventory():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, name, quantity, unit, location, minimum, notes
    FROM inventory
    ORDER BY id DESC
    """)

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_low_stock():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, name, quantity, unit, location, minimum, notes
    FROM inventory
    WHERE quantity <= minimum
    ORDER BY id DESC
    """)

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_logs(limit=10):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, action, created_at
    FROM logs
    ORDER BY id DESC
    LIMIT ?
    """, (limit,))

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def add_product(name, quantity, unit, location, minimum, notes):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO inventory (name, quantity, unit, location, minimum, notes)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (name, quantity, unit, location, minimum, notes))

    conn.commit()
    conn.close()

    add_log(f"נוסף מוצר: {name}, כמות {quantity} {unit}, מיקום {location}")


def use_product(product_id, used_quantity):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, name, quantity, unit
    FROM inventory
    WHERE id = ?
    """, (product_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return False, "המוצר לא נמצא"

    current_quantity = float(row["quantity"])
    new_quantity = current_quantity - float(used_quantity)

    if new_quantity < 0:
        conn.close()
        return False, "אין מספיק מלאי"

    cursor.execute("""
    UPDATE inventory
    SET quantity = ?
    WHERE id = ?
    """, (new_quantity, product_id))

    conn.commit()
    conn.close()

    add_log(f"שימוש במוצר: {row['name']}, ירדו {used_quantity} {row['unit']}")
    return True, "ok"


def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT name FROM inventory WHERE id = ?
    """, (product_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return False

    product_name = row["name"]

    cursor.execute("""
    DELETE FROM inventory
    WHERE id = ?
    """, (product_id,))

    conn.commit()
    conn.close()

    add_log(f"נמחק מוצר: {product_name}")
    return True