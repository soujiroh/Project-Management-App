import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
try:
    import pandas as pd
except Exception:
    pd = None
try:
    import matplotlib
    import matplotlib.pyplot as plt
except Exception:
    matplotlib = None
    plt = None
import datetime
import time
import csv
import os
try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
except Exception:
    FigureCanvasTkAgg = None

# Use modularized DB and analytics helpers
from pm_app.db import init_db, get_connection
from pm_app.analytics import save_to_csv_analytics
from pm_app import navigation
from pm_app.ui_tasks import show_task_management as show_task_management_module
from pm_app.db import get_tasks
try:
    import matplotlib.dates as mdates
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
    MPL_AVAILABLE = True
except Exception:
    mdates = None
    Figure = None
    NavigationToolbar2Tk = None
    MPL_AVAILABLE = False

try:
    import mplcursors
    MPLCURSORS_AVAILABLE = True
except Exception:
    MPLCURSORS_AVAILABLE = False

# Initialize DB
init_db()



def show_task_management(role, full_name):
    return show_task_management_module(root, role, full_name)


def show_gantt_chart(role, full_name):
    # Create a simple Gantt chart in a Toplevel using matplotlib
    try:
        if not MPL_AVAILABLE or Figure is None or mdates is None or FigureCanvasTkAgg is None:
            messagebox.showerror("Gantt Error", "Matplotlib is not available in this environment.")
            return
        tasks = get_tasks()
        if not tasks:
            messagebox.showinfo("Gantt Chart", "No tasks to display.")
            return
        gantt_win = tk.Toplevel(root)
        gantt_win.title("Gantt Chart")

        # Prepare data
        names = []
        starts = []
        durations = []
        for t in tasks:
            name, start_str, dur = t[0], t[1], t[2]
            try:
                dt = datetime.datetime.strptime(start_str, "%Y-%m-%d")
            except Exception:
                dt = datetime.datetime.now()
            names.append(name)
            starts.append(mdates.date2num(dt))
            durations.append(int(dur))

        fig = Figure(figsize=(8, max(3, len(names) * 0.6)))
        ax = fig.add_subplot(111)
        bars = ax.barh(range(len(names)), durations, left=starts, align='center')
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names)
        ax.xaxis_date()
        ax.set_xlabel('Date')
        ax.set_title('Gantt Chart')

        # format dates
        try:
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(mdates.AutoDateLocator()))
        except Exception:
            pass

        canvas = FigureCanvasTkAgg(fig, master=gantt_win)
        canvas.draw()
        widget = canvas.get_tk_widget()
        widget.pack(fill=tk.BOTH, expand=True)

        # add navigation toolbar for pan/zoom
        try:
            toolbar = NavigationToolbar2Tk(canvas, gantt_win)
            toolbar.update()
            toolbar.pack(side=tk.TOP, fill=tk.X)
        except Exception:
            pass

        # hover tooltips (mplcursors) and click handler
        def _on_click(event):
            if event.inaxes != ax:
                return
            # find nearest bar by y coordinate
            y = event.ydata
            if y is None:
                return
            idx = int(round(y))
            if idx < 0 or idx >= len(names):
                return
            name = names[idx]
            start = mdates.num2date(starts[idx]).strftime('%Y-%m-%d')
            dur = durations[idx]
            # detail window
            det = tk.Toplevel(gantt_win)
            det.title(f"Task: {name}")
            ttk.Label(det, text=f"Task: {name}").pack(pady=5)
            ttk.Label(det, text=f"Start: {start}").pack()
            ttk.Label(det, text=f"Duration (days): {dur}").pack()
            try:
                from pm_app.utils import RoundedButton
                ob = RoundedButton(det, text='Open in Task Management', command=lambda: show_task_management('admin', full_name), width=240, height=36, radius=8, bg='#111827', fg='#06b6d4', font=('Helvetica Neue', 11))
                ob.pack(pady=10)
            except Exception:
                import tkinter as _tk
                _tk.Button(det, text="Open in Task Management", command=lambda: show_task_management('admin', full_name)).pack(pady=10)
            try:
                from pm_app.utils import center_window
                det.update_idletasks()
                center_window(det, det.winfo_reqwidth()+40, det.winfo_reqheight()+40, parent=gantt_win)
            except Exception:
                pass

        widget.bind("<Button-1>", lambda ev: _on_click(ev))

        if MPLCURSORS_AVAILABLE:
            try:
                cr = mplcursors.cursor(bars, hover=True)
                @cr.connect("add")
                def on_add(sel):
                    i = sel.target.index
                    dt = mdates.num2date(starts[i]).strftime('%Y-%m-%d')
                    sel.annotation.set(text=f"{names[i]}\nStart: {dt}\nDur: {durations[i]}d")
            except Exception:
                pass

        # center window after it's built
        try:
            from pm_app.utils import center_window
            gantt_win.update_idletasks()
            w = gantt_win.winfo_reqwidth() + 40
            h = gantt_win.winfo_reqheight() + 40
            center_window(gantt_win, w, h, parent=root)
        except Exception:
            pass
    except Exception as e:
        messagebox.showerror("Gantt Error", f"Could not build Gantt chart: {e}")

