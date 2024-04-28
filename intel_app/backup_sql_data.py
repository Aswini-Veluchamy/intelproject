import mysql.connector
import pandas as pd
from sqlalchemy import create_engine
import time


def db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root1234',
        database="intel_project",
        port=3406
    )
    return conn


def read_sql_data(table_name, csv_file_path):
    conn = db_connection()
    dict_cursor = conn.cursor(dictionary=True)
    sql = f"SELECT * FROM {table_name}"
    dict_cursor.execute(sql)
    records = dict_cursor.fetchall()

    # Convert dictionary to DataFrame
    df = pd.DataFrame(records)
    # Save DataFrame to CSV
    df.to_csv(csv_file_path, index=False)


def load_data_to_sql(csv_file_path, table_name):
    # Create MySQL engine
    engine = create_engine('mysql+mysqlconnector://root:root1234@localhost:3406/intel_project')
    # Read CSV into DataFrame
    df = pd.read_csv(csv_file_path)
    # Load DataFrame into MySQL
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    print("Data loaded into MySQL table:", table_name)


def delete_data(table_name):
    conn = db_connection()
    cursor = conn.cursor()
    sql = f"delete from {table_name}"
    print(sql)
    cursor.execute(sql)
    conn.commit()

    time.sleep(4)
    # delete the table
    sql = f"drop table {table_name}"
    print(sql)
    cursor.execute(sql)
    conn.commit()
    conn.close()
    print(f'Deleted table {table_name}')



#read_sql_data('issues_bkp_table', 'D:\\issues_bkp.csv')
load_data_to_sql('D:\\issues.csv', 'issues_table')
#delete_data('issues_bkp_table')

