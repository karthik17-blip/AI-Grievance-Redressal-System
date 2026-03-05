import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import os

# Load embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

DB_PATH = os.path.join(os.path.dirname(__file__), "../complaints.db")
SIMILARITY_THRESHOLD = 0.80


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS grievances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            embedding TEXT
        )
    """)
    conn.commit()
    conn.close()


def check_duplicate(new_text: str):
    init_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    new_embedding = embedder.encode([new_text])[0]

    cursor.execute("SELECT id, text, embedding FROM grievances")
    rows = cursor.fetchall()

    if len(rows) == 0:
        cursor.execute(
            "INSERT INTO grievances (text, embedding) VALUES (?, ?)",
            (new_text, json.dumps(new_embedding.tolist()))
        )
        conn.commit()
        conn.close()

        return {
            "is_duplicate": False,
            "duplicate_of": None,
            "similarity_score": None
        }

    stored_embeddings = []
    stored_texts = []
    stored_ids = []

    for row in rows:
        stored_ids.append(row[0])
        stored_texts.append(row[1])
        stored_embeddings.append(np.array(json.loads(row[2])))

    similarities = cosine_similarity(
        [new_embedding],
        stored_embeddings
    )[0]

    max_sim = float(np.max(similarities))
    max_index = int(np.argmax(similarities))

    if max_sim > SIMILARITY_THRESHOLD:
        conn.close()
        return {
            "is_duplicate": True,
            "duplicate_of": stored_texts[max_index],
            "similarity_score": round(max_sim, 4)
        }

    # If not duplicate, store it
    cursor.execute(
        "INSERT INTO grievances (text, embedding) VALUES (?, ?)",
        (new_text, json.dumps(new_embedding.tolist()))
    )
    conn.commit()
    conn.close()

    return {
        "is_duplicate": False,
        "duplicate_of": None,
        "similarity_score": round(max_sim, 4)
    }
