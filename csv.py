"""import csv
from fastapi.responses import StreamingResponse
from io import StringIO
import mysql.connector
from mysql.connector import Error

@app.get("/crimes/csv")
async def export_crimes_csv():
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM crimeswomen")
        rows = cursor.fetchall()

        # Create a CSV in-memory file
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=[key for key in rows[0].keys()])
        writer.writeheader()
        writer.writerows(rows)
        
        # Set the file pointer to the beginning
        output.seek(0)

        # Create a streaming response to send the CSV
        return StreamingResponse(output, media_type="text/csv", headers={
            "Content-Disposition": "attachment; filename=crime_data.csv"
        })
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")
    finally:
        connection.close()"""

"""Explanation:
StreamingResponse: The StreamingResponse class is used to stream the CSV file directly as a response. The media_type="text/csv" tells the client that the response contains CSV data.
StringIO: This is used as an in-memory file to write the CSV data instead of writing to disk.
Headers: The Content-Disposition header is set to suggest to the client that this is an attachment, so it prompts the user to download the file."""