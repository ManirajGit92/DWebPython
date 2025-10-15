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
            CREATE TABLE IF NOT EXISTS Users (
                id SERIAL PRIMARY KEY,
                userName VARCHAR(255) NOT NULL,
                emailAddress TEXT NOT NULL,
                phoneNumber VARCHAR(15) NOT NULL,
                password VARCHAR(15) NOT NULL    
            )
        ''')
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Table 'users' is ready.")
    except Exception as e:
        print("❌ Error initializing database:", e)


# ----------------------------
# Pydantic Model
# ----------------------------
class Users(BaseModel):
    username: str
    emailaddress: str
    phonenumber:str
    password:str


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
@app.post("/users")
def create_users(item: Users):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("INSERT INTO Users (username, emailaddress,phonenumber,password) VALUES (%s, %s,%s, %s) RETURNING id", (item.username, item.emailaddress , item.phonenumber,item.password))
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return {"message": "Users added successfully", "id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 2️⃣ READ (All Records)
@app.get("/users")
def get_all_users():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM users ORDER BY id ASC")
        records = cur.fetchall()
        cur.close()
        conn.close()
        return [dict(record) for record in records]
        #  # Convert all keys in each record to camelCase
        # result = []
        # for record in records:
        #     camel_case_record = {to_camel_case(k): v for k, v in dict(record).items()}
        #     result.append(camel_case_record)
        # return result
        # 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 3️⃣ READ (Single Record)
@app.get("/users/{user_id}")
def get_users(user_id: int):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        record = cur.fetchone()
        cur.close()
        conn.close()
        if record:
            return dict(record)
        else:
            raise HTTPException(status_code=404, detail="Users not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 4️⃣ UPDATE
@app.put("/users/{user_id}")
def update_users(user_id: int, item: Users):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("UPDATE users SET username = %s, emailAddress = %s,phonenumber = %s,password = %s WHERE id = %s RETURNING id",
                    (item.username, item.emailaddress,item.phonenumber,item.password, user_id))
        updated = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if updated:
            return {"message": "Users updated successfully", "id": user_id}
        else:
            raise HTTPException(status_code=404, detail="Users not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 5️⃣ DELETE
@app.delete("/users/{user_id}")
def delete_users(user_id: int):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE id = %s RETURNING id", (user_id,))
        deleted = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if deleted:
            return {"message": "Users deleted successfully", "id": user_id}
        else:
            raise HTTPException(status_code=404, detail="Users not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def to_camel_case(snake_str):
    """Convert snake_case or lowercase to camelCase."""
    parts = re.split(r'_| ', snake_str)
    if not parts:
        return snake_str
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])
# ----------------------------
# Run the Server
# ----------------------------
if __name__ == "__main__":
    init_db()  # Ensure table exists
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
