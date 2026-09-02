import tkinter as tk
from tkinter import ttk, messagebox
from pm_app.db import get_connection, get_tasks_with_rowid, update_task_by_rowid, get_usernames
from pm_app import navigation

# Module-level refs
_widgets = {}


def _load_progress_tasks():
    frame = _widgets['progress_frame']
    for widget in frame.winfo_children():
        widget.destroy()

    tree = ttk.Treeview(frame, columns=("Name", "Start Date", "Duration", "Priority", "Progress"), show="headings")
    tree.heading("Name", text="Task Name")
    tree.heading("Start Date", text="Start Date")
    tree.heading("Duration", text="Duration")
    tree.heading("Priority", text="Priority")
    tree.heading("Progress", text="Progress")
    tree.column("Name", width=100)
    tree.column("Start Date", width=80)
    tree.column("Duration", width=70)
    tree.column("Priority", width=70)
    tree.column("Progress", width=100)

    rows = get_tasks_with_rowid()
    for row in rows:
        iid = row[0]
        values = row[1:]
        tree.insert("", "end", iid=iid, values=values)
    tree.pack(fill=tk.BOTH, expand=True)
    _widgets['progress_tree'] = tree


def _update_selected_task():
    tree = _widgets.get('progress_tree')
    if not tree:
        messagebox.showerror("Error", "No tasks loaded")
        return
    selected = tree.focus()
    if not selected:
        messagebox.showerror("Error", "Please select a task to update.")
        return
    new_priority = _widgets['priority_var'].get()
    new_progress = _widgets['status_var'].get()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET priority=?, progress=? WHERE rowid=?", (new_priority, new_progress, selected))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Task updated successfully.")
    _load_progress_tasks()


def show_progress_tracking(root, role, full_name):
    for w in root.winfo_children():
        w.destroy()
    ttk.Label(root, text="Progress Tracking", font=("Arial", 16)).pack(pady=10)

    progress_frame = ttk.Frame(root)
    progress_frame.pack(fill=tk.BOTH, expand=True)
    _widgets['progress_frame'] = progress_frame

    summary = ttk.Label(root, text="📊 Overall Project Completion: 0%", font=("Arial", 12))
    summary.pack(pady=5)
    _widgets['summary_label'] = summary

    def load_tasks_internal():
        frame = progress_frame
        for widget in frame.winfo_children():
            widget.destroy()

        tree = ttk.Treeview(frame, columns=("Name", "Start", "Duration", "Priority", "Progress", "Completion", "Time Spent", "Assignee"), show="headings")
        for col in tree["columns"]:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        conn = get_connection()
        cur = conn.cursor()
        # Add optional columns if missing
        try:
            cur.execute("ALTER TABLE tasks ADD COLUMN completion REAL DEFAULT 0")
        except:
            pass
        try:
            cur.execute("ALTER TABLE tasks ADD COLUMN assignee TEXT DEFAULT ''")
        except:
            pass
        try:
            cur.execute("ALTER TABLE tasks ADD COLUMN time_spent REAL DEFAULT 0")
        except:
            pass

        rows = get_tasks_with_rowid()

        total = 0
        count = 0
        for row in rows:
            rowid = row[0]
            values = list(row[1:])
            # convert time_spent to minutes display
            try:
                minutes = int(values[6])
                values[6] = f"{minutes} min"
            except:
                values[6] = "0 min"
            tree.insert("", "end", iid=rowid, values=values)
            try:
                total += float(row[6])
                count += 1
            except:
                pass

        average = round(total / count, 2) if count > 0 else 0
        summary.config(text=f"📊 Overall Project Completion: {average}%")
        tree.pack(fill=tk.BOTH, expand=True)
        _widgets['progress_tree'] = tree

    def update_task_internal():
        tree = _widgets.get('progress_tree')
        if not tree:
            messagebox.showerror("Error", "Select a task.")
            return
        selected = tree.focus()
        if not selected:
            messagebox.showerror("Error", "Select a task.")
            return
        try:
            percent = float(_widgets['completion_entry'].get())
            if percent < 0 or percent > 100:
                raise ValueError
        except:
            messagebox.showerror("Error", "Enter valid % (0–100).")
            return
        assignee = _widgets['assignee_var'].get()
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE tasks SET priority=?, progress=?, completion=?, assignee=? WHERE rowid=?",
                    (_widgets['priority_var'].get(), _widgets['status_var'].get(), percent, assignee, selected))
        conn.commit()
        conn.close()
        load_tasks_internal()
        messagebox.showinfo("Updated", "Task updated successfully.")

    # initial load
    load_tasks_internal()

    if role == 'admin':
        editor = ttk.Frame(root)
        editor.pack(pady=10)

        ttk.Label(editor, text="Priority:").grid(row=0, column=0, padx=5)
        priority_var = tk.StringVar(value="Medium")
        _widgets['priority_var'] = priority_var
        ttk.Combobox(editor, textvariable=priority_var, values=["Low", "Medium", "High"], state="readonly").grid(row=0, column=1)

        ttk.Label(editor, text="Progress:").grid(row=0, column=2, padx=5)
        status_var = tk.StringVar(value="not started")
        _widgets['status_var'] = status_var
        ttk.Combobox(editor, textvariable=status_var, values=["not started", "in-progress", "complete"], state="readonly").grid(row=0, column=3)

        ttk.Label(editor, text="Completion (%):").grid(row=0, column=4, padx=5)
        completion_entry = ttk.Entry(editor, width=6)
        completion_entry.insert(0, "0")
        completion_entry.grid(row=0, column=5)
        _widgets['completion_entry'] = completion_entry

        ttk.Label(editor, text="Assignee:").grid(row=0, column=6, padx=5)
        assignee_var = tk.StringVar()
        _widgets['assignee_var'] = assignee_var
        assignee_box = ttk.Combobox(editor, textvariable=assignee_var, state="readonly", width=12)
        assignee_box.grid(row=0, column=7)

        # Populate usernames
        assignee_box['values'] = get_usernames()

        try:
            from pm_app.utils import RoundedButton, get_theme
            theme = get_theme()
            upd = RoundedButton(root, text='✅ Update Selected Task', command=_update_selected_task, width=220, height=40, radius=10, bg=theme['accent'], fg=theme['card_bg'], font=('Helvetica Neue', 11))
            upd.pack(pady=8)
        except Exception:
            import tkinter as _tk
            _tk.Button(root, text="Update Selected Task", command=_update_selected_task).pack(pady=5)

    try:
        from pm_app.utils import RoundedButton, get_theme
        theme = get_theme()
        back = RoundedButton(root, text='◀️ Back', command=lambda: navigation.go_dashboard(role, full_name), width=220, height=36, radius=8, bg=theme['card_bg'], fg=theme['fg'], font=('Helvetica Neue', 11))
        back.pack(pady=10)
    except Exception:
        import tkinter as _tk
        _tk.Button(root, text="Back to Dashboard", command=lambda: navigation.go_dashboard(role, full_name)).pack(pady=10)

    # Resize & center main window to fit new UI
    try:
        from pm_app.utils import center_window
        root.update_idletasks()
        w = root.winfo_reqwidth() + 40
        h = root.winfo_reqheight() + 40
        center_window(root, w, h, parent=root)
    except Exception:
        pass
