import tkinter as tk
from tkinter import messagebox

from admin_panel import AdminPanel
from investor_panel import InvestorPanel
from manager_panel import ManagerPanel


class App(tk.Tk):
    def __init__(self, db):
        super().__init__()
        self.db = db

        self.title("Phoenix")
        self.geometry("780x560")
        self.resizable(False, False)

        self.current_user = None
        self.role_panels = {
            "admin": AdminPanel,
            "manager": ManagerPanel,
            "investor": InvestorPanel,
        }
        self.login_ui()

    @staticmethod
    def _entry_text(entry_widget):
        return entry_widget.get().strip()

    def clear(self):
        for w in self.winfo_children():
            w.destroy()

    def login_ui(self):
        self.clear()
        tk.Label(self, text="Phoenix Login", font=("Segoe UI", 16, "bold")).pack(pady=18)

        box = tk.Frame(self)
        box.pack(pady=10)

        tk.Label(box, text="User ID").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        self.user_e = tk.Entry(box, width=30)
        self.user_e.grid(row=0, column=1, padx=8, pady=8)

        tk.Label(box, text="Password").grid(row=1, column=0, sticky="w", padx=8, pady=8)
        self.pass_e = tk.Entry(box, width=30, show="*")
        self.pass_e.grid(row=1, column=1, padx=8, pady=8)

        tk.Button(self, text="Login", width=14, command=self.do_login).pack(pady=10)
        tk.Button(self, text="Investor Signup", width=14, command=self.signup_ui).pack(pady=4)
        tk.Label(self, text="Demo: admin/1234, manager/1234, investor/1234", fg="gray").pack(pady=6)

    def do_login(self):
        user_id = self._entry_text(self.user_e)
        password = self._entry_text(self.pass_e)
        row = self.db.login(user_id, password)
        if not row:
            messagebox.showerror("Login Failed", "Invalid user id or password")
            return

        self.current_user = row
        self.show_role_panel(row["role"])

    def show_role_panel(self, role):
        panel_cls = self.role_panels.get(role)
        if panel_cls is None:
            messagebox.showerror("Role Error", f"Unknown role: {role}")
            self.login_ui()
            return
        panel_cls(self).render()

    def topbar(self, title):
        tk.Label(self, text=title, font=("Segoe UI", 14, "bold")).pack(pady=10)
        # Show manager wallet balance and total profit for admin/manager; show investor-only balance to investors
        if self.current_user and self.current_user.get("role") == "investor":
            bal = self.db.investor_balance(self.current_user["user_id"])
            tk.Label(self, text=f"Your Balance: BDT {bal:,.2f}", font=("Segoe UI", 11)).pack()
        else:
            tk.Label(self, text=f"Wallet Balance: BDT {self.db.wallet_balance():,.2f}", font=("Segoe UI", 11)).pack()
            # show total profit if project was closed (or zero)
            profit = self.db.total_profit()
            tk.Label(self, text=f"Total Profit: BDT {profit:,.2f}", font=("Segoe UI", 11)).pack()
        tk.Button(self, text="Logout", command=self.login_ui).pack(pady=6)

    def signup_ui(self):
        self.clear()
        tk.Label(self, text="Investor Signup", font=("Segoe UI", 16, "bold")).pack(pady=18)

        box = tk.Frame(self)
        box.pack(pady=10)

        tk.Label(box, text="New User ID").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        self.new_user_e = tk.Entry(box, width=30)
        self.new_user_e.grid(row=0, column=1, padx=8, pady=8)

        tk.Label(box, text="Password").grid(row=1, column=0, sticky="w", padx=8, pady=8)
        self.new_pass_e = tk.Entry(box, width=30, show="*")
        self.new_pass_e.grid(row=1, column=1, padx=8, pady=8)

        tk.Label(box, text="Confirm Password").grid(row=2, column=0, sticky="w", padx=8, pady=8)
        self.confirm_pass_e = tk.Entry(box, width=30, show="*")
        self.confirm_pass_e.grid(row=2, column=1, padx=8, pady=8)

        tk.Button(self, text="Create Investor Account", command=self.do_signup).pack(pady=10)
        tk.Button(self, text="Back to Login", command=self.login_ui).pack(pady=4)

    def do_signup(self):
        user_id = self._entry_text(self.new_user_e)
        password = self._entry_text(self.new_pass_e)
        confirm = self._entry_text(self.confirm_pass_e)

        if not user_id:
            messagebox.showerror("Signup Failed", "User ID is required")
            return
        if not password:
            messagebox.showerror("Signup Failed", "Password is required")
            return

        if password != confirm:
            messagebox.showerror("Signup Failed", "Password and confirm password must match")
            return

        ok, msg = self.db.signup_investor(user_id, password)
        if not ok:
            messagebox.showerror("Signup Failed", msg)
            return

        messagebox.showinfo("Success", "Investor account created. Please login.")
        self.login_ui()
