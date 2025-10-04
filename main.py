from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import psycopg2.extras
import uvicorn
hostName = "localhost"
portName = 5432
databaseName = "DynamicWebsite"
userName = "postgres"
password = "Vinsa$POS$ool"
# cur = None
conn = None
try:
    with psycopg2.connect(
        dbname=databaseName,
        user= userName,
        password=password,
        host=hostName,
        port=portName
    ) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("DROP TABLE IF EXISTS content")
                create_script = '''
                    CREATE TABLE IF NOT EXISTS content (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        body TEXT NOT NULL)'''
                cur.execute(create_script)
                insert_script = '''
                    INSERT INTO content (title, body) VALUES (%s, %s) '''
                insert_values = [('sample title', 'sample body'),('sample title1', 'sample body1'),('sample title2', 'sample body2'),('sample title3', 'sample body3')]
                
                for record in insert_values:
                    cur.execute(insert_script,record)

                update_script = ''' UPDATE content SET title = %s WHERE id = %s '''
                update_values = ('updated title',1) 
                cur.execute(update_script,update_values)

                delete_script = ''' DELETE FROM content WHERE id = %s '''
                delete_value = (2,)
                cur.execute(delete_script,delete_value)

                cur.execute("SELECT * FROM content")
                records = cur.fetchall()
                print("Records:", records) 

                for record in records:
                    print(record["title"], record["body"])

                conn.commit()
                print("Table created Successfully")   
except Exception as e:
    print("Error:", e)
finally:
    if conn is not None:
        conn.close()
    # if cur is not None:
    #     cur.close()    
#Define schema
class Item(BaseModel):
    name: str
    price: float
    is_offer: bool | None = None
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:4200"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
async def root():
    return {"message":"Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id:int,q:str|None =None):
    return {"item_id":item_id,"q":q}

@app.get("/item",response_model=Item)
def read_gen_item():
    return {"name":"sample item","price":9.99,"is_offer":True}

@app.post("/addItem",response_model=Item)
async def create_item(item: Item):
    # Convert string fields to uppercase
    data = item.dict()
    for key, value in data.items():
        if isinstance(value, str):
            data[key] = value.upper()
    return Item(**data)  # return new Item with updated values



if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

