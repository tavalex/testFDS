import json
import sqlite3
from contextlib import contextmanager

from config import DATABASE_PATH


@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                manufacturer TEXT DEFAULT '',
                supplier_info TEXT DEFAULT '',
                cas_numbers TEXT DEFAULT '[]',
                ghs_pictograms TEXT DEFAULT '',
                signal_word TEXT DEFAULT '',
                hazard_statements TEXT DEFAULT '[]',
                precautionary_statements TEXT DEFAULT '[]',
                supplemental_info TEXT DEFAULT '',
                ufi_code TEXT DEFAULT '',
                first_aid TEXT DEFAULT '',
                storage_handling TEXT DEFAULT '',
                net_quantity TEXT DEFAULT '',
                source_filename TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def insert_product(data):
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO products (product_name, manufacturer, supplier_info, "
            "cas_numbers, ghs_pictograms, signal_word, hazard_statements, "
            "precautionary_statements, supplemental_info, ufi_code, first_aid, "
            "storage_handling, net_quantity, source_filename) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                data.get("product_name", "Unknown"),
                data.get("manufacturer", ""),
                data.get("supplier_info", ""),
                json.dumps(data.get("cas_numbers", []), ensure_ascii=False),
                data.get("ghs_pictograms", ""),
                data.get("signal_word", ""),
                json.dumps(data.get("hazard_statements", []), ensure_ascii=False),
                json.dumps(data.get("precautionary_statements", []), ensure_ascii=False),
                data.get("supplemental_info", ""),
                data.get("ufi_code", ""),
                data.get("first_aid", ""),
                data.get("storage_handling", ""),
                data.get("net_quantity", ""),
                data.get("source_filename", ""),
            ),
        )
        conn.commit()
        return cursor.lastrowid


def get_product(product_id):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM products WHERE id = ?", (product_id,)
        ).fetchone()
        if row is None:
            return None
        return _row_to_dict(row)


def get_all_products():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM products ORDER BY updated_at DESC"
        ).fetchall()
        return [_row_to_dict(r) for r in rows]


def update_product(product_id, data):
    with get_db() as conn:
        cas = data.get("cas_numbers", "[]")
        if isinstance(cas, list):
            cas = json.dumps(cas, ensure_ascii=False)
        hs = data.get("hazard_statements", "[]")
        if isinstance(hs, list):
            hs = json.dumps(hs, ensure_ascii=False)
        ps = data.get("precautionary_statements", "[]")
        if isinstance(ps, list):
            ps = json.dumps(ps, ensure_ascii=False)
        conn.execute(
            "UPDATE products SET product_name=?, manufacturer=?, supplier_info=?, "
            "cas_numbers=?, ghs_pictograms=?, signal_word=?, hazard_statements=?, "
            "precautionary_statements=?, supplemental_info=?, ufi_code=?, "
            "first_aid=?, storage_handling=?, net_quantity=?, "
            "updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (
                data.get("product_name", ""),
                data.get("manufacturer", ""),
                data.get("supplier_info", ""),
                cas,
                data.get("ghs_pictograms", ""),
                data.get("signal_word", ""),
                hs,
                ps,
                data.get("supplemental_info", ""),
                data.get("ufi_code", ""),
                data.get("first_aid", ""),
                data.get("storage_handling", ""),
                data.get("net_quantity", ""),
                product_id,
            ),
        )
        conn.commit()


def delete_product(product_id):
    with get_db() as conn:
        conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()


def _row_to_dict(row):
    d = dict(row)
    for field in ("cas_numbers", "hazard_statements", "precautionary_statements"):
        try:
            d[field] = json.loads(d[field]) if d[field] else []
        except (json.JSONDecodeError, TypeError):
            d[field] = []
    if d.get("ghs_pictograms"):
        d["ghs_pictograms_list"] = [
            p.strip() for p in d["ghs_pictograms"].split(",") if p.strip()
        ]
    else:
        d["ghs_pictograms_list"] = []
    return d
