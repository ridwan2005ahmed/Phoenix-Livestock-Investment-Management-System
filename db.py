from typing import Any, cast

import mysql.connector

from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME


class DB:
    def __init__(self):
        # Bootstrap connection without selecting a DB first.
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

    def cur(self, dictionary=False):
        return self.con.cursor(dictionary=dictionary)

    def init_schema(self):
        c = self.cur()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id VARCHAR(60) PRIMARY KEY,
                password VARCHAR(120) NOT NULL,
                role ENUM('admin','manager','investor') NOT NULL
            );
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS manager_wallet (
                wallet_id TINYINT PRIMARY KEY,
                balance DECIMAL(12,2) NOT NULL
            );
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS deposits (
                deposit_id INT PRIMARY KEY AUTO_INCREMENT,
                investor_id VARCHAR(60) NOT NULL,
                amount DECIMAL(12,2) NOT NULL,
                status ENUM('pending','approved') NOT NULL DEFAULT 'pending',
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS daily_costs (
                cost_id INT PRIMARY KEY AUTO_INCREMENT,
                purpose VARCHAR(120) NOT NULL,
                amount DECIMAL(12,2) NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        self.con.commit()
        c.close()

    def seed_data(self):
        c = self.cur()
        c.execute("DELETE FROM users WHERE user_id IN ('manager_001', 'investor_001')")
        c.execute(
            """
            INSERT INTO users (user_id, password, role) VALUES
            ('admin', '1234', 'admin'),
            ('manager', '1234', 'manager'),
            ('investor', '1234', 'investor')
            ON DUPLICATE KEY UPDATE
                password = VALUES(password),
                role = VALUES(role);
            """
        )
        c.execute("INSERT IGNORE INTO manager_wallet (wallet_id, balance) VALUES (1, 100000.00);")
        self.con.commit()
        c.close()

    def login(self, user_id, password):
        c = self.cur()
        c.execute(
            "SELECT user_id, role FROM users WHERE user_id=%s AND password=%s",
            (user_id, password),
        )
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

        c = self.cur()
        c.execute("SELECT user_id FROM users WHERE user_id=%s", (user_id,))
        exists = c.fetchone()
        if exists:
            c.close()
            return False, "User ID already exists"

        c.execute(
            "INSERT INTO users (user_id, password, role) VALUES (%s, %s, 'investor')",
            (user_id, password),
        )
        self.con.commit()
        c.close()
        return True, "Signup successful"

    def wallet_balance(self):
        c = self.cur()
        c.execute("SELECT balance FROM manager_wallet WHERE wallet_id=1")
        row = c.fetchone()
        c.close()
        if not row:
            return 0.0
        row_any = cast(Any, row)
        return float(row_any[0])

    def investor_balance(self, investor_id):
        c = self.cur()
        # If project was closed, investor_accounts will exist and hold final balances
        try:
            c.execute("SELECT balance FROM investor_accounts WHERE investor_id=%s", (investor_id,))
            row = c.fetchone()
            if row:
                row_any = cast(Any, row)
                c.close()
                return float(row_any[0])
        except Exception:
            # table may not exist yet; fall back to summing approved deposits
            pass

        c.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM deposits WHERE investor_id=%s AND status='approved'",
            (investor_id,),
        )
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
        c = self.cur()
        c.execute("SELECT deposit_id, investor_id, amount FROM deposits WHERE status='pending' ORDER BY deposit_id ASC")
        rows = c.fetchall()
        c.close()
        result = []
        for row in rows:
            row_any = cast(Any, row)
            result.append(
                {
                    "deposit_id": int(row_any[0]),
                    "investor_id": str(row_any[1]),
                    "amount": float(row_any[2]),
                }
            )
        return result

    def approve_deposit(self, deposit_id):
        c = self.cur()
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

    def add_daily_cost(self, purpose, amount):
        c = self.cur()
        c.execute("SELECT balance FROM manager_wallet WHERE wallet_id=1 FOR UPDATE")
        row = c.fetchone()
        if not row:
            bal = 0.0
        else:
            row_any = cast(Any, row)
            bal = float(row_any[0])
        if bal < amount:
            self.con.rollback()
            c.close()
            return False
        c.execute("INSERT INTO daily_costs (purpose, amount) VALUES (%s, %s)", (purpose, amount))
        c.execute("UPDATE manager_wallet SET balance = balance - %s WHERE wallet_id=1", (amount,))
        self.con.commit()
        c.close()
        return True

    def add_manager_profit(self, amount):
        try:
            amt = float(amount)
        except (TypeError, ValueError):
            return False
        if amt <= 0:
            return False
        c = self.cur()
        c.execute("UPDATE manager_wallet SET balance = balance + %s WHERE wallet_id=1", (amt,))
        self.con.commit()
        c.close()
        return True

    def close_project(self):
        c = self.cur()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS investor_accounts (
                investor_id VARCHAR(60) PRIMARY KEY,
                invested DECIMAL(12,2) NOT NULL,
                profit DECIMAL(12,2) NOT NULL,
                balance DECIMAL(12,2) NOT NULL,
                withdrawn TINYINT(1) NOT NULL DEFAULT 0
            );
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS project_summary (
                summary_id TINYINT PRIMARY KEY,
                total_invested DECIMAL(12,2) NOT NULL,
                total_profit DECIMAL(12,2) NOT NULL,
                closed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        c.execute("DELETE FROM investor_accounts")
        c.execute(
            "INSERT INTO investor_accounts (investor_id, invested, profit, balance, withdrawn) "
            "SELECT investor_id, SUM(amount) AS invested, SUM(amount)*0.4 AS profit, SUM(amount)*1.4 AS balance, 0 "
            "FROM deposits WHERE status='approved' GROUP BY investor_id"
        )
        c.execute("SELECT COALESCE(SUM(amount), 0), COALESCE(SUM(amount), 0) * 0.4 FROM deposits WHERE status='approved'")
        row = c.fetchone()
        invested = 0.0
        profit = 0.0
        if row:
            row_any = cast(Any, row)
            invested = float(row_any[0])
            profit = float(row_any[1])
        c.execute("DELETE FROM project_summary")
        c.execute(
            "INSERT INTO project_summary (summary_id, total_invested, total_profit) VALUES (1, %s, %s)",
            (invested, profit),
        )
        c.execute("UPDATE manager_wallet SET balance = 0 WHERE wallet_id=1")
        self.con.commit()
        c.close()
        return True

    def investor_withdraw(self, investor_id):
        c = self.cur()
        c.execute("SELECT balance, withdrawn FROM investor_accounts WHERE investor_id=%s FOR UPDATE", (investor_id,))
        row = c.fetchone()
        if not row:
            self.con.rollback()
            c.close()
            return False
        row_any = cast(Any, row)
        bal = float(row_any[0])
        withdrawn = bool(row_any[1])
        if withdrawn or bal <= 0:
            self.con.rollback()
            c.close()
            return False

        c.execute("UPDATE investor_accounts SET balance=0, withdrawn=1 WHERE investor_id=%s", (investor_id,))
        self.con.commit()
        c.close()
        return True

    def total_profit(self):
        summary = self.project_summary()
        if summary:
            return float(summary["total_profit"])

        c = self.cur()
        try:
            c.execute("SELECT COALESCE(SUM(amount), 0) * 0.4 FROM deposits WHERE status='approved'")
            row = c.fetchone()
            c.close()
            if not row:
                return 0.0
            row_any = cast(Any, row)
            return float(row_any[0])
        except Exception:
            c.close()
            return 0.0

    def project_summary(self):
        c = self.cur()
        try:
            c.execute("SELECT total_invested, total_profit, closed_at FROM project_summary WHERE summary_id=1")
            row = c.fetchone()
            c.close()
            if not row:
                return None
            row_any = cast(Any, row)
            return {
                "total_invested": float(row_any[0]),
                "total_profit": float(row_any[1]),
                "closed_at": str(row_any[2]),
            }
        except Exception:
            c.close()
            return None

    def project_closed(self):
        return self.project_summary() is not None

    def manager_daily_costs(self):
        c = self.cur()
        c.execute(
            """
            SELECT cost_id, purpose, amount, created_at
            FROM daily_costs
            ORDER BY cost_id DESC
            """
        )
        rows = c.fetchall()
        c.close()

        result = []
        for row in rows:
            row_any = cast(Any, row)
            result.append(
                {
                    "cost_id": int(row_any[0]),
                    "purpose": str(row_any[1]),
                    "amount": float(row_any[2]),
                    "created_at": str(row_any[3]),
                }
            )
        return result

    def manager_cost_summary(self):
        c = self.cur()
        c.execute("SELECT COUNT(*), COALESCE(SUM(amount), 0) FROM daily_costs")
        row = c.fetchone()
        c.close()
        if not row:
            return {"count": 0, "total": 0.0}

        row_any = cast(Any, row)
        return {"count": int(row_any[0]), "total": float(row_any[1])}
