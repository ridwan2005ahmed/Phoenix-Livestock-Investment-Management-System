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
