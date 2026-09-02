import tkinter as tk
from tkinter import ttk, messagebox
from pm_app.db import get_connection, add_time_log, stop_time_log
from pm_app import navigation
import time

_widgets = {}

start_time = None
running = False


def start_task_timer(user, task, timer_label):
    global start_time, running
    if not task.strip():
        messagebox.showerror("Error", "Enter a task name!")
        return
    if not running:
        start_time = time.time()
        running = True
        _update_timer(start_time, timer_label)
        add_time_log(user, task, start_time)


def _update_timer(start, timer_label):
    if not timer_label.winfo_exists():
        return
    elapsed = int(time.time() - start)
    hours, remainder = divmod(elapsed, 3600)
    minutes, seconds = divmod(remainder, 60)
    timer_label.config(text=f"Elapsed Time: {hours:02}:{minutes:02}:{seconds:02}")
    timer_label.after(1000, lambda: _update_timer(start, timer_label))


def stop_task_timer(user, task):
    global running, start_time
    if not task.strip():
        messagebox.showerror("Error", "Enter a task name!")
        return
    if running:
        running = False
        end_time = time.time()
        duration = end_time - start_time
        duration_minutes = round(duration / 60, 2)
        stop_time_log(user, task, end_time, duration)
        messagebox.showinfo("Timer Stopped", f"Tracked {duration_minutes} minutes for '{task}', total time updated!")


def show_time_tracker(root, role, full_name):
    for w in root.winfo_children():
        w.destroy()
    ttk.Label(root, text="Time Tracker", font=("Arial", 16)).pack(pady=10)

    ttk.Label(root, text="Enter Task Name:").pack()
    task_var = tk.StringVar()
    task_entry = ttk.Entry(root, textvariable=task_var)
    task_entry.pack(pady=5)

    timer_label = ttk.Label(root, text="Elapsed Time: 00:00:00", font=("Arial", 14))
    timer_label.pack(pady=10)

    try:
        from pm_app.utils import RoundedButton, get_theme, load_asset
        theme = get_theme()
        ic_time = load_asset('time')
        ic_gantt = load_asset('gantt')
        start_btn = RoundedButton(root, text='Start Timer', image=ic_time, command=lambda: start_task_timer(full_name, task_var.get(), timer_label), width=140, height=36, radius=8, bg=theme['accent'], fg=theme['card_bg'], font=('Helvetica Neue', 11))
        start_btn.pack(pady=6)
        stop_btn = RoundedButton(root, text='Stop Timer', image=ic_time, command=lambda: stop_task_timer(full_name, task_var.get()), width=140, height=36, radius=8, bg=theme['card_bg'], fg=theme['fg'], font=('Helvetica Neue', 11))
        stop_btn.pack(pady=6)
        back_btn = RoundedButton(root, text='Back', image=ic_gantt, command=lambda: navigation.go_dashboard(role, full_name), width=120, height=36, radius=8, bg=theme['card_bg'], fg=theme['fg'], font=('Helvetica Neue', 11))
        back_btn.pack(pady=10)
    except Exception:
        import tkinter as _tk
        _tk.Button(root, text="Start Timer", command=lambda: start_task_timer(full_name, task_var.get(), timer_label)).pack(pady=5)
        _tk.Button(root, text="Stop Timer", command=lambda: stop_task_timer(full_name, task_var.get())).pack(pady=5)
        _tk.Button(root, text="Back to Dashboard", command=lambda: navigation.go_dashboard(role, full_name)).pack(pady=10)
