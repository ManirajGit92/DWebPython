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
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "DynamicWebsite",
    "user": "postgres",
    "password": "Vinsa$POS$ool"
}
# DB_CONFIG = {
#     "dbname":"DwebDB",
#     "user":"neondb_owner",
#     "password":"npg_ujTCihN6Yr0H",
#     "host":"ep-long-tree-a15ne54g-pooler.ap-southeast-1.aws.neon.tech",
#     "sslmode":"require"
# }
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
        # cur.execute('''
        #     CREATE TABLE IF NOT EXISTS Users (
        #         id SERIAL PRIMARY KEY,
        #         userName VARCHAR(255) NOT NULL,
        #         emailAddress TEXT NOT NULL,
        #         phoneNumber VARCHAR(15) NOT NULL,
        #         password VARCHAR(15) NOT NULL    
        #     )
        # ''')
        # cur.execute('''
        #     CREATE TABLE IF NOT EXISTS Products (
        #         id SERIAL PRIMARY KEY,
        #         name VARCHAR(255) NOT NULL,
        #         category VARCHAR(255) NOT NULL,    
        #         price DECIMAL(10,2) NOT NULL,
        #         quantity DECIMAL(10,2) NOT NULL DEFAULT 0,
        #         rating SMALLINT DEFAULT NULL,
        #         descripton TEXT NOT NULL,
        #         salescount DECIMAL(10,2) DEFAULT 0, 
        #         spec jsonb DEFAULT '{}',
        #         moreinfo jsonb DEFAULT '{}',
        #         usersInfo jsonb DEFAULT '{}'                
        #     )
        # ''')
        # cur.execute('CREATE INDEX IF NOT EXISTS idx_products_category ON Products(category);')
        # cur.execute('CREATE INDEX IF NOT EXISTS idx_products_name ON Products(name);')

        # cur.execute('''
        #     CREATE TABLE IF NOT EXISTS webPage (
        #         id SERIAL PRIMARY KEY,
        #         webPageId VARCHAR(255) NOT NULL UNIQUE,
        #         header jsonb DEFAULT '{}'     
        #         home jsonb DEFAULT '{}',
        #         aboutus jsonb DEFAULT '{}',
        #         products jsonb DEFAULT '{}',
        #         contactus jsonb DEFAULT '{}',
        #         footer jsonb DEFAULT '{}',
        #         settings jsonb DEFAULT '{}'
                                   
        #     )
        # ''')
        # cur.execute('CREATE INDEX IF NOT EXISTS idx_webPage_webPageId ON webPage(webPageId);')
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
    header: List[Any]
    home: List[Any]
    aboutus: List[Any]
    products: List[Any]
    contactus: List[Any]
    footer: List[Any]
    settings: Dict[str, Any]

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
def get_all_webpageData():
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
def get_webpageData(id: int):
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
        cur.execute("UPDATE Webpage SET webpageid = %s,header = %s::jsonb,home = %s::jsonb, aboutus = %s::jsonb,products = %s::jsonb,contactus = %s::jsonb,footer = %s::jsonb,settings = %s::jsonb WHERE id = %s RETURNING id",
                    (data.webpageid,json.dumps(data.header),json.dumps(data.home),json.dumps(data.aboutus),json.dumps(data.products),json.dumps(data.contactus),json.dumps(data.footer),json.dumps(data.settings),id))
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
def create_products(item: Any):
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
    
