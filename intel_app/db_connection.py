import mysql.connector
from .config import HOST, PORT, USER, PASSWORD
from .config import KEY_MESSAGE_TABLE, RISK_TABLE, KEY_PROGRAM_METRIC_TABLE
from .config import DETAILS_TABLE, SCHEDULE_TABLE, LINKS_TABLE


def db_connection():
    conn = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database="intel_project",
        port=3406
    )
    cursor = conn.cursor()
    return conn, cursor


def load_key_message_data(data):
    conn, cursor = db_connection()
    for msg_id, user, msg, proj in data:
        sql = f"INSERT INTO {KEY_MESSAGE_TABLE} (message_id, user, message, project) VALUES (%s, %s, %s, %s)"
        val = (msg_id, user, msg, proj)
        cursor.execute(sql, val)
    print(f'data inserted in {KEY_MESSAGE_TABLE} ....')
    conn.commit()
    conn.close()


def update_key_message_data(data):
    conn, cursor = db_connection()
    for msg_id, message in data:
        sql = f"UPDATE {KEY_MESSAGE_TABLE} SET message = '{message}' WHERE message_id='{msg_id}'"
        cursor.execute(sql)
    print(f'data updated in {KEY_MESSAGE_TABLE} ....')
    conn.commit()
    conn.close()


def load_risk_data(data):
    conn, cursor = db_connection()
    for ps, status, owner, msg, eta, risk, severity, impact, risk_id, proj, user, display in data:
        sql = f"INSERT INTO {RISK_TABLE} (problem_statement, status, owner, message, eta, risk, severity, impact, \
            risk_id, project, user, display) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (ps, status, owner, msg, eta, risk, severity, impact, risk_id, proj, user, display)
        cursor.execute(sql, val)
    print(f'data inserted in {RISK_TABLE} ....')
    conn.commit()
    conn.close()


def update_risk_data(data):
    conn, cursor = db_connection()
    for ps, status, owner, msg, eta, risk, severity, impact, risk_id in data:
        sql = (f"UPDATE {RISK_TABLE} SET problem_statement = '{ps}', status = '{status}', owner = '{owner}', \
                message = '{msg}', eta = '{eta}', risk = '{risk}', severity = '{severity}', impact = '{impact}' \
                WHERE risk_id='{risk_id}'")
        cursor.execute(sql)
    print(f'data updated in {RISK_TABLE} ....')
    conn.commit()
    conn.close()


def load_key_program_metric_data(data):
    conn, cursor = db_connection()
    for metric, fv_target, cwa, cwp, status, comments, metric_id,  proj, user in data:
        sql = f"INSERT INTO {KEY_PROGRAM_METRIC_TABLE} (metric, fv_target, current_week_actual,\
                current_week_plan, status, comments, metric_id, project, user) \
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (metric, fv_target, cwa, cwp, status, comments, metric_id,  proj, user)
        cursor.execute(sql, val)
    print(f'data inserted in {KEY_PROGRAM_METRIC_TABLE} ....')
    conn.commit()
    conn.close()


def update_key_program_metric_data(data):
    conn, cursor = db_connection()
    for metric, fv_target, cwa, cwp, status, comments, metric_id in data:
        sql = (f"UPDATE {KEY_PROGRAM_METRIC_TABLE} SET metric = '{metric}', fv_target = '{fv_target}', \
                current_week_actual = '{cwa}', current_week_plan = '{cwp}', status = '{status}', comments = '{comments}' \
                WHERE metric_id='{metric_id}'")
        cursor.execute(sql)
    print(f'data updated in {KEY_PROGRAM_METRIC_TABLE} ....')
    conn.commit()
    conn.close()


def delete_key_program_metric_data(metric_id):
    conn, cursor = db_connection()
    sql = f"DELETE FROM {KEY_PROGRAM_METRIC_TABLE} WHERE metric_id='{metric_id}'"
    cursor.execute(sql)
    print(f'data deleted in {KEY_PROGRAM_METRIC_TABLE} ....{metric_id}')
    conn.commit()
    conn.close()


def load_details_data(details_id, user, msg, proj):
    conn, cursor = db_connection()
    sql = f"INSERT INTO {DETAILS_TABLE} (details_id, user, message, project) VALUES (%s, %s, %s, %s)"
    val = (details_id, user, msg, proj)
    cursor.execute(sql, val)
    print(f'data inserted in {DETAILS_TABLE} ....')
    conn.commit()
    conn.close()


def update_details_data(details_id, message):
    conn, cursor = db_connection()
    sql = f"UPDATE {DETAILS_TABLE} SET message = '{message}' WHERE details_id='{details_id}'"
    cursor.execute(sql)
    print(f'data updated in {DETAILS_TABLE} ....')
    conn.commit()
    conn.close()


def load_schedule_data(milestone, por_commit, por_trend, status, comments, schedule_id, user, proj):
    conn, cursor = db_connection()
    sql = f"INSERT INTO {SCHEDULE_TABLE} (milestone, por_commit, por_trend, status, comments, schedule_id,\
            user, project) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    val = (milestone, por_commit, por_trend, status, comments, schedule_id, user, proj)
    cursor.execute(sql, val)
    print(f'data inserted in {SCHEDULE_TABLE} ....')
    conn.commit()
    conn.close()


def update_schedule_data(data):
    conn, cursor = db_connection()
    for milestone, por_commit, por_trend, status, comments, schedule_id in data:
        sql = (f"UPDATE {SCHEDULE_TABLE} SET milestone = '{milestone}', por_commit = '{por_commit}', \
                por_trend = '{por_trend}', status = '{status}', comments = '{comments}' \
                WHERE schedule_id='{schedule_id}'")
        cursor.execute(sql)
    print(f'data updated in {SCHEDULE_TABLE} ....')
    conn.commit()
    conn.close()


def load_links_data():
    conn, cursor = db_connection()
    sql = f"INSERT INTO {LINKS_TABLE} (milestone, por_commit, por_trend, status, comments, schedule_id,\
            user, project) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    val = (milestone, por_commit, por_trend, status, comments, schedule_id, user, proj)
    cursor.execute(sql, val)
    print(f'data inserted in {SCHEDULE_TABLE} ....')
    conn.commit()
    conn.close()
