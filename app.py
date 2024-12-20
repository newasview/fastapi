from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from config import settings
#import pandas as pd
from typing import List, Optional
import mysql.connector
from mysql.connector import Error
#from fastapi.responses import JSONResponse

#df = pd.read_csv("crime_data.csv")

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# MySQL connection settings
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=settings.HOST,  # MySQL host
            database=settings.DATABASE,  # Database name
            user=settings.USER,  # Your MySQL username
            password=settings.PASSWORD  # Your MySQL password
        )
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None

# Pydantic model for crime data
class CrimeData(BaseModel):
    state: str
    year: int
    rape: int
    ka: int
    dd: int
    aow: int
    aom: int
    dv: int
    wt: int

# Fetch data for the given year and crime type
"""@app.get("/getcsv", response_model=List[CrimeData])
async def get_crimes(
    year: Optional[int] = None,
    state: Optional[str] = None,
    crime_type: Optional[str] = None,
):
    # Filter the dataset based on query parameters
    filtered_df = df
    if year:
        filtered_df = filtered_df[filtered_df["Year"] == year]
    if state:
        filtered_df = filtered_df[filtered_df["State"] == state]
    if crime_type:
        filtered_df = filtered_df[filtered_df["Crime_Type"] == crime_type]

    # Convert the filtered dataframe to a list of CrimeData models
    crime_list = filtered_df.to_dict(orient="records")
    return JSONResponse(content=crime_list)"""

@app.get("/crimes", response_model=List[CrimeData])
async def get_crimes():
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT *, LOWER(state) as lowerstate FROM crimeswomen")
        rows = cursor.fetchall()
        return rows
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")
    finally:
        connection.close()

@app.get("/crimes/{state}", response_model=List[CrimeData])
async def get_crimes_by_state(state: str):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT *, LOWER(state) as lowerstate FROM crimeswomen WHERE state = %s", (state,))
        rows = cursor.fetchall()
        if not rows:
            raise HTTPException(status_code=404, detail=f"No data found for state: {state}")
        return rows
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")
    finally:
        connection.close()

@app.get("/crimeorderby/{order}/{direction}", response_model=List[CrimeData])
async def get_crimes_by_state(order: str, direction: str):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT *, LOWER(state) as lowerstate FROM crimeswomen ORDER BY %s %s", (order, direction))
        rows = cursor.fetchall()
        return rows
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")
    finally:
        connection.close()

# Pydantic model for aggregated crime data by state
class AggregatedCrimeData(BaseModel):
    state: str
    crime_rate: float  # We can calculate a simple crime rate, or more advanced metrics

@app.get("/crimesaggregated", response_model=List[AggregatedCrimeData])
async def get_aggregated_crime_data():
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        cursor = connection.cursor(dictionary=True)
        # Aggregating crime data by state (You can adjust the columns based on your requirements)
        cursor.execute("""
            SELECT state, 
                   SUM(rape + ka + dd + aow + aom + dv + wt) AS total_crimes,
                   COUNT(*) AS num_records
            FROM crimeswomen
            GROUP BY state
        """)
        rows = cursor.fetchall()

        # Calculating crime rate: sum of crimes divided by the number of records for each state
        aggregated_data = []
        for row in rows:
            crime_rate = row["total_crimes"] / row["num_records"]  # Simplified crime rate
            aggregated_data.append(AggregatedCrimeData(state=row["state"], crime_rate=crime_rate))

        # Sort by crime_rate in descending order
        aggregated_data.sort(key=lambda x: x.crime_rate, reverse=True)

        return aggregated_data

    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")
    finally:
        connection.close()

"""
Suggestions for Improvement:
Exception Handling in API Endpoints:

It would be good to add exception handling in the API routes to ensure that any issues with database queries or connections are handled gracefully.
You could also consider using FastAPI’s HTTPException to send proper error codes to the client when things go wrong.
Database Connection Cleanup:

In the current code, the database connection is closed manually after each query. You might want to use a context manager (e.g., with statement) to ensure that the connection and cursor are properly closed, even in case of errors.
Connection Pooling:

For production-level applications, using connection pooling (like mysql.connector.pooling) can be beneficial to optimize database connection management.
Data Validation and Schema:

Ensure that the data being inserted into or fetched from the database strictly adheres to the Pydantic CrimeData model. You can add more validation on the input side (for POST requests, if you decide to add them) and on the database schema to prevent data inconsistencies.
Password Security:

In the get_db_connection function, you have hardcoded the MySQL password. It’s recommended to use environment variables or a configuration file to store sensitive credentials for security reasons.
Consider Async Database Calls:

FastAPI supports asynchronous database calls. However, mysql.connector is synchronous. If you want to fully leverage FastAPI’s asynchronous capabilities, you may want to consider an async-compatible database library such as databases (which supports MySQL) or aiomysql.

"""