from pm_app.ui_progress import show_progress_tracking as show_progress_tracking_module


def show_progress_tracking(role, full_name):
    return show_progress_tracking_module(root, role, full_name)

from pm_app.ui_time import show_time_tracker as show_time_tracker_module


def show_time_tracker(role, full_name):
    return show_time_tracker_module(root, role, full_name)


# ---------------- Budget Management Functions ----------------
from pm_app.ui_budget import show_budget_management as show_budget_management_module


def show_budget_management(role, full_name):
    return show_budget_management_module(root, role, full_name)



# ---------------- Dashboard and Navigation ----------------
def show_dashboard(role, full_name):
    # build a modern card-style dashboard with rounded buttons
    for widget in root.winfo_children():
        widget.destroy()

    # visual variables consistent with login
    accent = '#06b6d4'
    bg = '#0f1724'
    card_bg = '#111827'
    fg = '#e6eef6'

    root.configure(bg=bg)

    card = ttk.Frame(root, padding=(20, 18), style='Card.TFrame')
    card.place(relx=0.5, rely=0.5, anchor='center')

    header = ttk.Label(card, text=f"Welcome {full_name}", font=('Helvetica', 16, 'bold'), background=card_bg, foreground=fg)
    header.grid(row=0, column=0, columnspan=2, sticky='w', pady=(0,10))

    sub = ttk.Label(card, text=f"Role: {role.title()}", font=('Helvetica', 10), background=card_bg, foreground=fg)
    sub.grid(row=1, column=0, columnspan=1, sticky='w', pady=(0,12))

    # High-contrast accessibility toggle
    try:
        from pm_app.utils import set_high_contrast, HIGH_CONTRAST
        hc_var = tk.BooleanVar(value=HIGH_CONTRAST)
        def _toggle_hc():
            set_high_contrast(hc_var.get())
            # re-render dashboard to apply theme
            show_dashboard(role, full_name)
        chk = ttk.Checkbutton(card, text='High Contrast', variable=hc_var, command=_toggle_hc)
        chk.grid(row=1, column=1, sticky='e')
    except Exception:
        pass

    # menu buttons
    try:
        from pm_app.utils import RoundedButton, load_asset
        btn_font = ('Helvetica Neue', 12)
        # load icons (may return None)
        ic_progress = load_asset('progress')
        ic_task = load_asset('task')
        ic_time = load_asset('time')
        ic_gantt = load_asset('gantt')
        ic_budget = load_asset('budget')
        ic_logout = load_asset('logout')

        b1 = RoundedButton(card, text='Progress', image=ic_progress, command=lambda: show_progress_tracking(role, full_name), width=160, height=48, radius=12, bg=accent, fg=card_bg, font=btn_font)
        b1.grid(row=2, column=0, padx=10, pady=8)
        ttk.Label(card, text='Track project progress', background=card_bg, foreground=fg).grid(row=3, column=0)

        b2 = RoundedButton(card, text='Tasks', image=ic_task, command=lambda: show_task_management(role, full_name), width=160, height=48, radius=12, bg=accent, fg=card_bg, font=btn_font)
        b2.grid(row=2, column=1, padx=10, pady=8)
        ttk.Label(card, text='Create and manage tasks', background=card_bg, foreground=fg).grid(row=3, column=1)

        b3 = RoundedButton(card, text='Time Tracker', image=ic_time, command=lambda: show_time_tracker(role, full_name), width=160, height=48, radius=12, bg=accent, fg=card_bg, font=btn_font)
        b3.grid(row=4, column=0, padx=10, pady=8)
        ttk.Label(card, text='Log time on tasks', background=card_bg, foreground=fg).grid(row=5, column=0)

        b4 = RoundedButton(card, text='Gantt', image=ic_gantt, command=lambda: show_gantt_chart(role, full_name), width=160, height=48, radius=12, bg=accent, fg=card_bg, font=btn_font)
        b4.grid(row=4, column=1, padx=10, pady=8)
        ttk.Label(card, text='View project timeline', background=card_bg, foreground=fg).grid(row=5, column=1)

        b5 = RoundedButton(card, text='Budget', image=ic_budget, command=lambda: show_budget_management(role, full_name), width=340, height=48, radius=12, bg='#0b1220', fg=accent, font=btn_font)
        b5.grid(row=6, column=0, columnspan=2, pady=(12,6))
        ttk.Label(card, text='Manage budgets and expenses', background=card_bg, foreground=fg).grid(row=7, column=0, columnspan=2)

        # logout small button
        out_btn = RoundedButton(card, text='Logout', image=ic_logout, command=logout, width=120, height=36, radius=10, bg='#3b4552', fg=fg, font=('Helvetica Neue', 11))
        out_btn.grid(row=8, column=0, columnspan=2, pady=(12,0))
    except Exception:
        # fallback to simple ttk buttons
        try:
            from pm_app.utils import RoundedButton, get_theme
            theme = get_theme()
            RoundedButton(card, text='Progress Tracking', command=lambda: show_progress_tracking(role, full_name), width=180, height=36, radius=8, bg=theme['card_bg'], fg=theme['fg']).grid(row=2, column=0, pady=4)
            RoundedButton(card, text='Task Management', command=lambda: show_task_management(role, full_name), width=180, height=36, radius=8, bg=theme['card_bg'], fg=theme['fg']).grid(row=2, column=1, pady=4)
            RoundedButton(card, text='Time Tracker', command=lambda: show_time_tracker(role, full_name), width=180, height=36, radius=8, bg=theme['card_bg'], fg=theme['fg']).grid(row=3, column=0, pady=4)
            RoundedButton(card, text='Gantt Chart', command=lambda: show_gantt_chart(role, full_name), width=180, height=36, radius=8, bg=theme['card_bg'], fg=theme['fg']).grid(row=3, column=1, pady=4)
            RoundedButton(card, text='Budget Management', command=lambda: show_budget_management(role, full_name), width=380, height=40, radius=8, bg=theme['accent'], fg=theme['card_bg']).grid(row=4, column=0, columnspan=2, pady=8)
            RoundedButton(card, text='Logout', command=logout, width=380, height=40, radius=8, bg=theme['card_bg'], fg=theme['fg']).grid(row=5, column=0, columnspan=2, pady=8)
        except Exception:
            import tkinter as _tk
            _tk.Button(card, text="Progress Tracking", command=lambda: show_progress_tracking(role, full_name)).grid(row=2, column=0, pady=4)
            _tk.Button(card, text="Task Management", command=lambda: show_task_management(role, full_name)).grid(row=2, column=1, pady=4)
            _tk.Button(card, text="Time Tracker", command=lambda: show_time_tracker(role, full_name)).grid(row=3, column=0, pady=4)
            _tk.Button(card, text="Gantt Chart", command=lambda: show_gantt_chart(role, full_name)).grid(row=3, column=1, pady=4)
            _tk.Button(card, text="Budget Management", command=lambda: show_budget_management(role, full_name)).grid(row=4, column=0, columnspan=2, pady=8)
            _tk.Button(card, text="Logout", command=logout).grid(row=5, column=0, columnspan=2, pady=8)

    # resize and center root to fit card
    try:
        from pm_app.utils import center_window
        root.update_idletasks()
        w = max(720, root.winfo_reqwidth() + 80)
        h = max(520, root.winfo_reqheight() + 80)
        root.geometry(f"{w}x{h}")
        center_window(root, w, h, parent=root)
    except Exception:
        pass



