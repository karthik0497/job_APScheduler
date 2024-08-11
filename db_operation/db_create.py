import psycopg2
from psycopg2 import sql
from urllib.parse import urlparse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DATABASE_URL = "postgresql://postgres:12345@localhost:5432/job_schedule_db"
table_name = "jobs"

def check_and_create_table():
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        with conn.cursor() as cursor:
            # Create table if it doesn't exist
            cursor.execute(sql.SQL("""
                CREATE TABLE IF NOT EXISTS {} (
                    job_id SERIAL PRIMARY KEY,
                    job_name VARCHAR(255) NOT NULL,
                    job_schedule JSONB NOT NULL,
                    job_description TEXT NOT NULL,
                    job_type VARCHAR(50),
                    job_params JSONB,
                    last_run TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """).format(sql.Identifier(table_name)))
            
            conn.commit()
            logging.info("Table '{}' created or already exists.".format(table_name))

    except psycopg2.Error as e:
        logging.error("An error occurred while creating the table: %s", e)

    finally:
        if conn:
            conn.close()

def check_and_add_columns():
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        with conn.cursor() as cursor:
            # List of expected columns and their types
            expected_columns = {
                "job_name": "VARCHAR(255) NOT NULL",
                "job_schedule": "JSONB NOT NULL",
                "job_description": "TEXT NOT NULL",
                "job_type": "VARCHAR(50)",
                "job_params": "JSONB",
                "last_run": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            }
            
            # Check existing columns in the table
            cursor.execute(sql.SQL("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = %s
            """), (table_name,))
            
            existing_columns = {row[0] for row in cursor.fetchall()}
            
            logging.info("Existing columns: %s", existing_columns)
            
            # Determine missing columns
            missing_columns = {col: typ for col, typ in expected_columns.items() if col not in existing_columns}
            
            if missing_columns:
                logging.info("Adding missing columns:")
                for col, typ in missing_columns.items():
                    logging.info("  - %s", col)
                    cursor.execute(sql.SQL("""
                        ALTER TABLE {} ADD COLUMN {} {}
                    """).format(sql.Identifier(table_name), sql.Identifier(col), sql.SQL(typ)))
                conn.commit()
                logging.info("Missing columns added successfully.")
            else:
                logging.info("All expected columns are present.")
                
    except psycopg2.Error as e:
        logging.error("An error occurred while adding columns: %s", e)
        
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_and_create_table()
    check_and_add_columns()
