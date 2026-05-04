from typing import Any, cast

import mysql.connector

from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME


class DB:
    def __init__(self):
        bootstrap_con = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            auth_plugin="mysql_native_password",
            autocommit=True,
        )
        bootstrap_cur = bootstrap_con.cursor()
        bootstrap_cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`")
        bootstrap_cur.close()
        bootstrap_con.close()

        self.con = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            auth_plugin="mysql_native_password",
            autocommit=False,
        )
        self.init_schema()
        self.seed_data()

    def cur(self, dictionary=False, buffered=False):
        return self.con.cursor(dictionary=dictionary, buffered=buffered)

    def init_schema(self):
        c = self.cur()
        c.execute("CREATE TABLE IF NOT EXISTS users (user_id VARCHAR(60) PRIMARY KEY, password VARCHAR(120) NOT NULL, role ENUM('admin','manager','investor') NOT NULL);")
        c.execute("CREATE TABLE IF NOT EXISTS manager_wallet (wallet_id TINYINT PRIMARY KEY, balance DECIMAL(12,2) NOT NULL);")
        c.execute("CREATE TABLE IF NOT EXISTS projects (project_id INT PRIMARY KEY AUTO_INCREMENT, status ENUM('open','closed') NOT NULL DEFAULT 'open', created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, closed_at DATETIME);")
        
        try:
            c.execute("SHOW COLUMNS FROM deposits LIKE 'project_id'")
            col_exists = c.fetchone()
            if not col_exists:
                c.execute("ALTER TABLE deposits ADD COLUMN project_id INT NOT NULL DEFAULT 1 AFTER deposit_id")
        except:
            c.execute("CREATE TABLE IF NOT EXISTS deposits (deposit_id INT PRIMARY KEY AUTO_INCREMENT, project_id INT NOT NULL DEFAULT 1, investor_id VARCHAR(60) NOT NULL, amount DECIMAL(12,2) NOT NULL, status ENUM('pending','approved','withdrawn') NOT NULL DEFAULT 'pending', created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP);")
        
        c.execute("CREATE TABLE IF NOT EXISTS daily_costs (cost_id INT PRIMARY KEY AUTO_INCREMENT, purpose VARCHAR(120) NOT NULL, amount DECIMAL(12,2) NOT NULL, created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP);")
        c.execute("CREATE TABLE IF NOT EXISTS income_entries (entry_id INT PRIMARY KEY AUTO_INCREMENT, description VARCHAR(255) NOT NULL, amount DECIMAL(12,2) NOT NULL, entry_type ENUM('income','expense') NOT NULL, created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP);")
        c.execute("CREATE TABLE IF NOT EXISTS investor_profits (profit_id INT PRIMARY KEY AUTO_INCREMENT, investor_id VARCHAR(60) NOT NULL, project_id INT NOT NULL, invested_amount DECIMAL(12,2) NOT NULL, profit_share DECIMAL(12,2) NOT NULL, final_balance DECIMAL(12,2) NOT NULL, withdrawn TINYINT(1) DEFAULT 0, created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, withdrawn_at DATETIME);")
        
        self.con.commit()
        c.close()

    def seed_data(self):
        c = self.cur()
        c.execute("DELETE FROM users WHERE user_id IN ('manager_001', 'investor_001')")
        c.execute("INSERT INTO users (user_id, password, role) VALUES ('admin', '1234', 'admin'), ('manager', '1234', 'manager'), ('investor', '1234', 'investor') ON DUPLICATE KEY UPDATE password = VALUES(password), role = VALUES(role);")
        c.execute("INSERT IGNORE INTO manager_wallet (wallet_id, balance) VALUES (1, 100000.00);")
        c.execute("INSERT IGNORE INTO projects (project_id, status) VALUES (1, 'open');")
        c.execute("UPDATE deposits SET project_id = 1 WHERE project_id IS NULL OR project_id = 0")
        self.con.commit()
        c.close()

    def login(self, user_id, password):
        c = self.cur(buffered=True)
        c.execute("SELECT user_id, role FROM users WHERE user_id=%s AND password=%s", (user_id, password))
        row = c.fetchone()
        c.close()
        if not row:
            return None
        row_any = cast(Any, row)
        return {"user_id": str(row_any[0]), "role": str(row_any[1])}

    def signup_investor(self, user_id, password):
        user_id = user_id.strip().lower()
        password = password.strip()
        if not user_id or not password:
            return False, "User ID and password are required"
        if len(user_id) > 60:
            return False, "User ID is too long"
        if user_id.startswith("admin") or user_id.startswith("manager"):
            return False, "Use an investor-style user id"
        c = self.cur(buffered=True)
        c.execute("SELECT user_id FROM users WHERE user_id=%s", (user_id,))
        exists = c.fetchone()
        if exists:
            c.close()
            return False, "User ID already exists"
        c.execute("INSERT INTO users (user_id, password, role) VALUES (%s, %s, 'investor')", (user_id, password))
        self.con.commit()
        c.close()
        return True, "Signup successful"

    def wallet_balance(self):
        c = self.cur(buffered=True)
        c.execute("SELECT balance FROM manager_wallet WHERE wallet_id=1")
        row = c.fetchone()
        c.close()
        if not row:
            return 0.0
        row_any = cast(Any, row)
        return float(row_any[0])

    def add_deposit_request(self, investor_id, amount):
        c = self.cur()
        c.execute("INSERT INTO deposits (investor_id, amount) VALUES (%s, %s)", (investor_id, amount))
        self.con.commit()
        c.close()

    def pending_deposits(self):
        c = self.cur(buffered=True)
        c.execute("SELECT deposit_id, investor_id, amount FROM deposits WHERE status='pending' ORDER BY deposit_id ASC")
        rows = c.fetchall()
        c.close()
        result = []
        for row in rows:
            row_any = cast(Any, row)
            result.append({"deposit_id": int(row_any[0]), "investor_id": str(row_any[1]), "amount": float(row_any[2])})
        return result

    def approve_deposit(self, deposit_id):
        c = self.cur(buffered=True)
        c.execute("SELECT amount, status FROM deposits WHERE deposit_id=%s FOR UPDATE", (deposit_id,))
        row = c.fetchone()
        if not row:
            self.con.rollback()
            c.close()
            return False
        row_any = cast(Any, row)
        if row_any[1] == "approved":
            self.con.rollback()
            c.close()
            return False
        c.execute("UPDATE deposits SET status='approved' WHERE deposit_id=%s", (deposit_id,))
        c.execute("UPDATE manager_wallet SET balance = balance + %s WHERE wallet_id=1", (float(row_any[0]),))
        self.con.commit()
        c.close()
        return True

    def add_income_entry(self, description, amount, entry_type):
        if entry_type not in ("income", "expense"):
            return False
        c = self.cur()
        c.execute("INSERT INTO income_entries (description, amount, entry_type) VALUES (%s, %s, %s)", (description, amount, entry_type))
        self.con.commit()
        c.close()
        return True

    def get_income_entries(self):
        c = self.cur(buffered=True)
        c.execute("SELECT entry_id, description, amount, entry_type, created_at FROM income_entries ORDER BY entry_id DESC")
        rows = c.fetchall()
        c.close()
        result = []
        for row in rows:
            row_any = cast(Any, row)
            result.append({"entry_id": int(row_any[0]), "description": str(row_any[1]), "amount": float(row_any[2]), "entry_type": str(row_any[3]), "created_at": str(row_any[4])})
        return result

    def get_profit_summary(self):
        c = self.cur(buffered=True)
        c.execute("SELECT entry_type, COALESCE(SUM(amount), 0) FROM income_entries GROUP BY entry_type")
        rows = c.fetchall()
        c.close()
        income = 0.0
        expense = 0.0
        for row in rows:
            row_any = cast(Any, row)
            if str(row_any[0]) == "income":
                income = float(row_any[1])
            elif str(row_any[0]) == "expense":
                expense = float(row_any[1])
        net_profit = income - expense
        return {"income": income, "expense": expense, "net_profit": net_profit}

    def get_approved_deposits_for_project(self, project_id=1):
        c = self.cur(buffered=True)
        try:
            c.execute("SELECT investor_id, SUM(amount) FROM deposits WHERE (project_id=%s OR project_id IS NULL) AND status='approved' GROUP BY investor_id", (project_id,))
        except:
            c.execute("SELECT investor_id, SUM(amount) FROM deposits WHERE status='approved' GROUP BY investor_id")
        rows = c.fetchall()
        c.close()
        result = []
        for row in rows:
            row_any = cast(Any, row)
            result.append({"investor_id": str(row_any[0]), "amount": float(row_any[1])})
        return result

    def close_project_and_calculate(self, project_id=1):
        c = self.cur(buffered=True)
        c.execute("SELECT status FROM projects WHERE project_id=%s FOR UPDATE", (project_id,))
        project_row = c.fetchone()
        if not project_row:
            self.con.rollback()
            c.close()
            return False, "Project not found"
        if cast(Any, project_row)[0] == "closed":
            self.con.rollback()
            c.close()
            return False, "Project already closed"

        profit_summary = self.get_profit_summary()
        net_profit = profit_summary["net_profit"]
        approved_deposits = self.get_approved_deposits_for_project(project_id)
        
        if not approved_deposits:
            self.con.rollback()
            c.close()
            return False, "No approved deposits"

        total_invested = sum(d["amount"] for d in approved_deposits)
        if total_invested <= 0:
            self.con.rollback()
            c.close()
            return False, "Total invested is zero"

        profit_distribution = net_profit * 0.4 if net_profit > 0 else 0.0

        for deposit in approved_deposits:
            investor_id = deposit["investor_id"]
            invested_amount = deposit["amount"]
            share_ratio = invested_amount / total_invested
            profit_share = profit_distribution * share_ratio
            final_balance = invested_amount + profit_share
            c.execute("INSERT INTO investor_profits (investor_id, project_id, invested_amount, profit_share, final_balance) VALUES (%s, %s, %s, %s, %s)", (investor_id, project_id, invested_amount, profit_share, final_balance))

        c.execute("UPDATE projects SET status='closed', closed_at=CURRENT_TIMESTAMP WHERE project_id=%s", (project_id,))
        self.con.commit()
        c.close()
        return True, f"Project closed. Net Profit: ৳{net_profit:,.2f}. 40% (৳{profit_distribution:,.2f}) distributed to investors."

    def get_investor_profit_details(self, investor_id):
        c = self.cur(buffered=True)
        c.execute("SELECT investor_id, invested_amount, profit_share, final_balance, withdrawn, created_at FROM investor_profits WHERE investor_id=%s AND project_id=1", (investor_id,))
        row = c.fetchone()
        c.close()
        if not row:
            return None
        row_any = cast(Any, row)
        return {"investor_id": str(row_any[0]), "invested_amount": float(row_any[1]), "profit_share": float(row_any[2]), "final_balance": float(row_any[3]), "withdrawn": bool(row_any[4]), "created_at": str(row_any[5])}

    def withdraw_investor_profit(self, investor_id):
        c = self.cur(buffered=True)
        c.execute("SELECT final_balance, withdrawn FROM investor_profits WHERE investor_id=%s AND project_id=1 FOR UPDATE", (investor_id,))
        row = c.fetchone()
        if not row:
            self.con.rollback()
            c.close()
            return False, "No profit record found"
        row_any = cast(Any, row)
        final_balance = float(row_any[0])
        already_withdrawn = bool(row_any[1])
        if already_withdrawn:
            self.con.rollback()
            c.close()
            return False, "Already withdrawn"
        c.execute("UPDATE investor_profits SET withdrawn=1, withdrawn_at=CURRENT_TIMESTAMP WHERE investor_id=%s AND project_id=1", (investor_id,))
        self.con.commit()
        c.close()
        return True, f"Withdrawal successful. Amount: ৳{final_balance:,.2f}"

    def is_project_closed(self):
        c = self.cur(buffered=True)
        try:
            c.execute("SELECT status FROM projects WHERE project_id=1")
            row = c.fetchone()
            c.close()
            if not row:
                return False
            return cast(Any, row)[0] == "closed"
        except:
            c.close()
            return False

    def start_new_project(self):
        c = self.cur()
        try:
            c.execute("UPDATE projects SET status='open', closed_at=NULL WHERE project_id=1")
            c.execute("UPDATE manager_wallet SET balance = 0 WHERE wallet_id=1")
            c.execute("DELETE FROM income_entries")
            c.execute("DELETE FROM deposits")
            c.execute("DELETE FROM daily_costs")
            self.con.commit()
            c.close()
            return True, "✓ New Project Started!\n\n✓ Wallet Reset: ৳0\n✓ All Old Entries Cleared\n✓ All Deposits Cleared\n✓ Ready for New Investments"
        except Exception as e:
            self.con.rollback()
            c.close()
            return False, f"Error starting new project: {str(e)}"
