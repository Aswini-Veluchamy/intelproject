import mysql.connector
from .config import HOST, PORT, USER, PASSWORD
from .config import KEY_MESSAGE_TABLE, RISK_TABLE, KEY_PROGRAM_METRIC_TABLE
from .config import DETAILS_TABLE, SCHEDULE_TABLE, LINKS_TABLE, BBOX_TABLE, ISSUES_TABLE
import json
import bcrypt
import time


def db_connection():
    conn = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database="intel_project",
        port=3306
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


def load_risk_data(data, table):
    conn, cursor = db_connection()
    print(data, table)
    display, risk_summary, risk_area, status, owner, consequence, mitigations, trigger_date, risk_initiated, impact, risk_id, project, user = data
    sql = f"INSERT INTO {table} (display, risk_summary, risk_area, status, owner, consequence, mitigations, trigger_date, risk_initiated, impact, \
        risk_id, project, user) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (display, risk_summary, risk_area, status, owner, consequence, mitigations, trigger_date, risk_initiated, impact, risk_id, project, user)
    print(sql)
    cursor.execute(sql, val)
    print(f'data inserted in {table} ....')
    conn.commit()
    conn.close()


def get_key_msg_or_details_data(table, project):
    conn, cursor = db_connection()
    cursor.execute(f'SELECT * FROM {table} where project="{project}" ORDER BY ts DESC LIMIT 1;')
    columns = [col[0] for col in cursor.description]
    result = dict(zip(columns, cursor.fetchone()))
    conn.commit()
    conn.close()
    return result


def get_data(user, table, project, deleted=None):
    conn, cursor = db_connection()
    if deleted == False:
        sql = f"SELECT * FROM {table} where user='{user}' and project='{project}' and deleted={deleted}"
    else:
        sql = f"SELECT * FROM {table} where user='{user}' and project='{project}'"
    cursor.execute(sql)
    records = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    result = [dict(zip(columns, record)) for record in records]
    conn.commit()
    conn.close()
    return result


def get_schedule_record(pk):
    conn, cursor = db_connection()
    sql = f"SELECT * FROM {SCHEDULE_TABLE} where schedule_id='{pk}'"
    cursor.execute(sql)
    records = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    result = [dict(zip(columns, record)) for record in records]
    conn.commit()
    conn.close()
    return result


def update_risk_data(data):
    conn, cursor = db_connection()
    for display, risk_summary, risk_area, status, owner, consequence, mitigations, trigger_date, risk_initiated, impact, risk_id in data:
        sql = (f"UPDATE {RISK_TABLE} SET display = '{display}', risk_summary = '{risk_summary}',risk_area = '{risk_area}', status = '{status}', owner = '{owner}', \
                consequence = '{consequence}',mitigations = '{mitigations}', trigger_date = '{trigger_date}', \
                risk_initiated = '{risk_initiated}', impact = '{impact}' \
                WHERE risk_id='{risk_id}'")
        cursor.execute(sql)
    print(f'data updated in {RISK_TABLE} ....')
    conn.commit()
    conn.close()


def load_key_program_metric_data(data, table):
    conn, cursor = db_connection()
    for display, metric, fv_target, cwa, cwp, status, comments, metric_id,  proj, user in data:
        sql = f"INSERT INTO {table} (display, metric, fv_target, current_week_actual,\
                current_week_plan, status, comments, metric_id, project, user) \
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (display, metric, fv_target, cwa, cwp, status, comments, metric_id,  proj, user)
        cursor.execute(sql, val)
    print(f'data inserted in {table} ....')
    conn.commit()
    conn.close()