# Register navigation callbacks so UI modules can call back into main
navigation.set_dashboard_callback(show_dashboard)

def login():
    uname = username_entry.get().strip()
    pwd = password_entry.get().strip()
    role = role_var.get()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT full_name FROM users WHERE username=? AND password=? AND role=?", (uname, pwd, role))
    row = cursor.fetchone()
    conn.close()

    if row:
        full_name = row[0]
        show_dashboard(role, full_name)
    else:
        messagebox.showerror("Login Failed", "Invalid credentials.")

def logout():
    global root
    root.destroy()  # Closes current window
    main_screen()

def register_user():
    def perform_registration():
        uname = reg_username_entry.get().strip()
        fname = reg_fullname_entry.get().strip()
        pwd = reg_password_entry.get().strip()
        role = reg_role_var.get()

        if not uname or not pwd or not fname:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",
                           (uname, pwd, role, fname))
            conn.commit()
            messagebox.showinfo("Success", f"Registered {fname} as {role}")
            reg_win.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists.")
        finally:
            conn.close()

    reg_win = tk.Toplevel(root)
    reg_win.title("Register")
    reg_win.geometry("300x300")

    center_window(reg_win, 300, 300, parent=root)

    ttk.Label(reg_win, text="Register New Account", font=("Arial", 12)).pack(pady=10)

    ttk.Label(reg_win, text="Full Name:").pack()
    reg_fullname_entry = ttk.Entry(reg_win)
    reg_fullname_entry.pack()

    ttk.Label(reg_win, text="Username:").pack()
    reg_username_entry = ttk.Entry(reg_win)
    reg_username_entry.pack()

    ttk.Label(reg_win, text="Password:").pack()
    reg_password_entry = ttk.Entry(reg_win, show="*")
    reg_password_entry.pack()

    ttk.Label(reg_win, text="Role:").pack()
    reg_role_var = tk.StringVar(value="user")
    ttk.Radiobutton(reg_win, text="User", variable=reg_role_var, value="user").pack()
    ttk.Radiobutton(reg_win, text="Admin", variable=reg_role_var, value="admin").pack()

    try:
        from pm_app.utils import RoundedButton
        btn = RoundedButton(reg_win, text='Register', command=perform_registration, width=140, height=40, radius=10, bg='#06b6d4', fg='#111827', font=('Helvetica Neue', 11))
        btn.pack(pady=10)
    except Exception:
        import tkinter as _tk
        _tk.Button(reg_win, text="Register", command=perform_registration).pack(pady=10)
    
