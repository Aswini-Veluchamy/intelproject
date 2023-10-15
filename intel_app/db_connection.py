import mysqlx
from .config import HOST, PORT, USER, PASSWORD
from .config import KEY_MESSAGE_TABLE


def load_key_message_data(data):
    session = mysqlx.get_session({"host": HOST, "port": PORT, "user": USER, "password": PASSWORD})
    for msg_id, user, msg, proj in data:
        insert_query = f"INSERT INTO `intel_project`.`{KEY_MESSAGE_TABLE}`(message_id, user, message, project)values('{msg_id}','{user}','{msg}','{proj}');"
        session.sql(insert_query).execute()
    print(f'data inserted in {KEY_MESSAGE_TABLE} ....')
    session.commit()
    session.close()


def update_key_message_data(data):
    session = mysqlx.get_session({"host": HOST, "port": PORT, "user": USER, "password": PASSWORD})
    for msg_id, message in data:
        update_query = f"UPDATE `intel_project`.`{KEY_MESSAGE_TABLE}` SET message='{message}' WHERE message_id='{msg_id}';"
        session.sql(update_query).execute()
    print(f'data updated in {KEY_MESSAGE_TABLE} ....')
    session.commit()
    session.close()