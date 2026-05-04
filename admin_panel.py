import tkinter as tk
from tkinter import messagebox


class AdminPanel:
    def __init__(self, app):
        self.app = app
        self.dep_list = None
        self.entry_list = None
        self.summary_label = None
        self.profit_summary_label = None
        self.wallet_label = None

    def render(self):
        self.app.clear()
        self.app.topbar("Admin Panel")

        is_closed = self.app.db.is_project_closed()
        
        if is_closed:
            tk.Label(self.app, text="PROJECT CLOSED - Distribution Complete", font=("Segoe UI", 12, "bold"), fg="red").pack(pady=10)
            tk.Button(self.app, text="Start New Project", command=self.start_new_project, bg="#FFD700", width=30, font=("Segoe UI", 11, "bold")).pack(pady=10)
        else:
            tk.Label(self.app, text="PROJECT OPEN - Accepting deposits", font=("Segoe UI", 12, "bold"), fg="green").pack(pady=10)

        tk.Label(self.app, text="Pending Deposits", font=("Segoe UI", 11, "bold")).pack(pady=(6, 4))
        self.dep_list = tk.Listbox(self.app, width=90, height=3)
        self.dep_list.pack(pady=6)

        tk.Label(self.app, text="Income & Expense Entries", font=("Segoe UI", 11, "bold")).pack(pady=(6, 4))
        self.profit_summary_label = tk.Label(self.app, text="", font=("Segoe UI", 10), fg="darkblue")
        self.profit_summary_label.pack()

        # Manager wallet balance (admin-only)
        self.wallet_label = tk.Label(self.app, text="", font=("Segoe UI", 10, "bold"), fg="darkgreen")
        self.wallet_label.pack(pady=(4, 6))

        self.entry_list = tk.Listbox(self.app, width=90, height=3)
        self.entry_list.pack(pady=6)

        self.refresh()

        button_frame = tk.Frame(self.app)
        button_frame.pack(pady=8)
        tk.Button(button_frame, text="Approve Selected", command=self.approve_selected, width=16).pack(side=tk.LEFT, padx=4)
        tk.Button(button_frame, text="Refresh", command=self.refresh, width=16).pack(side=tk.LEFT, padx=4)
        
        if not is_closed:
            tk.Button(button_frame, text="Close Project & Calculate", command=self.close_project, bg="#FFD700", width=20).pack(side=tk.LEFT, padx=4)

    def refresh(self):
        if self.dep_list is None or self.entry_list is None or self.profit_summary_label is None:
            return
        self._load_pending_deposits()
        self._load_income_entries()
        # Update manager wallet balance
        if self.wallet_label is not None:
            bal = self.app.db.wallet_balance()
            self.wallet_label.config(text=f"Manager Wallet Balance: ৳{bal:,.2f}")

    def _load_pending_deposits(self):
        if self.dep_list is None:
            return
        self.dep_list.delete(0, tk.END)
        rows = self.app.db.pending_deposits()
        if not rows:
            self.dep_list.insert(tk.END, "No pending deposits")
            return
        for row in rows:
            line = f"#{row['deposit_id']} | {row['investor_id']} | ৳{float(row['amount']):,.2f}"
            self.dep_list.insert(tk.END, line)

    def _load_income_entries(self):
        if self.entry_list is None or self.profit_summary_label is None:
            return
        self.entry_list.delete(0, tk.END)
        summary = self.app.db.get_profit_summary()
        summary_text = f"Income: ৳{summary['income']:,.2f} | Expense: ৳{summary['expense']:,.2f} | Net Profit: ৳{summary['net_profit']:,.2f}"
        self.profit_summary_label.config(text=summary_text)
        entries = self.app.db.get_income_entries()
        if not entries:
            self.entry_list.insert(tk.END, "No income/expense entries")
            return
        for entry in entries:
            symbol = "+" if entry["entry_type"] == "income" else "−"
            line = f"{symbol} #{entry['entry_id']} | {entry['created_at']} | {entry['description']} | ৳{entry['amount']:,.2f}"
            self.entry_list.insert(tk.END, line)

    def approve_selected(self):
        if self.dep_list is None:
            return
        sel = self.dep_list.curselection()
        if not sel:
            messagebox.showwarning("Select", "Please select a deposit")
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
        if messagebox.askyesno("Confirm", "Close project and calculate investor profits?"):
            ok, msg = self.app.db.close_project_and_calculate(1)
            if ok:
                messagebox.showinfo("Success", msg)
                self.render()
            else:
                messagebox.showerror("Failed", msg)

    def start_new_project(self):
        if messagebox.askyesno("Confirm", "Start a new project?\n\nWallet will reset to ৳0\nAll investors can invest again"):
            ok, msg = self.app.db.start_new_project()
            if ok:
                messagebox.showinfo("Success", msg)
                self.render()
            else:
                messagebox.showerror("Failed", msg)
