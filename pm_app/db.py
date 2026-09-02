import sqlite3

DB_FILE = "user_auth.db"


def get_connection():
    return sqlite3.connect(DB_FILE)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT UNIQUE, password TEXT, role TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS tasks (name TEXT, start_date TEXT, duration INTEGER)")
    conn.commit()

    # Add optional columns safely
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE tasks ADD COLUMN priority TEXT DEFAULT 'Medium'")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE tasks ADD COLUMN progress TEXT DEFAULT 'not started'")
    except sqlite3.OperationalError:
        pass

    # Budgets table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        project TEXT,
        requested_amount REAL,
        allocated_amount REAL DEFAULT 0,
        spent_amount REAL DEFAULT 0,
        status TEXT DEFAULT 'pending'
    )''')

    # Time logs
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS time_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        project TEXT,
        start_time REAL,
        end_time REAL DEFAULT NULL,
        duration REAL DEFAULT 0
    )''')

    conn.commit()
    conn.close()


def add_task(name, start_date, duration, priority="Medium", progress="not started"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (name, start_date, duration, priority, progress) VALUES (?, ?, ?, ?, ?)",
                (name, start_date, duration, priority, progress))
    conn.commit()
    conn.close()


def get_tasks():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, start_date, duration, priority, progress FROM tasks")
    rows = cur.fetchall()
    conn.close()
    return rows


def get_tasks_with_rowid():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT rowid, name, start_date, duration, priority, progress, completion, time_spent, assignee FROM tasks")
    rows = cur.fetchall()
    conn.close()
    return rows


def delete_task_by_name(name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE name=?", (name,))
    conn.commit()
    conn.close()


def update_task_by_rowid(rowid, priority=None, progress=None, completion=None, assignee=None):
    conn = get_connection()
    cur = conn.cursor()
    # Build update dynamically
    updates = []
    params = []
    if priority is not None:
        updates.append("priority=?")
        params.append(priority)
    if progress is not None:
        updates.append("progress=?")
        params.append(progress)
    if completion is not None:
        updates.append("completion=?")
        params.append(completion)
    if assignee is not None:
        updates.append("assignee=?")
        params.append(assignee)
    if updates:
        sql = f"UPDATE tasks SET {', '.join(updates)} WHERE rowid=?"
        params.append(rowid)
        cur.execute(sql, tuple(params))
        conn.commit()
    conn.close()


def get_usernames():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT username FROM users")
    rows = [r[0] for r in cur.fetchall()]
    conn.close()
    return rows


def add_time_log(user, project, start_time):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO time_logs (user, project, start_time) VALUES (?, ?, ?)", (user, project, start_time))
    conn.commit()
    conn.close()


def stop_time_log(user, project, end_time, duration):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE time_logs SET end_time=?, duration=? WHERE user=? AND project=? AND end_time IS NULL",
                (end_time, duration, user, project))
    # update tasks' time_spent in minutes
    cur.execute("UPDATE tasks SET time_spent = COALESCE(time_spent, 0) + ? WHERE name=?", (round(duration/60,2), project))
    conn.commit()
    conn.close()


def add_budget_request(user, project, amount):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO budgets (user, project, requested_amount, status) VALUES (?, ?, ?, 'pending')", (user, project, amount))
    conn.commit()
    conn.close()


def get_pending_budgets():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, user, project, requested_amount, allocated_amount, spent_amount, status FROM budgets WHERE status='pending'")
    rows = cur.fetchall()
    conn.close()
    return rows


def approve_budget_request(request_id, amount):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE budgets SET allocated_amount=?, status='approved' WHERE id=?", (amount, request_id))
    conn.commit()
    conn.close()


def reject_budget_request(request_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE budgets SET status='rejected' WHERE id=?", (request_id,))
    conn.commit()
    conn.close()


def record_expense(project, amount):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE budgets SET spent_amount=spent_amount + ? WHERE project=?", (amount, project))
    conn.commit()
    conn.close()
