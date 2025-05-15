import mysql.connector
from sqlalchemy import values

from .config import HOST, USER, PASSWORD
from .config import KEY_MESSAGE_TABLE, RISK_TABLE, KEY_PROGRAM_METRIC_TABLE
from .config import DETAILS_TABLE, SCHEDULE_TABLE, LINKS_TABLE, BBOX_TABLE, ISSUES_TABLE
import json
import bcrypt
import time
import ast


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
    display, risk_summary, risk_area, status, owner, consequence, mitigations, trigger_date, risk_initiated, impact, risk_id, project, user = data
    sql = f"INSERT INTO {table} (display, risk_summary, risk_area, status, owner, consequence, mitigations, trigger_date, risk_initiated, impact, \
        risk_id, project, user) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (display, risk_summary, risk_area, status, owner, consequence, mitigations, trigger_date, risk_initiated, impact, risk_id, project, user)
    cursor.execute(sql, val)
    print(f'data inserted in {table} ....')
    conn.commit()
    conn.close()


def get_key_msg_or_details_data(table, project):
    conn, cursor = db_connection()
    sql = f"SELECT * FROM {table} WHERE project = %s ORDER BY ts DESC LIMIT 1"
    cursor.execute(sql, (project,))
    row = cursor.fetchone()
    result = dict(zip([col[0] for col in cursor.description], row)) if row else {}
    conn.close()
    return result


def get_data(user, table, project, deleted=None):
    conn, cursor = db_connection()
    sql = f"SELECT * FROM {table} WHERE project = %s"
    values = [project]
    if deleted is not None:
        sql += " AND deleted = %s"
        values.append(deleted)
    cursor.execute(sql, tuple(values))
    records = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    result = [dict(zip(columns, record)) for record in records]
    conn.close()
    return result


def get_schedule_record(pk):
    conn, cursor = db_connection()
    sql = f"SELECT * FROM {SCHEDULE_TABLE} WHERE schedule_id = %s"
    cursor.execute(sql, (pk,))
    records = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    result = [dict(zip(columns, record)) for record in records]
    conn.close()
    return result


def update_risk_data(data):
    conn, cursor = db_connection()
    sql = f"""
        UPDATE {RISK_TABLE}
        SET display = %s, risk_summary = %s, risk_area = %s, status = %s, owner = %s,
            consequence = %s, mitigations = %s, trigger_date = %s,
            risk_initiated = %s, impact = %s
        WHERE risk_id = %s
    """
    for row in data:
        display, risk_summary, risk_area, status, owner, consequence, mitigations, trigger_date, risk_initiated, impact, risk_id = row
        values = (
            display, risk_summary, risk_area, status, owner,
            consequence, mitigations, trigger_date, risk_initiated, impact, risk_id
        )
        cursor.execute(sql, values)
    print(f'Data updated in {RISK_TABLE} ...')
    conn.commit()
    conn.close()


