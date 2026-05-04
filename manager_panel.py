import tkinter as tk
from tkinter import messagebox


class ManagerPanel:
    def __init__(self, app):
        self.app = app
        self.description_e = None
        self.amount_e = None
        self.entries_list = None
        self.summary_label = None

    def render(self):
        self.app.clear()
        self.app.topbar("Manager Panel - Income & Expense")

        tk.Label(self.app, text="Add Income/Expense Entry", font=("Segoe UI", 11, "bold")).pack(pady=(8, 4))
        
        box = tk.Frame(self.app)
        box.pack(pady=8)

        tk.Label(box, text="Description").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        self.description_e = tk.Entry(box, width=30)
        self.description_e.grid(row=0, column=1, padx=8, pady=6)

        tk.Label(box, text="Amount").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        self.amount_e = tk.Entry(box, width=30)
        self.amount_e.grid(row=1, column=1, padx=8, pady=6)

        button_frame = tk.Frame(self.app)
        button_frame.pack(pady=6)
        tk.Button(button_frame, text="+ Add Income", command=lambda: self.save_entry("income"), bg="#90EE90", width=14).pack(side=tk.LEFT, padx=4)
        tk.Button(button_frame, text="− Add Expense", command=lambda: self.save_entry("expense"), bg="#FFB6C1", width=14).pack(side=tk.LEFT, padx=4)

        tk.Label(self.app, text="Profit Summary", font=("Segoe UI", 11, "bold")).pack(pady=(10, 4))
        self.summary_label = tk.Label(self.app, text="", font=("Segoe UI", 10), fg="darkblue")
        self.summary_label.pack()

        tk.Label(self.app, text="All Entries", font=("Segoe UI", 11, "bold")).pack(pady=(6, 4))
        self.entries_list = tk.Listbox(self.app, width=90, height=6)
        self.entries_list.pack(pady=6)

        self.refresh()
        tk.Button(self.app, text="Refresh", command=self.refresh).pack(pady=4)

    def _parse_amount(self):
        if self.amount_e is None:
            return None
        try:
            amount = float(self.amount_e.get().strip())
            if amount <= 0:
                return None
            return amount
        except ValueError:
            return None

    def save_entry(self, entry_type):
        if self.description_e is None or self.amount_e is None:
            return
        description = self.description_e.get().strip()
        if not description:
            messagebox.showerror("Invalid", "Description is required")
            return
        amount = self._parse_amount()
        if amount is None:
            messagebox.showerror("Invalid", "Enter a valid positive amount")
            return
        ok = self.app.db.add_income_entry(description, amount, entry_type)
        if ok:
            entry_symbol = "+" if entry_type == "income" else "−"
            messagebox.showinfo("Saved", f"Entry {entry_symbol} added")
            self.render()
        else:
            messagebox.showerror("Failed", "Could not add entry")

    def refresh(self):
        if self.entries_list is None or self.summary_label is None:
            return
        summary = self.app.db.get_profit_summary()
        summary_text = f"Income: ৳{summary['income']:,.2f} | Expense: ৳{summary['expense']:,.2f} | Net Profit: ৳{summary['net_profit']:,.2f}"
        self.summary_label.config(text=summary_text)
        self.entries_list.delete(0, tk.END)
        entries = self.app.db.get_income_entries()
        if not entries:
            self.entries_list.insert(tk.END, "No entries yet")
            return
        for entry in entries:
            symbol = "+" if entry["entry_type"] == "income" else "−"
            line = f"{symbol} #{entry['entry_id']} | {entry['created_at']} | {entry['description']} | ৳{entry['amount']:,.2f}"
            self.entries_list.insert(tk.END, line)
