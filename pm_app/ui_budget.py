import tkinter as tk
from tkinter import ttk, messagebox
from pm_app.db import get_connection, add_budget_request, get_pending_budgets, approve_budget_request as db_approve_budget_request, reject_budget_request as db_reject_budget_request, record_expense as db_record_expense
from pm_app import navigation

_widgets = {}


def request_budget(user, project, amount):
    if not project or not amount:
        messagebox.showerror("Error", "Project name and amount are required!")
        return
    try:
        amount = float(amount)
        add_budget_request(user, project, amount)
        messagebox.showinfo("Request Submitted", f"Budget request for {project}: ${amount} submitted.")
    except ValueError:
        messagebox.showerror("Error", "Enter a valid numerical amount.")


def _approve_budget_request_ui(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Select a request to approve!")
        return
    request_id = tree.item(selected_item, "values")[0]
    amount = float(tree.item(selected_item, "values")[3])
    db_approve_budget_request(request_id, amount)
    messagebox.showinfo("Budget Approved", f"Approved ${amount} for request {request_id}.")
    navigation.go_dashboard("admin", "Admin")


def _reject_budget_request_ui(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Select a request to reject!")
        return
    request_id = tree.item(selected_item, "values")[0]
    db_reject_budget_request(request_id)
    messagebox.showinfo("Budget Rejected", f"Request {request_id} was rejected.")
    navigation.go_dashboard("admin", "Admin")


def _record_expense_ui(project, amount):
    db_record_expense(project, amount)
    messagebox.showinfo("Expense Recorded", f"${amount} spent on {project}.")


def show_budget_management(root, role, full_name):
    for w in root.winfo_children():
        w.destroy()
    ttk.Label(root, text="Budget Management", font=("Arial", 16)).pack(pady=10)

    ttk.Label(root, text="Expense:").pack()
    project_entry = ttk.Entry(root)
    project_entry.pack()

    ttk.Label(root, text="Requested Amount:").pack()
    amount_entry = ttk.Entry(root)
    amount_entry.pack()

    try:
        from pm_app.utils import RoundedButton, get_theme, load_asset
        theme = get_theme()
        ic_budget = load_asset('budget')
        submit_btn = RoundedButton(root, text='Submit Request', image=ic_budget, command=lambda: request_budget(full_name, project_entry.get(), amount_entry.get()), width=260, height=40, radius=10, bg=theme['accent'], fg=theme['card_bg'], font=('Helvetica Neue', 11))
        submit_btn.pack(pady=10)
    except Exception:
        import tkinter as _tk
        _tk.Button(root, text="Submit Budget Request", command=lambda: request_budget(full_name, project_entry.get(), amount_entry.get())).pack(pady=10)

    if role == 'admin':
        ttk.Label(root, text="Pending Budget Requests").pack()
        budget_tree = ttk.Treeview(root, columns=("ID", "User", "Project", "Requested", "Allocated", "Spent", "Status"), show="headings")
        for col in budget_tree["columns"]:
            budget_tree.heading(col, text=col)
            budget_tree.column(col, width=100)
        budget_tree.pack(fill=tk.BOTH, expand=True)

        rows = get_pending_budgets()
        for row in rows:
            budget_tree.insert("", "end", values=row)

        try:
            from pm_app.utils import RoundedButton, load_asset
            ic_budget = load_asset('budget')
            a_btn = RoundedButton(root, text='Approve', image=ic_budget, command=lambda: _approve_budget_request_ui(budget_tree), width=200, height=36, radius=8, bg='#16a34a', fg='white')
            a_btn.pack(pady=5)
            r_btn = RoundedButton(root, text='Reject', image=ic_budget, command=lambda: _reject_budget_request_ui(budget_tree), width=200, height=36, radius=8, bg='#e53e3e', fg='white')
            r_btn.pack(pady=5)
        except Exception:
            import tkinter as _tk
            _tk.Button(root, text="Approve Selected Request", command=lambda: _approve_budget_request_ui(budget_tree)).pack(pady=5)
            _tk.Button(root, text="Reject Selected Request", command=lambda: _reject_budget_request_ui(budget_tree)).pack(pady=5)

    try:
        from pm_app.utils import RoundedButton
        from pm_app.utils import load_asset
        ic_gantt = load_asset('gantt')
        back = RoundedButton(root, text='Back', image=ic_gantt, command=lambda: navigation.go_dashboard(role, full_name), width=220, height=36, radius=8, bg='#111827', fg='#e6eef6')
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
