import tkinter as tk
from tkinter import messagebox


class InvestorPanel:
    def __init__(self, app):
        self.app = app
        self.dep_amount_e = None

    def render(self):
        self.app.clear()
        self.app.topbar("Investor Panel - Deposit Request")

        box = tk.Frame(self.app)
        box.pack(pady=18)

        tk.Label(box, text="Deposit Amount").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        self.dep_amount_e = tk.Entry(box, width=30)
        self.dep_amount_e.grid(row=0, column=1, padx=8, pady=8)

        tk.Button(self.app, text="Submit Deposit Request", command=self.submit_deposit).pack(pady=8)

        # Show current investor balance and withdraw option if project is closed
        balance = 0.0
        if self.app.current_user:
            balance = self.app.db.investor_balance(self.app.current_user["user_id"])

        tk.Label(self.app, text=f"Current Balance: BDT {balance:,.2f}").pack(pady=6)

        try:
            closed = self.app.db.project_closed()
        except Exception:
            closed = False

        if closed and balance > 0:
            tk.Button(self.app, text="Withdraw", command=self.withdraw).pack(pady=4)

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

    def withdraw(self):
        if not self.app.current_user:
            messagebox.showerror("Session Error", "Please login again")
            self.app.login_ui()
            return

        investor_id = self.app.current_user["user_id"]
        ok = self.app.db.investor_withdraw(investor_id)
        if ok:
            messagebox.showinfo("Done", "Withdrawal completed. Your balance is now 0.")
        else:
            messagebox.showerror(
                "Failed",
                "Withdrawal failed. Either nothing to withdraw or insufficient manager funds.",
            )
        self.render()
