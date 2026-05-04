import tkinter as tk
from tkinter import messagebox


class InvestorPanel:
    def __init__(self, app):
        self.app = app
        self.dep_amount_e = None
        self.profit_info_label = None
        self.profit_details_label = None

    def render(self):
        self.app.clear()
        self.app.topbar("Investor Panel")

        investor_id = self.app.current_user["user_id"] if self.app.current_user else None
        is_closed = self.app.db.is_project_closed()

        if is_closed:
            tk.Label(self.app, text="PROJECT CLOSED", font=("Segoe UI", 13, "bold"), fg="darkred").pack(pady=10)
            self.profit_info_label = tk.Label(self.app, text="", font=("Segoe UI", 10))
            self.profit_info_label.pack(pady=8)
            self.profit_details_label = tk.Label(self.app, text="", font=("Segoe UI", 11, "bold"), fg="darkgreen")
            self.profit_details_label.pack(pady=8)
            self.refresh_profit_info(investor_id)
            tk.Button(self.app, text="Withdraw My Balance", command=lambda: self.withdraw_profit(investor_id), bg="#90EE90", width=20).pack(pady=8)
            tk.Button(self.app, text="Refresh", command=lambda: self.refresh_profit_info(investor_id), width=20).pack(pady=4)
        else:
            tk.Label(self.app, text="Deposit Request", font=("Segoe UI", 12, "bold")).pack(pady=10)
            box = tk.Frame(self.app)
            box.pack(pady=18)
            tk.Label(box, text="Deposit Amount (৳)").grid(row=0, column=0, sticky="w", padx=8, pady=8)
            self.dep_amount_e = tk.Entry(box, width=30)
            self.dep_amount_e.grid(row=0, column=1, padx=8, pady=8)
            tk.Button(self.app, text="Submit Deposit Request", command=self.submit_deposit, bg="#87CEEB", width=20).pack(pady=8)
            tk.Label(self.app, text="My Deposits", font=("Segoe UI", 11, "bold")).pack(pady=(10, 4))
            self.profit_info_label = tk.Listbox(self.app, width=80, height=5)
            self.profit_info_label.pack(pady=6)
            self.show_my_deposits(investor_id)

    def _parse_amount(self):
        if self.dep_amount_e is None:
            return None
        try:
            amount = float(self.dep_amount_e.get().strip())
            if amount <= 0:
                return None
            return amount
        except ValueError:
            return None

    def submit_deposit(self):
        if self.dep_amount_e is None:
            return
        if not self.app.current_user:
            messagebox.showerror("Session Error", "Please login again")
            self.app.login_ui()
            return
        amount = self._parse_amount()
        if amount is None:
            messagebox.showerror("Invalid", "Enter a valid positive amount")
            return
        self.app.db.add_deposit_request(self.app.current_user["user_id"], amount)
        messagebox.showinfo("Done", "Deposit request submitted")
        self.render()

    def show_my_deposits(self, investor_id):
        if not investor_id or self.profit_info_label is None:
            return
        if isinstance(self.profit_info_label, tk.Listbox):
            self.profit_info_label.delete(0, tk.END)
            c = self.app.db.cur()
            c.execute("SELECT deposit_id, amount, status, created_at FROM deposits WHERE investor_id=%s ORDER BY deposit_id DESC", (investor_id,))
            rows = c.fetchall()
            c.close()
            if not rows:
                self.profit_info_label.insert(tk.END, "No deposits yet")
                return
            for row in rows:
                status_symbol = "✓" if row[2] == "approved" else "⧖"
                line = f"{status_symbol} #{row[0]} | ৳{float(row[1]):,.2f} | {row[2]} | {row[3]}"
                self.profit_info_label.insert(tk.END, line)

    def refresh_profit_info(self, investor_id):
        if not investor_id:
            return
        profit_info = self.app.db.get_investor_profit_details(investor_id)
        if profit_info is None:
            if self.profit_info_label and isinstance(self.profit_info_label, tk.Label):
                self.profit_info_label.config(text="No profit record found")
            return
        if self.profit_info_label and isinstance(self.profit_info_label, tk.Label):
            info_text = f"Invested: ৳{profit_info['invested_amount']:,.2f} | Profit Share (40%): ৳{profit_info['profit_share']:,.2f}"
            self.profit_info_label.config(text=info_text)
        if self.profit_details_label:
            status = "WITHDRAWN" if profit_info["withdrawn"] else "PENDING"
            balance_text = f"Your Final Balance: ৳{profit_info['final_balance']:,.2f} ({status})"
            self.profit_details_label.config(text=balance_text)

    def withdraw_profit(self, investor_id):
        if not investor_id:
            messagebox.showerror("Error", "Please login again")
            return
        if messagebox.askyesno("Confirm", "Withdraw your final balance?"):
            ok, msg = self.app.db.withdraw_investor_profit(investor_id)
            if ok:
                messagebox.showinfo("Success", msg)
                self.render()
            else:
                messagebox.showerror("Failed", msg)
