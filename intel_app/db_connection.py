import mysqlx

'''
 pip install mysql-connector-python
'''


def load_key_message_data(data):
    session = mysqlx.get_session({"host": "localhost", "port": 33060, "user": "root", "password": "root1234"})
    for user, msg, proj in data:
        insert = f"INSERT INTO `intel_project`.`key_message`(user, message, project)values('{user}','{msg}','{proj}');"
        session.sql(insert).execute()
    print('data loadedd')
    session.commit()
    session.close()