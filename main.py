from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import psycopg2.extras
import uvicorn
from typing import Any,Dict,List
import json
# ----------------------------
# Database Configuration
# ----------------------------
# DB_CONFIG = {
#     "host": "localhost",
#     "port": 5432,
#     "dbname": "DynamicWebsite",
#     "user": "postgres",
#     "password": "Vinsa$POS$ool"
# }
DB_CONFIG = {
    "dbname":"DwebDB",
    "user":"neondb_owner",
    "password":"npg_ujTCihN6Yr0H",
    "host":"ep-long-tree-a15ne54g-pooler.ap-southeast-1.aws.neon.tech",
    "sslmode":"require"
}
# psql 'postgresql://neondb_owner:npg_ujTCihN6Yr0H@ep-long-tree-a15ne54g-pooler.ap-southeast-1.aws.neon.tech/DwebDB?sslmode=require&channel_binding=require'
# DB_CONFIG ="postgresql://neondb_owner:npg_ujTCihN6Yr0H@ep-long-tree-a15ne54g-pooler.ap-southeast-1.aws.neon.tech/DwebDB?sslmode=require&channel_binding=require"
# ----------------------------
# Create Table (if not exists)
# ----------------------------
def init_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        print(cur.fetchone())
        cur.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                id SERIAL PRIMARY KEY,
                userName VARCHAR(255) NOT NULL,
                emailAddress TEXT NOT NULL,
                phoneNumber VARCHAR(15) NOT NULL,
                password VARCHAR(15) NOT NULL    
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS Products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                category VARCHAR(255) NOT NULL,    
                price DECIMAL(10,2) NOT NULL,
                quantity DECIMAL(10,2) NOT NULL DEFAULT 0,
                rating SMALLINT DEFAULT NULL,
                descripton TEXT NOT NULL,
                salescount DECIMAL(10,2) DEFAULT 0, 
                spec jsonb DEFAULT '{}',
                moreinfo jsonb DEFAULT '{}',
                usersInfo jsonb DEFAULT '{}'                
            )
        ''')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_products_category ON Products(category);')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_products_name ON Products(name);')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS webPage (
                id SERIAL PRIMARY KEY,
                webPageId VARCHAR(255) NOT NULL UNIQUE,    
                home jsonb DEFAULT '{}',
                aboutus jsonb DEFAULT '{}',
                products jsonb DEFAULT '{}'                
            )
        ''')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_webPage_webPageId ON webPage(webPageId);')
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

class Webpage(BaseModel):
    webpageid: str
    home: List[Any]
    aboutus: List[Any]
    products: List[Any]
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
@app.get("/")
def root():
    return {"message": "Welcome to FastAPI on Render!"}
# Users
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


# 2️⃣ READ (All User Records)
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
    
# Webpage CRUD operations   
# 2️⃣ READ (All Webpage Records)
@app.get("/webpage")
def get_all_users():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM webpage ORDER BY id ASC")
        records = cur.fetchall()
        cur.close()
        conn.close()
        return [dict(record) for record in records]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 3️⃣ READ (Single Record)
@app.get("/webpage/{id}")
def get_users(id: int):
    try:
        print("id===>",id)
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM webpage WHERE id = %s", (id,))
        print("cur===>",cur)
        record = cur.fetchone()
        cur.close()
        conn.close()
        if record:
            return dict(record)
        else:
            raise HTTPException(status_code=404, detail="webpage not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
@app.post("/webpage")
def create_webpage(item: Webpage):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("INSERT INTO Webpage (webpageid, home, aboutus, products) VALUES (%s, %s::jsonb, %s::jsonb, %s::jsonb) RETURNING id",('webpage1',item.home,item.aboutus,item.products))
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return {"message": "Users added successfully", "id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 4️⃣ UPDATE
@app.put("/webpage/{id}")
def update_webpage(id: int, data: Webpage):
    try:
        # print('data==>',data)
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("UPDATE Webpage SET webpageid = %s, home = %s::jsonb, aboutus = %s::jsonb,products = %s::jsonb WHERE id = %s RETURNING id",
                    (data.webpageid,json.dumps(data.home),json.dumps(data.aboutus),json.dumps(data.products),id))
        updated = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if updated:
            return {"message": "Webpage updated successfully", "id": id}
        else:
            raise HTTPException(status_code=404, detail="Webpage not found")
    except Exception as e:
     import traceback
     print("❌ ERROR:", e)
     traceback.print_exc()
     raise HTTPException(status_code=500, detail=str(e))
    

# Products CRUD operations
@app.post("/products")
def create_users(item: Any):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("INSERT INTO Products (name, category, price, quantity, rating, description, salescount, spec, moreinfo, usersinfo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb) RETURNING id",(item.name,item.category,item.price,item.quantity,item.rating,item.description,item.salescount,item.spec,item.moreinfo,item.usersinfo))
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return {"message": "Users added successfully", "id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# help functions
def to_camel_case(snake_str):
    """Convert snake_case or lowercase to camelCase."""
    parts = re.split(r'_| ', snake_str)
    if not parts:
        return snake_str
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])
        #  # Convert all keys in each record to camelCase
        # result = []
        # for record in records:
        #     camel_case_record = {to_camel_case(k): v for k, v in dict(record).items()}
        #     result.append(camel_case_record)
        # return result
        # 

# ----------------------------
# Run the Server
# ----------------------------
if __name__ == "__main__":
    init_db()  # Ensure table exists
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
