import tkinter as tk
from tkinter import messagebox


class AdminPanel:
    def __init__(self, app):
        self.app = app
        self.dep_list = None
        self.cost_list = None
        self.summary_label = None

    def render(self):
        self.app.clear()
        self.app.topbar("Admin Panel")

        tk.Label(self.app, text="Pending Deposits", font=("Segoe UI", 11, "bold")).pack(pady=(6, 4))
        self.dep_list = tk.Listbox(self.app, width=90, height=6)
        self.dep_list.pack(pady=6)

        tk.Label(self.app, text="Manager All Daily Costs", font=("Segoe UI", 11, "bold")).pack(pady=(6, 4))
        self.summary_label = tk.Label(self.app, text="", font=("Segoe UI", 10))
        self.summary_label.pack()

        self.cost_list = tk.Listbox(self.app, width=90, height=6)
        self.cost_list.pack(pady=6)

        self.refresh()
        tk.Button(self.app, text="Approve Selected Deposit", command=self.approve_selected).pack(pady=8)
        tk.Button(self.app, text="Refresh All Accounts", command=self.refresh).pack(pady=4)

    def refresh(self):
        if self.dep_list is None or self.cost_list is None or self.summary_label is None:
            return

        self._load_pending_deposits()
        self._load_manager_costs()

    def _load_pending_deposits(self):
        if self.dep_list is None:
            return

        self.dep_list.delete(0, tk.END)
        rows = self.app.db.pending_deposits()
        if not rows:
            self.dep_list.insert(tk.END, "No pending deposits")
            return

        for row in rows:
            line = f"#{row['deposit_id']} | {row['investor_id']} | BDT {float(row['amount']):,.2f}"
            self.dep_list.insert(tk.END, line)

    def _load_manager_costs(self):
        if self.cost_list is None or self.summary_label is None:
            return

        self.cost_list.delete(0, tk.END)
        cost_rows = self.app.db.manager_daily_costs()
        summary = self.app.db.manager_cost_summary()
        self.summary_label.config(
            text=f"Entries: {summary['count']} | Total Spent: BDT {summary['total']:,.2f}"
        )

        if not cost_rows:
            self.cost_list.insert(tk.END, "No manager daily costs found")
            return

        for row in cost_rows:
            line = (
                f"#{row['cost_id']} | {row['created_at']} | "
                f"{row['purpose']} | BDT {row['amount']:,.2f}"
            )
            self.cost_list.insert(tk.END, line)

    def approve_selected(self):
        if self.dep_list is None:
            return

        sel = self.dep_list.curselection()
        if not sel:
            return

        text = self.dep_list.get(sel[0])
        if text.startswith("No pending"):
            return

        dep_id = int(text.split("|")[0].replace("#", "").strip())
        ok = self.app.db.approve_deposit(dep_id)
        if ok:
            messagebox.showinfo("Done", "Deposit approved")
            self.render()
        else:
            messagebox.showerror("Failed", "Could not approve this deposit")

    def close_project(self):
        ok = self.app.db.close_project()
        if ok:
            messagebox.showinfo("Project Closed", "Project closed and investor profits calculated")
        else:
            messagebox.showerror("Failed", "Could not close project")
        self.render()
