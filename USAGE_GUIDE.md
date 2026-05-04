# Usage Guide - Phoenix Livestock Investment Management System

## Complete Workflow Example

### Step 1: Admin Approves Deposits

1. Login: `admin` / `1234`
2. View "Pending Deposits" list
3. Select a deposit and click "Approve Selected"
4. Refresh to see updated status

### Step 2: Manager Tracks Income/Expense

1. Login: `manager` / `1234`
2. Enter description (e.g., "Livestock Feed")
3. Enter amount
4. Click **"+ Add Income"** or **"− Add Expense"**
5. View real-time profit summary

### Step 3: Admin Closes Project

1. Login as admin
2. Review income/expense entries
3. Verify Net Profit = Income - Expense
4. Click **"Close Project & Calculate"**
5. System calculates 40% distribution to investors

### Step 4: Investor Withdraws

1. Login as investor
2. View calculated profit share (after project closes)
3. Click **"Withdraw My Balance"**
4. Receive final balance = invested + profit_share

### Step 5: Start New Project

1. Admin clicks **"Start New Project"**
2. Wallet resets to ৳0
3. All old data cleared
4. New cycle begins

---

## Example Calculation

**Scenario:**
- 3 investors: Alice (৳20,000), Bob (৳12,000), Carol (৳8,000)
- Manager entries: Income ৳50,000 - Expense ৳10,000
- **Net Profit: ৳40,000**
- **40% Distribution: ৳16,000**

**Results:**

| Investor | Invested | Share % | Profit | Final |
|----------|----------|---------|--------|-------|
| Alice | ৳20,000 | 50% | ৳8,000 | ৳28,000 |
| Bob | ৳12,000 | 30% | ৳4,800 | ৳16,800 |
| Carol | ৳8,000 | 20% | ৳3,200 | ৳11,200 |

---

**For setup help, see README.md**