def main_screen():
    global root, username_entry, password_entry, role_var

    root = tk.Tk()
    # Global Tk exception handler: prints traceback to console and appends to pma_errors.log
    def _tk_exception_handler(exc, val, tb):
        import traceback
        traceback.print_exception(exc, val, tb)
        try:
            with open('pma_errors.log', 'a') as f:
                traceback.print_exception(exc, val, tb, file=f)
        except Exception:
            pass
        try:
            messagebox.showerror("Error", f"An unexpected error occurred: {val}", parent=root)
        except Exception:
            pass

    root.report_callback_exception = _tk_exception_handler
    # Show login directly; center window before mainloop
    root.title("GRP2-PYTHON")
    w, h = 600, 500
    root.update_idletasks()
    # center window on screen
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = (screen_w - w) // 2
    y = (screen_h - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")

    # Apply a modern visual style for the login form
    style = ttk.Style(root)
    try:
        style.theme_use('clam')
    except Exception:
        pass

    accent = '#06b6d4'  # cyan accent for dark theme
    bg = '#0f1724'
    card_bg = '#111827'
    fg = '#e6eef6'

    root.configure(bg=bg)
    style.configure('Card.TFrame', background=card_bg, relief='flat')
    style.configure('Header.TLabel', font=('Helvetica', 18, 'bold'), background=card_bg, foreground=fg)
    style.configure('TLabel', background=card_bg, foreground=fg)
    style.configure('TEntry', padding=6)
    style.configure('Accent.TButton', background=accent, foreground='#071428', padding=8, font=('Helvetica', 10, 'bold'))
    style.map('Accent.TButton', background=[('active', '#058fae')])
    style.configure('Secondary.TButton', background='#0b1220', foreground=accent, padding=6)

    root.columnconfigure(0, weight=1)
    card = ttk.Frame(root, style='Card.TFrame', padding=(24, 18))
    card.place(relx=0.5, rely=0.45, anchor='center')

    # optional logo / mark
    try:
        from pm_app.utils import load_asset
        logo_img = load_asset('gantt') or load_asset('task')
    except Exception:
        logo_img = None
    if logo_img:
        logo = ttk.Label(card, image=logo_img, background=card_bg)
        logo.image = logo_img
    else:
        logo = ttk.Label(card, text='⚙️', font=('Helvetica', 28), background=card_bg)
    logo.grid(row=0, column=0, rowspan=2, padx=(0,12))

    title = ttk.Label(card, text='Project Management', style='Header.TLabel')
    title.grid(row=0, column=1, columnspan=2, sticky='w')

    desc = ttk.Label(card, text='Sign in to continue', font=('Helvetica', 9), background=card_bg)
    desc.grid(row=1, column=1, columnspan=2, sticky='w', pady=(0,8))

    ttk.Label(card, text='Username:').grid(row=2, column=1, sticky='w', pady=4)
    username_entry = ttk.Entry(card, width=32)
    username_entry.grid(row=2, column=2, sticky='w', pady=4)

    ttk.Label(card, text='Password:').grid(row=3, column=1, sticky='w', pady=4)
    password_entry = ttk.Entry(card, show='*', width=32)
    password_entry.grid(row=3, column=2, sticky='w', pady=4)

    ttk.Label(card, text='Role:').grid(row=4, column=1, sticky='w', pady=4)
    role_var = tk.StringVar(value='user')
    role_box = ttk.Combobox(card, textvariable=role_var, values=('user', 'admin'), state='readonly', width=30)
    role_box.grid(row=4, column=2, sticky='w', pady=4)

    remember_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(card, text='Remember me', variable=remember_var).grid(row=5, column=2, sticky='w', pady=6)

    btn_frame = ttk.Frame(card, style='Card.TFrame')
    btn_frame.grid(row=6, column=1, columnspan=2, pady=(10,0))
    # Use rounded buttons from pm_app.utils
    try:
        from pm_app.utils import RoundedButton
        mac_font = ('Helvetica Neue', 13)
        login_btn = RoundedButton(btn_frame, text='Login', command=login, width=120, height=40, radius=12, bg=accent, fg=card_bg, font=mac_font)
        login_btn.grid(row=0, column=0, padx=8)
        reg_btn = RoundedButton(btn_frame, text='Register', command=register_user, width=120, height=40, radius=12, bg=card_bg, fg=accent, font=mac_font)
        reg_btn.grid(row=0, column=1, padx=8)
    except Exception:
        import tkinter as _tk
        _tk.Button(btn_frame, text='Login', command=login).grid(row=0, column=0, padx=8)
        _tk.Button(btn_frame, text='Register', command=register_user).grid(row=0, column=1, padx=8)

    username_entry.focus_set()

    root.mainloop()


def center_window(win, width=None, height=None, parent=None):
    """Center a window. If width/height provided, set geometry accordingly; otherwise use current size."""
    try:
        if parent is None:
            p = root
        else:
            p = parent
        p.update_idletasks()
        screen_w = p.winfo_screenwidth()
        screen_h = p.winfo_screenheight()
        if width is None or height is None:
            win.update_idletasks()
            w = win.winfo_width()
            h = win.winfo_height()
        else:
            w = width
            h = height
        x = (screen_w - w) // 2
        y = (screen_h - h) // 2
        win.geometry(f"{w}x{h}+{x}+{y}")
    except Exception:
        pass

    pass



# ---------------- Start the Application ----------------
main_screen()
