import tkinter as tk
from tkinter import messagebox


class ManagerPanel:
    def __init__(self, app):
        self.app = app
        self.purpose_e = None
        self.cost_e = None
        self.profit_e = None

    def render(self):
        self.app.clear()
        self.app.topbar("Manager Panel - Daily Cost")

        box = tk.Frame(self.app)
        box.pack(pady=12)

        tk.Label(box, text="Purpose").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        self.purpose_e = tk.Entry(box, width=35)
        self.purpose_e.grid(row=0, column=1, padx=8, pady=8)

        tk.Label(box, text="Amount").grid(row=1, column=0, sticky="w", padx=8, pady=8)
        self.cost_e = tk.Entry(box, width=35)
        self.cost_e.grid(row=1, column=1, padx=8, pady=8)

        tk.Button(self.app, text="Save Daily Cost", command=self.save_daily_cost).pack(pady=8)

        # Manager profit section
        sep = tk.Frame(self.app, height=2, bd=1, relief="sunken")
        sep.pack(fill="x", padx=8, pady=12)

        prof_box = tk.Frame(self.app)
        prof_box.pack(pady=6)

        tk.Label(prof_box, text="Add Profit Amount").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        self.profit_e = tk.Entry(prof_box, width=20)
        self.profit_e.grid(row=0, column=1, padx=8, pady=8)
        tk.Button(self.app, text="Add Profit", command=self.add_profit).pack(pady=6)

    def _parse_amount(self):
        if self.cost_e is None:
            return None
        try:
            amount = float(self.cost_e.get().strip())
            if amount <= 0:
                return None
            return amount
        except ValueError:
            return None

    def _parse_profit_amount(self):
        if self.profit_e is None:
            return None
        try:
            amount = float(self.profit_e.get().strip())
            if amount <= 0:
                return None
            return amount
        except ValueError:
            return None

    def save_daily_cost(self):
        if self.purpose_e is None or self.cost_e is None:
            return

        purpose = self.purpose_e.get().strip()
        if not purpose:
            messagebox.showerror("Invalid", "Purpose is required")
            return

        amount = self._parse_amount()
        if amount is None:
            messagebox.showerror("Invalid", "Enter a valid positive amount")
            return

        ok = self.app.db.add_daily_cost(purpose, amount)
        if not ok:
            messagebox.showerror("Failed", "Insufficient wallet balance")
            return

        messagebox.showinfo("Saved", "Daily cost added")
        self.render()

    def add_profit(self):
        if self.profit_e is None:
            return

        amount = self._parse_profit_amount()
        if amount is None:
            messagebox.showerror("Invalid", "Enter a valid positive amount")
            return

        ok = self.app.db.add_manager_profit(amount)
        if not ok:
            messagebox.showerror("Failed", "Could not add profit")
            return

        messagebox.showinfo("Done", "Profit added to wallet")
        self.render()
