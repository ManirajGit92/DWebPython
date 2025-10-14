from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import psycopg2.extras
import uvicorn

# ----------------------------
# Database Configuration
# ----------------------------
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "DynamicWebsite",
    "user": "postgres",
    "password": "Vinsa$POS$ool"
}

# ----------------------------
# Create Table (if not exists)
# ----------------------------
def init_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS content (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                body TEXT NOT NULL
            )
        ''')
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Table 'content' is ready.")
    except Exception as e:
        print("❌ Error initializing database:", e)


# ----------------------------
# Pydantic Model
# ----------------------------
class Content(BaseModel):
    title: str
    body: str


# ----------------------------
# FastAPI App
# ----------------------------
app = FastAPI()

# Allow frontend (Angular) to access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can specify ["http://localhost:4200"] later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------
# CRUD API Endpoints
# ----------------------------

# 1️⃣ CREATE
@app.post("/content")
def create_content(item: Content):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("INSERT INTO content (title, body) VALUES (%s, %s) RETURNING id", (item.title, item.body))
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return {"message": "Content added successfully", "id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 2️⃣ READ (All Records)
@app.get("/content")
def get_all_content():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM content ORDER BY id ASC")
        records = cur.fetchall()
        cur.close()
        conn.close()
        return [dict(record) for record in records]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 3️⃣ READ (Single Record)
@app.get("/content/{content_id}")
def get_content(content_id: int):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM content WHERE id = %s", (content_id,))
        record = cur.fetchone()
        cur.close()
        conn.close()
        if record:
            return dict(record)
        else:
            raise HTTPException(status_code=404, detail="Content not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 4️⃣ UPDATE
@app.put("/content/{content_id}")
def update_content(content_id: int, item: Content):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("UPDATE content SET title = %s, body = %s WHERE id = %s RETURNING id",
                    (item.title, item.body, content_id))
        updated = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if updated:
            return {"message": "Content updated successfully", "id": content_id}
        else:
            raise HTTPException(status_code=404, detail="Content not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 5️⃣ DELETE
@app.delete("/content/{content_id}")
def delete_content(content_id: int):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("DELETE FROM content WHERE id = %s RETURNING id", (content_id,))
        deleted = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if deleted:
            return {"message": "Content deleted successfully", "id": content_id}
        else:
            raise HTTPException(status_code=404, detail="Content not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------
# Run the Server
# ----------------------------
if __name__ == "__main__":
    init_db()  # Ensure table exists
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
