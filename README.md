# Phoenix Livestock Investment Management System

**A complete investment management system with role-based access, income/expense tracking, and automated profit distribution.**

Built with: **Python 3.10+** | **Tkinter GUI** | **MySQL Database**

---

## 🎯 Features

- **Manager Panel**: Track income (+) and expenses (−) with real-time profit calculation
- **Admin Panel**: Approve deposits, monitor entries, close projects, and start new cycles
- **Investor Panel**: Submit deposits, view profit calculations, and withdraw final balance
- **Profit Calculation**: 40% of net profit distributed proportionally to investors
- **Project Management**: Close completed projects and reset for new investment cycles

---

## 🚀 Quick Start

### Windows

1. **Install Python 3.10+** and add to PATH
2. **Install MySQL** and remember root password
3. Clone repo and create venv:
   ```powershell
   git clone https://github.com/ridwan2005ahmed/Phoenix-Livestock-Investment-Management-System.git
   cd Phoenix-Livestock-Investment-Management-System-main
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. **Edit `config.py`** with your MySQL credentials
5. **Run**: `python app.py`

### Linux/macOS

```bash
git clone https://github.com/ridwan2005ahmed/Phoenix-Livestock-Investment-Management-System.git
cd Phoenix-Livestock-Investment-Management-System-main
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Edit config.py with credentials
python3 app.py
```

---

## 👤 Demo Users

| Role | ID | Password |
|------|----|----|
| Admin | admin | 1234 |
| Manager | manager | 1234 |
| Investor | investor | 1234 |

---

## 📊 Profit Formula

```
Net Profit = Total Income − Total Expense
Profit Share = Net Profit × 40% × (Investor's Deposit / Total Deposits)
Final Balance = Invested Amount + Profit Share
```

---

## 📋 File Structure

- `app.py` - Main entry point
- `config.py` - Database config (edit with your credentials)
- `db.py` - Database & profit calculations
- `ui.py` - Login/signup interface
- `admin_panel.py` - Admin features
- `manager_panel.py` - Manager features
- `investor_panel.py` - Investor features
- `requirements.txt` - Dependencies
- `venv/` - Virtual environment

---

## 🔧 Troubleshooting

**MySQL connection failed**: Check `config.py` credentials and MySQL is running
**Module not found**: Ensure venv is activated and `pip install -r requirements.txt` ran
**Port in use**: Close previous app instances

---

**See README.md for detailed setup instructions and USAGE_GUIDE.md for complete feature documentation.**
