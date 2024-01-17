import mysql.connector
from .config import HOST, PORT, USER, PASSWORD
from .config import KEY_MESSAGE_TABLE, RISK_TABLE, KEY_PROGRAM_METRIC_TABLE
from .config import DETAILS_TABLE, SCHEDULE_TABLE, LINKS_TABLE, BBOX_TABLE
import json
import bcrypt


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


def get_key_msg_or_details_data(user, table):
    conn, cursor = db_connection()
    cursor.execute(f'SELECT * FROM {table} where user="{user}" ORDER BY ts DESC LIMIT 1;')
    columns = [col[0] for col in cursor.description]
    result = dict(zip(columns, cursor.fetchone()))
    conn.commit()
    conn.close()
    return result


def get_data(user, table):
    conn, cursor = db_connection()
    cursor.execute(f"SELECT * FROM {table} where user='{user}'")
    records = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    result = [dict(zip(columns, record)) for record in records]
    conn.commit()
    conn.close()
    return result


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


def load_links_data(links_url, comments, links_id, project, user):
    conn, cursor = db_connection()
    sql = f"INSERT INTO {LINKS_TABLE} (links_url, comments_links, links_id, project, user) VALUES (%s, %s, %s, %s, %s)"
    val = (links_url, comments, links_id, project, user)
    cursor.execute(sql, val)
    print(f'data inserted in {LINKS_TABLE} ....')
    conn.commit()
    conn.close()


def update_links_data(links_url, comments, links_id):
    conn, cursor = db_connection()
    sql = (f"UPDATE {LINKS_TABLE} SET links_url = '{links_url}', comments_links = '{comments}' WHERE links_id='{links_id}'")
    print(sql)
    cursor.execute(sql)
    print(f'data updated in {links_id} ....')
    conn.commit()
    conn.close()


def register_user(username, password, project, admin_status):
    """Register a new user."""
    try:
        conn, cursor = db_connection()
        query = "INSERT INTO users (username, password, project, admin_status) VALUES (%s, %s, %s, %s)"
        project_json = json.dumps(project)
        cursor.execute(query, (username, password, project_json, admin_status))
        conn.commit()
        print("User registered successfully!")
    except mysql.connector.Error as err:
        print(f"Error: {err}")


def login_user(username, password):
    """Login an existing user."""
    try:
        conn, cursor = db_connection()
        query = "SELECT username, password FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        if user:
            stored_hashed_password = user[1]
            # Verify the entered password against the stored hash
            if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
                columns = [col[0] for col in cursor.description]
                result = dict(zip(columns, user))
                return user[0], result
            else:
                return None, None
        else:
            return None, None
    except mysql.connector.Error as err:
        print(f"Error: {err}")


def create_project(project):
    """Register a new project."""
    try:
        conn, cursor = db_connection()
        query = f"INSERT INTO project_data (project) VALUES (%s)"
        data = (project,)
        cursor.execute(query, data)
        conn.commit()
        print("project created successfully!")
    except mysql.connector.Error as err:
        print(f"Error: {err}")


def get_projects():
    """Register a new project."""
    try:
        conn, cursor = db_connection()
        query = "SELECT project FROM project_data"
        cursor.execute(query)
        project = cursor.fetchall()
        if project:
            result = [i[0] for i in project]
            return result
        else:
            return None
    except mysql.connector.Error as err:
        print(f"Error: {err}")


def get_users():
    """Register a new project."""
    try:
        conn, cursor = db_connection()
        query = "select distinct(username) from users"
        cursor.execute(query)
        users = cursor.fetchall()
        if users:
            result = [i[0] for i in users]
            return result
        else:
            return None
    except mysql.connector.Error as err:
        print(f"Error: {err}")


def load_bbox_data(process, die_area, config, pv_freq, perf_target, cdyn, schedule_bbox, bbox_id,
                   project, user):
    conn, cursor = db_connection()
    sql = f"INSERT INTO {BBOX_TABLE} (process, die_area, config, pv_freq, perf_target, cdyn,\
            schedule_bbox, bbox_id, project, user) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (process, die_area, config, pv_freq, perf_target, cdyn, schedule_bbox, bbox_id, project, user)
    cursor.execute(sql, val)
    print(f'data inserted in {BBOX_TABLE} ....')
    conn.commit()
    conn.close()


def update_bbox_data(process, die_area, config, pv_freq, perf_target, cdyn, schedule_bbox, bbox_id):
    conn, cursor = db_connection()
    sql = (f"UPDATE {BBOX_TABLE} SET process = '{process}', die_area = '{die_area}', \
            config = '{config}', pv_freq = '{pv_freq}', perf_target = '{perf_target}', cdyn = '{cdyn}', \
            schedule_bbox = '{schedule_bbox}' \
            WHERE bbox_id='{bbox_id}'")
    cursor.execute(sql)
    print(f'data updated in {BBOX_TABLE} ....')
    conn.commit()
    conn.close()


def update_password(user_id, password):
    try:
        conn, cursor = db_connection()
        get_user_query = f"select * from users where username='{user_id}'"
        cursor.execute(get_user_query)
        users = cursor.fetchall()
        if users:
            sql = f"UPDATE users SET password = '{password}' WHERE username='{user_id}'"
            cursor.execute(sql)
            conn.commit()
            conn.close()
            return True
        else:
            raise Exception("Username not exists.................")
    except Exception as ex:
        return False


def encrypt_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password