def load_key_program_metric_data(data, table):
    conn, cursor = db_connection()
    sql = f"""
        INSERT INTO {table} (
            display, metric, fv_target, current_week_actual,
            current_week_plan, status, comments, metric_id, project, user
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(sql, data)
    print(f'Data inserted in {table} ...')
    conn.commit()
    conn.close()


def update_key_program_metric_data(data):
    conn, cursor = db_connection()
    sql = f"""
        UPDATE {KEY_PROGRAM_METRIC_TABLE}
        SET display = %s, metric = %s, fv_target = %s,
            current_week_actual = %s, current_week_plan = %s,
            status = %s, comments = %s
        WHERE metric_id = %s
    """
    for row in data:
        display, metric, fv_target, cwa, cwp, status, comments, metric_id = row
        values = (display, metric, fv_target, cwa, cwp, status, comments, metric_id)
        cursor.execute(sql, values)
    print(f'Data updated in {KEY_PROGRAM_METRIC_TABLE} ...')
    conn.commit()
    conn.close()


def delete_key_program_metric_data(metric_id):
    conn, cursor = db_connection()
    sql = f"DELETE FROM {KEY_PROGRAM_METRIC_TABLE} WHERE metric_id = %s"
    cursor.execute(sql, (metric_id,))
    print(f'Data deleted in {KEY_PROGRAM_METRIC_TABLE} ... {metric_id}')
    conn.commit()
    conn.close()


def drop_table(table):
    conn, cursor = db_connection()
    sql = f"DROP TABLE {table}"
    cursor.execute(sql)
    print(f'data deleted ')
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


def load_schedule_data(display, milestone, por_commit, por_trend, status, comments, schedule_id, user, proj, ts, deleted, deleted_by,
                       deleted_on):
    conn, cursor = db_connection()
    sql = f"INSERT INTO {SCHEDULE_TABLE} (display, milestone, por_commit, por_trend, status, comments, schedule_id,\
            user, project, ts,  deleted, deleted_by, deleted_on) VALUES (%s, %s, %s, %s, %s,  %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (display, milestone, por_commit, por_trend, status, comments, schedule_id, user, proj, ts, deleted, deleted_by, deleted_on)
    cursor.execute(sql, val)
    print(f'data inserted in {SCHEDULE_TABLE} ....')
    conn.commit()
    conn.close()


def update_schedule_data(data):
    conn, cursor = db_connection()
    sql = f"""
        UPDATE {SCHEDULE_TABLE}
        SET display = %s, milestone = %s, por_commit = %s, por_trend = %s,
            status = %s, comments = %s
        WHERE schedule_id = %s
    """
    for display, milestone, por_commit, por_trend, status, comments, schedule_id in data:
        values = (display, milestone, por_commit, por_trend, status, comments, schedule_id)
        cursor.execute(sql, values)
    print(f'Data updated in {SCHEDULE_TABLE}...')
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
    sql = f"""
        UPDATE {LINKS_TABLE}
        SET display = %s, links_url = %s, comments_links = %s
        WHERE links_id = %s
    """
    values = (display, links_url, comments, links_id)
    cursor.execute(sql, values)
    print(f'Data updated in {links_id} ...')
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
                return (None, None)
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


def get_distinct_metric(project_name):
    """Fetch distinct metric names for a given project."""
    try:
        conn, cursor = db_connection()
        query = "SELECT DISTINCT(metric) FROM key_program_metric_table WHERE project = %s"
        cursor.execute(query, (project_name,))
        metric = cursor.fetchall()
        if metric:
            return [i[0] for i in metric]
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
    insert_query = f"""
        INSERT INTO {BBOX_TABLE} (
            category, process, die_area, config, pv_freq,
            perf_target, cdyn, schedule_bbox, project, user, bbox_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
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
        values = (
            category, process, die_area, config, pv_freq,
            perf_target, cdyn, schedule_bbox, project, user, bbox_id
        )

        # print(cursor.mogrify(insert_query, values))  # optional: print final query with values
        cursor.execute(insert_query, values)
    print(f'Data inserted into {BBOX_TABLE}...')
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
    except Exception:
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
    sql = f"""
        UPDATE {ISSUES_TABLE}
        SET display = %s,
            issues_summary = %s,
            status = %s,
            owner = %s,
            eta = %s,
            trigger_date = %s,
            issues_initiated = %s,
            severity = %s
        WHERE issues_id = %s
    """
    for row in data:
        values = tuple(row)  # or unpack: (display, issues_summary, ..., issues_id)
        cursor.execute(sql, values)

    print(f'Data updated in {ISSUES_TABLE} ...')
    conn.commit()
    conn.close()


def update_deleted_record(table, deleted_by, deleted_on, row_id, row_value):
    deleted = True
    conn, cursor = db_connection()
    sql = f"""
        UPDATE {table}
        SET deleted = %s,
            deleted_by = %s,
            deleted_on = %s
        WHERE {row_id} = %s
    """
    values = (deleted, deleted_by, deleted_on, row_value)
    cursor.execute(sql, values)
    print(f'Data marked as deleted in {table} ...')
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
    sql = f"SELECT * FROM {table} WHERE {id_key} = %s"
    dict_cursor.execute(sql, (id_value,))
    record = dict_cursor.fetchone()
    conn.close()
    return record


def delete_record(table, id_key, id_value):
    conn, cursor = db_connection()
    sql = f"DELETE FROM {table} WHERE {id_key} = %s"
    cursor.execute(sql, (id_value,))
    conn.commit()
    conn.close()
    print(f"Record with {id_key} = {id_value} deleted from {table}")


def update_project(username, project):
    conn, cursor = db_connection()
    project_json = json.dumps(project)
    sql = "UPDATE users SET project = %s WHERE username = %s"
    values = (project_json, username)
    cursor.execute(sql, values)
    print("Data updated in users table ...")
    conn.commit()
    conn.close()


def get_projects_data():
    conn, cursor = db_connection()
    dict_cursor = conn.cursor(dictionary=True)
    sql = f"SELECT * FROM project_data"
    dict_cursor.execute(sql)
    records = dict_cursor.fetchall()
    conn.close()
    return records



def delete_project_from_db(project_name):
    conn, cursor = db_connection()
    sql = "DELETE FROM project_data WHERE project = %s"
    cursor.execute(sql, (project_name,))
    print(f'Project deleted from database ... {project_name}')
    conn.commit()
    conn.close()


def update_project_list(project, pk):
    conn, cursor = db_connection()
    sql = "UPDATE project_data SET project = %s WHERE pk = %s"
    cursor.execute(sql, (project, pk))
    print(f'Data updated in project table ...')
    conn.commit()
    conn.close()


def update_user_projects(old_proj, new_proj, delete_flag=False):
    conn, cursor = db_connection()
    dict_cursor = conn.cursor(dictionary=True)
    sql = f"SELECT * FROM users"
    dict_cursor.execute(sql)
    records = dict_cursor.fetchall()
    for rec in records:
        projects = ast.literal_eval(rec.get('project')) or []
        if old_proj in projects:
            ''' delete the data when the flag is true'''
            if delete_flag:
                projects.remove(old_proj)
                update_project(rec.get('username'), projects)
            else:
                proj_index = projects.index(old_proj)
                projects[proj_index] = new_proj
                update_project(rec.get('username'), projects)


def get_old_project(pk):
    conn, cursor = db_connection()
    dict_cursor = conn.cursor(dictionary=True)
    sql = "SELECT project FROM project_data WHERE pk = %s"
    dict_cursor.execute(sql, (pk,))
    proj_data = dict_cursor.fetchone()
    conn.close()
    return proj_data.get('project') if proj_data else None


def create_project_status(project_name, quantity_type, status, created_by, modified_by):
    """ create project status record in db"""
    try:
        conn, cursor = db_connection()
        query = f"INSERT INTO project_status (project_name, quantity_type, status, created_by, modified_by) VALUES (%s, %s, %s, %s, %s)"
        data = (project_name, quantity_type, status, created_by, modified_by)
        cursor.execute(query, data)
        conn.commit()
        print(f"project status created successfully for {project_name}!")
    except mysql.connector.Error as err:
        print(f"Error: {err}")


def get_project_status(project_name, quantity_type):
    conn, cursor = db_connection()
    dict_cursor = conn.cursor(dictionary=True)
    sql = "SELECT * FROM project_status WHERE project_name = %s AND quantity_type = %s"
    dict_cursor.execute(sql, (project_name, quantity_type))
    record = dict_cursor.fetchone()
    conn.close()
    return record or {}

def update_project_status(project_name, quantity_type, status, modified_by):
    conn, cursor = db_connection()
    sql = """
        UPDATE project_status
        SET status = %s, modified_by = %s
        WHERE project_name = %s AND quantity_type = %s
    """
    values = (status, modified_by, project_name, quantity_type)
    cursor.execute(sql, values)
    print(f'Data updated in project_status table for {project_name}...')
    conn.commit()
    conn.close()

def upload_image_data(name, image, project_name, user):
    conn, cursor = db_connection()
    cursor.execute(
        "INSERT INTO image_table (name, image, project, user) VALUES (%s, %s, %s, %s)",
        [name, image, project_name, user]
    )
    conn.commit()
    conn.close()

def update_image_data(id, name, image, project_name, user):
    conn, cursor = db_connection()
    sql = """
            UPDATE image_table
            SET name = %s, image = %s, project = %s, user = %s
            WHERE id = %s
        """
    values = (name, image, project_name, user, id)
    cursor.execute(sql, values)
    conn.commit()
    conn.close()

def get_latest_timestamp(table, project):
    conn, cursor = db_connection()
    dict_cursor = conn.cursor(dictionary=True)
    sql = f"SELECT MAX(ts) as ts FROM `{table}` WHERE project = %s"
    values = (project,)
    dict_cursor.execute(sql, values)
    record = dict_cursor.fetchone()
    conn.close()
    return record or {}


def get_risk_data(project_name):
    conn, cursor = db_connection()
    sql = """
        SELECT *
        FROM risk_table
        WHERE project = %s
          AND status IN ('Open', 'Closed')
          AND display IN ('On', 'Off')
        ORDER BY 
          CASE 
            WHEN display = 'On' AND status = 'Open' THEN 1
            WHEN display = 'Off' AND status = 'Open' THEN 2
            WHEN display = 'On' AND status = 'Closed' THEN 3
            WHEN display = 'Off' AND status = 'Closed' THEN 4
            ELSE 5
          END,
          trigger_date ASC;
    """
    val = (project_name,)
    cursor.execute(sql, val)
    records = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    result = [dict(zip(columns, record)) for record in records]
    conn.close()
    return result

