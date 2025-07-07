from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
from datetime import date
import random

# Initialize FastAPI application
app = FastAPI()

# Allow frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific domain in production
    allow_methods=["*"],
    allow_headers=["*"]
)

# DB connection config
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "inventory",
    "port": 3306
}

# Pydantic model for request validation
class StockEntry(BaseModel):
    product_id: int
    quantity: float
    production_date: date
    expiry_date: date

# Pydantic model for product input
class ProductRequest(BaseModel):
    product_id: int
    

@app.post("/add-stock")
def add_stock(data: StockEntry):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        query = """
            INSERT INTO inventory (product_id, batch_id, production_date, expiry_date, quantity)
            VALUES (%s, %s, %s, %s, %s)
        """

        batch_id = date.today().strftime("%y%m%d") + str(random.randint(100, 999))

        values = (data.product_id, batch_id, data.production_date, data.expiry_date, data.quantity)

        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Stock added successfully!"}
    except Exception as e:
        return {"message": f"Error: {e}"}


@app.post("/get-batches")
def get_batches(request: ProductRequest):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT batch_id, quantity, production_date, expiry_date
            FROM inventory
            WHERE product_id = %s
            ORDER BY expiry_date ASC
        """, (request.product_id,))

        results = cursor.fetchall()
        cursor.close()
        conn.close()

        return results

    except Exception as e:
        print("Error:", e)