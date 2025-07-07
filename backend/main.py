from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
from datetime import date

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

# pydantic model for prooduct update
class ProductUpdate(BaseModel):
    batch_ids: list[int]
    delivered_on: date
    quantity_removed: float

@app.post("/add-stock")
def add_stock(data: StockEntry):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        query = """
            INSERT INTO inventory (product_id, production_date, expiry_date, quantity)
            VALUES (%s, %s, %s, %s)
        """

        values = (data.product_id, data.production_date, data.expiry_date, data.quantity)

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
            SELECT batch_id, product_id, quantity, production_date, expiry_date
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

@app.post("/update-stock")
def update_stock(request: ProductUpdate):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Step 1: Fetch product_id from first batch (assuming all batches are same product)
        cursor.execute("SELECT product_id FROM inventory WHERE batch_id = %s", (request.batch_ids[0],))
        result = cursor.fetchone()
        if not result:
            return {"message": "Invalid batch ID"}
        product_id = result["product_id"]

        # Step 2: Delete selected batches from inventory
        format_strings = ','.join(['%s'] * len(request.batch_ids))
        cursor.execute(
            f"DELETE FROM inventory WHERE batch_id IN ({format_strings})",
            tuple(request.batch_ids)
        )

        # Step 3: Insert into sales table
        cursor.execute(
            "INSERT INTO sales (product_id, quantity, sales_date) VALUES (%s, %s, %s)",
            (product_id, request.quantity_removed, request.delivered_on)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "Stock updated and sale recorded successfully!"}

    except Exception as e:
        return {"message": f"Error: {e}"}
    
@app.get("/product-summary")
def get_product_summary():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT p.product_id, p.product_names, p.unit, 
                   IFNULL(SUM(i.quantity), 0) AS total_quantity
            FROM products p
            LEFT JOIN inventory i ON p.product_id = i.product_id
            GROUP BY p.product_id, p.product_names, p.unit
        """)
        summary = cursor.fetchall()
        cursor.close()
        conn.close()
        return summary

    except Exception as e:
        return {"message": f"Error: {e}"}