# Reset webpage table
@app.get("/resetwebpage")
def reset_webpageTable():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        query = """
        INSERT INTO webPage (webPageId, header, home, aboutus, products, contactus, footer, settings)
        VALUES 
        (
            'webPage1',
            '[
                {"title":"Home","detail":"home","type":"scroll"},
                {"title":"Aboutus","detail":"about","type":"scroll"},
                {"title":"Products","detail":"services","type":"scroll"},
                {"title":"Contactus","detail":"contact","type":"scroll"},
                {"title":"Login","detail":"login","type":"navigate"},
                {"title":"Admin","detail":"admin","type":"navigate"}
            ]'::jsonb,
            '[
              {
                "image": "https://i.postimg.cc/RZ1mPhpJ/Army-Man.jpg",
                "title": "Innovate with Confidence",
                "detail": "We build cutting-edge web and AI solutions that help your business grow."
              },
              {
                "image": "https://i.postimg.cc/c1KrF7RB/World-Map.jpg",
                "title": "Design that Inspires",
                "detail": "Modern, responsive, and beautiful designs tailored for your brand."
              },
              {
                "image": "https://i.postimg.cc/Nfqfb3Gx/Indian-army-images-15.jpg",
                "title": "Scale Seamlessly",
                "detail": "Empowering your apps with performance, scalability, and great user experience."
              }
            ]'::jsonb,
            '[
              {
                "title": "Our Mission",
                "detail": "To deliver high-quality web solutions that empower businesses to grow and scale effectively."
              },
              {
                "title": "Our Vision",
                "detail": "To be a global leader in digital innovation and technology-driven transformation."
              },
              {
                "title": "Our Values",
                "detail": "Integrity, creativity, and collaboration form the core of everything we do."
              },
              {
                "title": "Our Approach",
                "detail": "We combine strategic thinking with modern tools to create efficient, user-focused products."
              }
            ]'::jsonb,
            '[
              { "title": "Web Development","image":"https://i.postimg.cc/hj1M6WWs/gun1.jpg" ,"detail": "Modern web apps using Angular and Node.js" },
              { "title": "Mobile Apps","image":"https://i.postimg.cc/6q6zNjBB/gun2.jpg" , "detail": "Hybrid apps with Ionic and Capacitor" },
              { "title": "Cloud Integration","image":"https://i.postimg.cc/wMW2xXB7/gun3.jpg" , "detail": "Seamless AWS and Azure integration" },
              { "title": "AI Solutions","image":"https://i.postimg.cc/8cCdY7b7/gun4.jpg" , "detail": "Intelligent automation and chatbots" },
              { "title": "UI/UX Design","image":"https://i.postimg.cc/bNsHH2J9/gun5.jpg" , "detail": "Beautiful and responsive designs" },
              { "title": "SEO Optimization","image":"https://i.postimg.cc/4Nqv8N7M/gun6.jpg" , "detail": "Boost your online visibility" },
              { "title": "DevOps","image":"https://i.postimg.cc/4xc6jkps/gun7.jpg" , "detail": "CI/CD and scalable deployment pipelines" },
              { "title": "API Development","image":"https://i.postimg.cc/Xv0fbHgm/gun8.jpg" , "detail": "Secure REST and GraphQL APIs" },
              { "title": "Consulting","image":"https://i.postimg.cc/6q6zNjBB/gun2.jpg" , "detail": "Technical guidance and architecture reviews" }
            ]'::jsonb,
            '[
              {"title":"address","detail":"Chellappa Chettiar Temple WRR8+66R, Devakottai, Udayachi, Tamil Nadu 630302"},
              {"title":"email","detail":"manirajmca.ac@gmail.com"},
              {"title":"map","detail":"https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d1964.9656486154352!2d78.81471954875092!3d9.939674502559942!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3b005b1f62bfffff%3A0x18a02f6e5b3bf3e9!2sChellappa%20Chettiar%20Temple!5e0!3m2!1sen!2sin!4v1762067262513!5m2!1sen!2sin"},
              {"title":"phone","detail":"9965972105"}
            ]'::jsonb,
            '[
              {"title":"home","detail":"/home","heading":"Important Link","position":"left"},
              {"title":"aboutus","detail":"/aboutus","heading":"Important Link","position":"left"},
              {"title":"products","detail":"/products","heading":"Resource Link","position":"right"},
              {"title":"contactus","detail":"/contactus","heading":"Resource Link","position":"right"}
            ]'::jsonb,
            '{
              "logo":"https://cdn-icons-png.flaticon.com/512/4257/4257824.png",
              "sitename":"NewDweb",
              "font":"",
              "textcolor":"",
              "darktheme":"0"
            }'::jsonb
        );
        """

        cur.execute("DELETE FROM webPage;")  # clear old data if needed
        cur.execute(query)
        conn.commit()
        cur.close()
        conn.close()
        return {"message": "webPage table reset successfully."}

    except Exception as e:
        return {"error": str(e)}
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
