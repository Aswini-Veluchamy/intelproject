import mysql.connector
import pandas as pd
from sqlalchemy import create_engine
import time
from datetime import datetime


# CREATE TABLE test_data(
# milestone VARCHAR(100) NOT NULL,
# trend VARCHAR(100) NOT NULL,
# target VARCHAR(100) NOT NULL,
# implement VARCHAR(100) NOT NULL,
# complete VARCHAR(100) NOT NULL,
# die VARCHAR(100) NOT NULL,
# sheet VARCHAR(100) NOT NULL,
# ts TIMESTAMP
# );

def db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root1234',
        database="intel_project",
        port=3406
    )
    return conn


def load_data(data):
    conn = db_connection()
    cursor = conn.cursor()
    for i in data:
        sql = f"INSERT INTO test_data (milestone, trend, target, implement, complete, die, sheet, ts) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        val = (i['milestone'], i['trend'], i['target'], i['implement'], i['complete'], i['die'], i['sheet'], datetime.now())
        cursor.execute(sql, val)
    conn.commit()
    print(f'data inserted in table ....')
    conn.close()


a = [
    {'trend': 'wW24', 'target': "24'ww12", 'milestone': '1', 'implement': '2', 'complete': '3','die': '4', 'sheet': 'sheet1'},
    {'trend': 'WW24', 'target': '24WW12', 'milestone': '1', 'implement': '2', 'complete': '3','die': '4', 'sheet': 'sheet2'},
    {'trend': "24'ww12", 'target': 'WW24', 'milestone': '1', 'implement': '2', 'complete': '3','die': '4', 'sheet': 'sheet3'}
]


def convert_upper(string):
    upper_string = ""
    for char in string:
        if char.isalpha():
            upper_string += char.upper()
        else:
            upper_string += char
    return upper_string


for i in range(len(a)):
    # data conversion for target column
    if len(a[i]['trend'].strip()) == 4 and a[i]['trend'][0:2].strip().upper() == 'WW':
        a[i]['trend'] = convert_upper(f'24{a[i]["trend"].strip()}')
    if len(a[i]['trend'].strip()) == 7:
        a[i]['trend'] = convert_upper(a[i]['trend'].strip().replace("'", ''))
    # data conversion for target column
    if len(a[i]['target'].strip()) == 4 and a[i]['target'][0:2].strip().upper() == 'WW':
        a[i]['target'] = convert_upper(f'24{a[i]["target"].strip()}')
    if len(a[i]['target'].strip()) == 7:
        a[i]['target'] = convert_upper(a[i]['target'].strip().replace("'", ''))


load_data(a)


exit()

#
#
#
#
# def read_excel_doc(path):
#     # Read all sheets into a dictionary
#     sheets_dict = pd.read_excel(path, sheet_name=None)
#     result = []
#     for i, j in sheets_dict.items():
#         d = j.to_dict(orient='records')
#         result.extend(d)
#     return result
#
#
# def load_new_data(path, table):
#     result = read_excel_doc(path)
#     for i in result:
#         print(i)
#
# load_new_data('C:\\Users\\Srinivas\\Documents\\test.xlsx', 'test')
#
#
#
# def read_sql_data(table_name, csv_file_path):
#     conn = db_connection()
#     dict_cursor = conn.cursor(dictionary=True)
#     sql = f"SELECT * FROM {table_name}"
#     dict_cursor.execute(sql)
#     records = dict_cursor.fetchall()
#
#     # Convert dictionary to DataFrame
#     df = pd.DataFrame(records)
#     # Save DataFrame to CSV
#     df.to_csv(csv_file_path, index=False)
#
#
# def load_data_to_sql(csv_file_path, table_name):
#     # Create MySQL engine
#     engine = create_engine('mysql+mysqlconnector://root:root1234@localhost:3406/intel_project')
#     # Read CSV into DataFrame
#     df = pd.read_csv(csv_file_path)
#     # Load DataFrame into MySQL
#     df.to_sql(table_name, engine, if_exists='replace', index=False)
#     print("Data loaded into MySQL table:", table_name)
#
#
# def load_sql(csv_file_path, table_name):
#     conn = db_connection()
#     cursor = conn.cursor()
#     df = pd.read_csv(csv_file_path)
#
#     # Convert the DataFrame to a dictionary
#     data_dict = df.to_dict(orient="records")
#
#     # Print the dictionary
#     print(data_dict)
#     # sql = f"INSERT INTO {table_name} (display, milestone, por_commit, por_trend, por_trend2, status, comments, schedule_id,\
#     #             user, project, deleted, deleted_by, deleted_on) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
#     # val = (display, milestone, por_commit, por_trend, por_trend2, status, comments, schedule_id, user, proj, deleted,
#     #        deleted_by, deleted_on)
#     # cursor.execute(sql, val)
#     # print(f'data inserted in {SCHEDULE_TABLE} ....')
#     # conn.commit()
#     # conn.close()
#
#
# def delete_data(table_name):
#     conn = db_connection()
#     cursor = conn.cursor()
#     sql = f"delete from {table_name}"
#     print(sql)
#     cursor.execute(sql)
#     conn.commit()
#
#     time.sleep(4)
#     # delete the table
#     sql = f"drop table {table_name}"
#     print(sql)
#     cursor.execute(sql)
#     conn.commit()
#     conn.close()
#     print(f'Deleted table {table_name}')
#
#
#
# #read_sql_data('schedule_table', 'D:\\schedule_table.csv')
# #load_data_to_sql('D:\\schedule_table.csv', 'schedule_table')
# #delete_data('schedule_table')
# #load_sql('D:\\schedule_table.csv', 'schedule_table')
#
