import tkinter as tk
from tkinter import ttk, messagebox
from pm_app.db import get_connection, add_task, get_tasks, delete_task_by_name
from pm_app import navigation
import datetime

# Module-level widget refs
_tm_widgets = {}


def _add_task():
    name = _tm_widgets['name_entry'].get().strip()
    start_date = _tm_widgets['date_entry'].get().strip()
    duration = _tm_widgets['duration_entry'].get().strip()

    if not name or not start_date or not duration:
        messagebox.showerror("Error", "All fields must be filled!")
        return
    try:
        datetime.datetime.strptime(start_date, "%Y-%m-%d")
        duration = int(duration)
    except ValueError:
        messagebox.showerror("Error", "Invalid date format or duration!")
        return

    add_task(name, start_date, duration, "Medium", "not started")
    messagebox.showinfo("Success", "Task added successfully!")
    _view_tasks()

    # Resize & center main window to fit new UI
    try:
        from pm_app.utils import center_window
        root.update_idletasks()
        # ensure a reasonable size minimum
        w = max(600, root.winfo_reqwidth() + 40)
        h = max(400, root.winfo_reqheight() + 40)
        root.geometry(f"{w}x{h}")
        center_window(root, w, h, parent=root)
    except Exception:
        pass

    # Resize & center main window to fit new UI
    try:
        from pm_app.utils import center_window
        root.update_idletasks()
        w = root.winfo_reqwidth() + 40
        h = root.winfo_reqheight() + 40
        center_window(root, w, h, parent=root)
    except Exception:
        pass


def _view_tasks(clear_frame=True):
    frame = _tm_widgets['list_frame']
    for widget in frame.winfo_children():
        widget.destroy()

    tasks = get_tasks()

    tree = ttk.Treeview(frame, columns=("Name", "Start Date", "Duration", "Priority", "Progress"), show="headings")
    tree.heading("Name", text="Task Name")
    tree.heading("Start Date", text="Start Date")
    tree.heading("Duration", text="Duration (Days)")
    tree.heading("Priority", text="Priority")
    tree.heading("Progress", text="Progress")
    tree.column("Name", width=100)
    tree.column("Start Date", width=80)
    tree.column("Duration", width=70)
    tree.column("Priority", width=70)
    tree.column("Progress", width=100)
    for task in tasks:
        tree.insert("", "end", values=task)
    tree.pack(fill=tk.BOTH, expand=True)


def _delete_task(name):
    delete_task_by_name(name)
    messagebox.showinfo("Task Deleted", f"Task '{name}' has been removed.")
    _view_tasks()


def _delete_task_ui():
    win = tk.Toplevel(_tm_widgets['root'])
    win.title("Delete Task")
    try:
        from pm_app.utils import center_window
    except Exception:
        center_window = None
    if center_window:
        center_window(win, 300, 120, parent=_tm_widgets['root'])
    ttk.Label(win, text="Task Name to Delete:").pack()
    entry = ttk.Entry(win)
    entry.pack()
    try:
        from pm_app.utils import RoundedButton
        btn = RoundedButton(win, text='Delete', command=lambda: _delete_task(entry.get()), width=120, height=36, radius=8, bg='#e53e3e', fg='white', font=('Helvetica Neue', 11))
        btn.pack(pady=5)
    except Exception:
        import tkinter as _tk
        _tk.Button(win, text="Delete", command=lambda: _delete_task(entry.get())).pack(pady=5)


def show_task_management(root, role, full_name):
    # store root
    _tm_widgets['root'] = root

    for widget in root.winfo_children():
        widget.destroy()
    ttk.Label(root, text="Task Management", font=("Arial", 16)).pack(pady=10)

    if role == 'admin':
        lbl = ttk.Label(root, text="Task Name:")
        lbl.pack()
        name_entry = ttk.Entry(root)
        name_entry.pack()
        _tm_widgets['name_entry'] = name_entry

        ttk.Label(root, text="Start Date (YYYY-MM-DD):").pack()
        date_entry = ttk.Entry(root)
        date_entry.pack()
        _tm_widgets['date_entry'] = date_entry

        ttk.Label(root, text="Duration (Days):").pack()
        duration_entry = ttk.Entry(root)
        duration_entry.pack()
        _tm_widgets['duration_entry'] = duration_entry

        # Styled rounded buttons if available
        try:
            from pm_app.utils import RoundedButton, get_theme, load_asset
            theme = get_theme()
            ic_task = load_asset('task')
            add_btn = RoundedButton(root, text='Add Task', image=ic_task, command=_add_task, width=140, height=40, radius=10, bg=theme['accent'], fg=theme['card_bg'], font=('Helvetica Neue', 11))
            add_btn.pack(pady=6)
            del_btn = RoundedButton(root, text='Delete Task', image=ic_task, command=_delete_task_ui, width=140, height=40, radius=10, bg=theme['card_bg'], fg=theme['fg'], font=('Helvetica Neue', 11))
            del_btn.pack(pady=6)
        except Exception:
            import tkinter as _tk
            _tk.Button(root, text="Add Task", command=_add_task).pack(pady=5)
            _tk.Button(root, text="Delete Task", command=_delete_task_ui).pack(pady=5)

    list_frame = ttk.Frame(root)
    list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    _tm_widgets['list_frame'] = list_frame

    try:
        from pm_app.utils import RoundedButton, get_theme
        theme = get_theme()
        from pm_app.utils import load_asset
        ic_progress = load_asset('progress')
        ref_btn = RoundedButton(root, text='Refresh Task List', image=ic_progress, command=_view_tasks, width=180, height=36, radius=8, bg=theme['card_bg'], fg=theme['fg'], font=('Helvetica Neue', 11))
        ref_btn.pack(pady=6)
        ic_gantt = load_asset('gantt')
        back_btn = RoundedButton(root, text='Back', image=ic_gantt, command=lambda: navigation.go_dashboard(role, full_name), width=120, height=36, radius=8, bg=theme['card_bg'], fg=theme['fg'], font=('Helvetica Neue', 11))
        back_btn.pack(pady=10)
    except Exception:
        import tkinter as _tk
        _tk.Button(root, text="Refresh Task List", command=_view_tasks).pack(pady=5)
        _tk.Button(root, text="Back to Dashboard", command=lambda: navigation.go_dashboard(role, full_name)).pack(pady=10)

    _view_tasks()