def update_key_program_metric_data(data):
    conn, cursor = db_connection()
    for display, metric, fv_target, cwa, cwp, status, comments, metric_id in data:
        sql = (f"UPDATE {KEY_PROGRAM_METRIC_TABLE} SET display = '{display}', metric = '{metric}', fv_target = '{fv_target}', \
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


def load_schedule_data(display, milestone, por_commit, por_trend, por_trend2, status, comments, schedule_id, user, proj, deleted, deleted_by,
                       deleted_on):
    conn, cursor = db_connection()
    sql = f"INSERT INTO {SCHEDULE_TABLE} (display, milestone, por_commit, por_trend, por_trend2, status, comments, schedule_id,\
            user, project, deleted, deleted_by, deleted_on) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (display, milestone, por_commit, por_trend, por_trend2, status, comments, schedule_id, user, proj, deleted, deleted_by, deleted_on)
    cursor.execute(sql, val)
    print(f'data inserted in {SCHEDULE_TABLE} ....')
    conn.commit()
    conn.close()


def update_schedule_data(data):
    conn, cursor = db_connection()
    for display, milestone, por_commit, por_trend, por_trend2, status, comments, schedule_id in data:
        sql = (f"UPDATE {SCHEDULE_TABLE} SET display = '{display}', milestone = '{milestone}', por_commit = '{por_commit}', \
                por_trend = '{por_trend}',por_trend2 = '{por_trend2}', status = '{status}', comments = '{comments}' \
                WHERE schedule_id='{schedule_id}'")
        cursor.execute(sql)
    print(f'data updated in {SCHEDULE_TABLE} ....')
    conn.commit()
    conn.close()


def load_links_data(table_name, display, links_url, comments, links_id, project, user, deleted=None,
                    deleted_by=None, deleted_on=None):
    conn, cursor = db_connection()
    if table_name == LINKS_TABLE:
        sql = f"INSERT INTO {table_name} (display, links_url, comments_links, links_id, project, user) \
                        VALUES (%s, %s, %s, %s, %s, %s)"
        val = (display, links_url, comments, links_id, project, user)
    else:
        sql = f"INSERT INTO {table_name} (display, links_url, comments_links, links_id, project, user, deleted, deleted_by, deleted_on) \
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (display, links_url, comments, links_id, project, user, deleted, deleted_by, deleted_on)

    cursor.execute(sql, val)
    print(f'data inserted in {table_name} ....')
    conn.commit()
    conn.close()


def update_links_data(display, links_url, comments, links_id):
    conn, cursor = db_connection()
    sql = f"UPDATE {LINKS_TABLE} SET display = '{display}', links_url = '{links_url}', comments_links = '{comments}' WHERE links_id='{links_id}'"
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
        query = "SELECT username, password, project FROM users WHERE username = %s"
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


def load_bbox_data(data, project, user):
    conn, cursor = db_connection()
    for row_data in data:
        category = row_data.get('category', '')
        process = row_data.get('process', '')
        die_area = row_data.get('die_area', '')
        config = row_data.get('config', '')
        pv_freq = row_data.get('pv_freq', '')
        perf_target = row_data.get('perf_target', '')
        cdyn = row_data.get('cdyn', '')
        schedule_bbox = row_data.get('schedule_bbox', '')
        bbox_id = f"{str(int(time.time() * 1000))}_{user}_{category}"
        sql = f"INSERT INTO {BBOX_TABLE} (category, process, die_area, config, pv_freq, perf_target, cdyn, schedule_bbox, project, user, bbox_id) \
        VALUES ('{category}', '{process}', '{die_area}',  '{config}', '{pv_freq}', '{perf_target}', '{cdyn}', '{schedule_bbox}', '{project}', '{user}', '{bbox_id}')"
        cursor.execute(sql)
    print(f'data inserted in {BBOX_TABLE} ....')
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


def load_issues_data(table, data):
    conn, cursor = db_connection()
    if table == ISSUES_TABLE:
        display, issues_summary, status, owner, eta, trigger_date, issues_initiated, severity, issues_id, project, user = data
        sql = f"INSERT INTO {table} (display, issues_summary, status, owner, eta, trigger_date, issues_initiated, severity, \
                    issues_id, project, user) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (display, issues_summary, status, owner, eta, trigger_date, issues_initiated, severity, issues_id, project, user)
    else:
        display, issues_summary, status, owner, eta,  trigger_date, issues_initiated, severity, issues_id, project, user, deleted, deleted_by, deleted_on = data
        sql = f"INSERT INTO {table} (display, issues_summary, status, owner, eta, trigger_date, issues_initiated, severity, \
            issues_id, project, user, deleted, deleted_by, deleted_on) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (display, issues_summary, status, owner, eta,  trigger_date, issues_initiated, severity, issues_id,
               project, user, deleted, deleted_by, deleted_on)
    cursor.execute(sql, val)
    print(f'data inserted in {table} ....')
    conn.commit()
    conn.close()


def update_issues_data(data):
    conn, cursor = db_connection()
    for display, issues_summary, status, owner, eta, trigger_date, issues_initiated, severity, issues_id in data:
        sql = (f"UPDATE {ISSUES_TABLE} SET display = '{display}', issues_summary = '{issues_summary}', status = '{status}', owner = '{owner}', \
                eta = '{eta}', trigger_date = '{trigger_date}', \
                issues_initiated = '{issues_initiated}', severity = '{severity}' \
                WHERE issues_id='{issues_id}'")
        cursor.execute(sql)
    print(f'data updated in {ISSUES_TABLE} ....')
    conn.commit()
    conn.close()


def update_deleted_record(table, deleted_by, deleted_on, row_id, row_value):
    deleted = True
    conn, cursor = db_connection()
    sql = (f"UPDATE {table} SET deleted = {deleted}, deleted_by = '{deleted_by}', \
            deleted_on = '{deleted_on}' WHERE {row_id}='{row_value}'")
    print(sql)
    cursor.execute(sql)
    print(f'data updated in {table} ....')
    conn.commit()
    conn.close()


def get_bbox_data(project):
    conn, cursor = db_connection()
    sql = f"""SELECT t.*
    FROM bbox t
    JOIN (
        SELECT category, MAX(created_on) AS max_created_at
        FROM bbox
        WHERE category IN ('Plan', 'Actual', 'Grading', 'Comments')
        GROUP BY category
    ) AS max_timestamps
    ON t.category = max_timestamps.category
    AND t.project = '{project}'
    AND t.created_on = max_timestamps.max_created_at;"""
    cursor.execute(sql)
    records = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    result = [dict(zip(columns, record)) for record in records]
    conn.commit()
    conn.close()
    return result


def get_users_data():
    """Register a new project."""
    try:
        conn, cursor = db_connection()
        query = "select username,project from users"
        cursor.execute(query)
        users = cursor.fetchall()
        if users:
            return users
        else:
            return None
    except mysql.connector.Error as err:
        print(f"Error: {err}")


def get_record(table, id_key, id_value):
    conn, cursor = db_connection()
    dict_cursor = conn.cursor(dictionary=True)
    sql = f"SELECT * FROM {table} where {id_key}='{id_value}'"
    dict_cursor.execute(sql)
    record = dict_cursor.fetchone()
    conn.close()
    return record


def delete_record(table, id_key, id_value):
    conn, cursor = db_connection()
    sql = f"delete from {table} where {id_key}='{id_value}'"
    cursor.execute(sql)
    conn.commit()
    conn.close()
    print(f'record {id_key} deleted from {table} !!!!!')


def update_project(username, project):
    conn, cursor = db_connection()
    project_json = json.dumps(project)
    sql = f"UPDATE users SET project = '{project_json}' WHERE username = '{username}'"
    cursor.execute(sql)
    print(f'data updated in users table ....')
    conn.commit()
    conn.close()