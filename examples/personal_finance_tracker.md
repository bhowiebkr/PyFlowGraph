# Personal Finance Tracker

Financial transaction processing system with CSV parsing, category analysis, balance calculations, and dashboard reporting. Implements comma-separated value parsing, defaultdict aggregation, running balance computation, and formatted financial reporting with health metrics.

## Node: Transaction Input & Parser (ID: transaction-input)

Parses CSV-formatted transaction data using string.split(',') on newline-separated input. Expected format: "date,amount,category,description". Uses datetime.strptime() for date validation with "%Y-%m-%d" format. Handles parsing errors with try-except blocks and validates minimum 4 comma-separated fields per line.

Categorizes transactions by amount sign: negative values = "Expense", positive = "Income". Sorts results by date using lambda key function. Returns Tuple[List[Dict], float] containing parsed transaction dictionaries and starting balance. Each transaction dict includes date, amount, category, description, type, and original_line fields.

GUI includes QDoubleSpinBox for starting balance (-999999 to 999999 range) and QTextEdit for transaction input with CSV format examples in placeholder text.

### Metadata

```json
{
  "uuid": "transaction-input",
  "title": "Transaction Input & Parser",
  "pos": [
    75.66600000000005,
    221.29225
  ],
  "size": [
    280,
    435
  ],
  "colors": {
    "title": "#007bff",
    "body": "#0056b3"
  },
  "gui_state": {
    "transactions_text": "",
    "starting_balance": 1000.0
  }
}
```

### Logic

```python
import datetime
from typing import List, Dict, Tuple

@node_entry
def parse_transactions(transactions_text: str, starting_balance: float) -> Tuple[List[Dict], float]:
    transactions = []
    lines = [line.strip() for line in transactions_text.split('\n') if line.strip()]
    
    for line in lines:
        # Expected format: "date,amount,category,description"
        # Example: "2024-01-15,-50.00,Food,Grocery shopping"
        try:
            parts = [part.strip() for part in line.split(',')]
            if len(parts) >= 4:
                date_str = parts[0]
                amount = float(parts[1])
                category = parts[2]
                description = ','.join(parts[3:])  # In case description has commas
                
                # Validate date
                try:
                    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                    date_formatted = date_obj.strftime("%Y-%m-%d")
                except:
                    date_formatted = date_str  # Keep original if parsing fails
                
                # Categorize transaction type
                transaction_type = "Expense" if amount < 0 else "Income"
                
                transactions.append({
                    'date': date_formatted,
                    'amount': amount,
                    'category': category,
                    'description': description,
                    'type': transaction_type,
                    'original_line': line
                })
            else:
                print(f"Skipping invalid line: {line}")
        except ValueError as e:
            print(f"Error parsing line '{line}': {e}")
    
    # Sort by date
    transactions.sort(key=lambda x: x['date'])
    
    print(f"\n=== TRANSACTION PARSING ===")
    print(f"Starting balance: ${starting_balance:.2f}")
    print(f"Parsed {len(transactions)} transactions")
    
    total_income = sum(t['amount'] for t in transactions if t['amount'] > 0)
    total_expenses = sum(abs(t['amount']) for t in transactions if t['amount'] < 0)
    
    print(f"Total income: ${total_income:.2f}")
    print(f"Total expenses: ${total_expenses:.2f}")
    
    return transactions, starting_balance
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QLineEdit, QTextEdit, QPushButton, QDoubleSpinBox

layout.addWidget(QLabel('Starting Balance ($):', parent))
widgets['starting_balance'] = QDoubleSpinBox(parent)
widgets['starting_balance'].setRange(-999999, 999999)
widgets['starting_balance'].setValue(1000.00)
widgets['starting_balance'].setDecimals(2)
layout.addWidget(widgets['starting_balance'])

layout.addWidget(QLabel('Transactions (date,amount,category,description):', parent))
widgets['transactions_text'] = QTextEdit(parent)
widgets['transactions_text'].setMinimumHeight(180)
widgets['transactions_text'].setPlaceholderText('Example:\n2024-01-15,-50.00,Food,Grocery shopping\n2024-01-16,2500.00,Salary,Monthly paycheck\n2024-01-17,-25.50,Transport,Gas station')
layout.addWidget(widgets['transactions_text'])

widgets['parse_btn'] = QPushButton('Parse Transactions', parent)
layout.addWidget(widgets['parse_btn'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {
        'transactions_text': widgets['transactions_text'].toPlainText(),
        'starting_balance': widgets['starting_balance'].value()
    }

def set_initial_state(widgets, state):
    widgets['transactions_text'].setPlainText(state.get('transactions_text', ''))
    widgets['starting_balance'].setValue(state.get('starting_balance', 1000.0))
```


## Node: Category & Pattern Analyzer (ID: category-analyzer)

Analyzes spending patterns using defaultdict for category aggregation. Processes only negative amounts (expenses), accumulating totals and counts per category. Extracts monthly spending by parsing YYYY-MM substring from date fields using slice notation.

Sorts category results by amount in descending order using sorted() with reverse=True. Calculates pattern metrics including total expenses, largest category identification, percentage calculations, and category averages. Returns Tuple[Dict, Dict, Dict] for category summary, monthly summary, and patterns.

Pattern analysis includes largest_category identification, percentage of total expenses, category count, and average spending per category. Monthly analysis creates time-series data for spending trends over YYYY-MM periods.

### Metadata

```json
{
  "uuid": "category-analyzer",
  "title": "Category & Pattern Analyzer",
  "pos": [
    508.0218749999999,
    110.45725000000002
  ],
  "size": [
    250,
    168
  ],
  "colors": {
    "title": "#28a745",
    "body": "#1e7e34"
  },
  "gui_state": {}
}
```

### Logic

```python
from typing import List, Dict, Tuple
from collections import defaultdict
import datetime

@node_entry
def analyze_categories(transactions: List[Dict]) -> Tuple[Dict, Dict, Dict]:
    if not transactions:
        return {}, {}, {}
    
    # Category analysis
    category_totals = defaultdict(float)
    category_counts = defaultdict(int)
    monthly_spending = defaultdict(float)
    
    for transaction in transactions:
        amount = transaction['amount']
        category = transaction['category']
        date = transaction['date']
        
        # Category totals (separate income and expenses)
        if amount < 0:  # Expense
            category_totals[category] += abs(amount)
            category_counts[category] += 1
        
        # Monthly analysis
        try:
            month = date[:7]  # Extract YYYY-MM
            if amount < 0:
                monthly_spending[month] += abs(amount)
        except:
            pass
    
    # Convert to regular dicts and sort
    category_summary = dict(sorted(category_totals.items(), key=lambda x: x[1], reverse=True))
    monthly_summary = dict(sorted(monthly_spending.items()))
    
    # Calculate patterns
    patterns = {}
    if category_summary:
        total_expenses = sum(category_summary.values())
        largest_category = max(category_summary.items(), key=lambda x: x[1])
        
        patterns['total_expenses'] = total_expenses
        patterns['largest_category'] = largest_category[0]
        patterns['largest_amount'] = largest_category[1]
        patterns['largest_percentage'] = (largest_category[1] / total_expenses) * 100
        patterns['category_count'] = len(category_summary)
        patterns['avg_per_category'] = total_expenses / len(category_summary) if category_summary else 0
    
    print(f"\n=== CATEGORY ANALYSIS ===")
    print(f"Expense categories: {len(category_summary)}")
    if patterns:
        print(f"Largest category: {patterns['largest_category']} (${patterns['largest_amount']:.2f})")
        print(f"Total expenses: ${patterns['total_expenses']:.2f}")
    
    return category_summary, monthly_summary, patterns
```


## Node: Budget & Balance Calculator (ID: budget-calculator)

Calculates financial metrics by separating positive (income) and negative (expense) amounts using sum() with conditional list comprehensions. Computes net change as income minus expenses, final balance as starting balance plus net change. Generates running balance history by iterating through date-sorted transactions.

Creates health metrics including income/expense ratio, savings rate percentage ((net_change/total_income)*100), average daily spending (total_expenses/30), balance trend determination, and minimum balance tracking. Returns Tuple[float, float, float, float, Dict] for income, expenses, net change, final balance, and health metrics.

Running balance calculation maintains chronological transaction processing, creating balance history list with date, balance, transaction description, and amount for each entry. Handles division by zero for ratio calculations using conditional expressions.

### Metadata

```json
{
  "uuid": "budget-calculator",
  "title": "Budget & Balance Calculator",
  "pos": [
    497.37575000000004,
    456.08349999999996
  ],
  "size": [
    250,
    218
  ],
  "colors": {
    "title": "#fd7e14",
    "body": "#e8590c"
  },
  "gui_state": {}
}
```

### Logic

```python
from typing import List, Dict, Tuple

@node_entry
def calculate_budget(transactions: List[Dict], starting_balance: float) -> Tuple[float, float, float, float, Dict]:
    if not transactions:
        return starting_balance, 0, 0, starting_balance, {}
    
    total_income = sum(t['amount'] for t in transactions if t['amount'] > 0)
    total_expenses = sum(abs(t['amount']) for t in transactions if t['amount'] < 0)
    net_change = total_income - total_expenses
    final_balance = starting_balance + net_change
    
    # Calculate running balance for each transaction
    running_balance = starting_balance
    balance_history = []
    
    for transaction in sorted(transactions, key=lambda x: x['date']):
        running_balance += transaction['amount']
        balance_history.append({
            'date': transaction['date'],
            'balance': round(running_balance, 2),
            'transaction': transaction['description'],
            'amount': transaction['amount']
        })
    
    # Financial health indicators
    health_metrics = {
        'income_expense_ratio': total_income / total_expenses if total_expenses > 0 else float('inf'),
        'savings_rate': (net_change / total_income * 100) if total_income > 0 else 0,
        'avg_daily_spending': total_expenses / 30 if total_expenses > 0 else 0,
        'balance_trend': 'Increasing' if net_change > 0 else 'Decreasing',
        'lowest_balance': min(h['balance'] for h in balance_history) if balance_history else starting_balance
    }
    
    print(f"\n=== BUDGET CALCULATION ===")
    print(f"Starting: ${starting_balance:.2f}")
    print(f"Income: ${total_income:.2f}")
    print(f"Expenses: ${total_expenses:.2f}")
    print(f"Net change: ${net_change:.2f}")
    print(f"Final balance: ${final_balance:.2f}")
    print(f"Savings rate: {health_metrics['savings_rate']:.1f}%")
    
    return total_income, total_expenses, net_change, final_balance, health_metrics
```


## Node: Personal Finance Dashboard (ID: financial-dashboard)

Formats comprehensive financial report using string concatenation with fixed-width formatting. Creates sections for account overview, income vs expenses, financial health, top spending categories, monthly trends, recent transactions, and automated insights. Uses f-string formatting with width specifiers for column alignment.

Implementes conditional logic for financial insights: negative savings rate warnings, category concentration alerts (>40% threshold), and negative balance warnings. Recent transactions display shows top 5 sorted by date in reverse chronological order. Category percentages calculated as (category_amount/total_expenses)*100.

GUI integration includes QTextEdit with Courier New monospace font for formatted display, export functionality, budget alert setup, and new period initialization. Dashboard output includes visual indicators and actionable recommendations based on calculated financial health metrics.

### Metadata

```json
{
  "uuid": "financial-dashboard",
  "title": "Personal Finance Dashboard",
  "pos": [
    913.87675,
    318.2505
  ],
  "size": [
    276,
    753
  ],
  "colors": {
    "title": "#6c757d",
    "body": "#545b62"
  },
  "gui_state": {}
}
```

### Logic

```python
from typing import List, Dict

@node_entry
def create_finance_dashboard(transactions: List[Dict], starting_balance: float, category_summary: Dict, monthly_summary: Dict, patterns: Dict, total_income: float, total_expenses: float, net_change: float, final_balance: float, health_metrics: Dict) -> str:
    dashboard = "\n" + "="*65 + "\n"
    dashboard += "              PERSONAL FINANCE DASHBOARD\n"
    dashboard += "="*65 + "\n\n"
    
    # Account Overview
    dashboard += f"💰 ACCOUNT OVERVIEW\n"
    dashboard += f"   Starting Balance:    ${starting_balance:10,.2f}\n"
    dashboard += f"   Final Balance:       ${final_balance:10,.2f}\n"
    dashboard += f"   Net Change:          ${net_change:10,.2f}\n"
    if net_change >= 0:
        dashboard += f"   Status: 📈 POSITIVE\n\n"
    else:
        dashboard += f"   Status: 📉 NEGATIVE\n\n"
    
    # Income vs Expenses
    dashboard += f"📊 INCOME vs EXPENSES\n"
    dashboard += f"   Total Income:        ${total_income:10,.2f}\n"
    dashboard += f"   Total Expenses:      ${total_expenses:10,.2f}\n"
    if total_expenses > 0:
        ratio = total_income / total_expenses
        dashboard += f"   Income/Expense Ratio: {ratio:9.2f}\n"
    dashboard += "\n"
    
    # Financial Health
    if health_metrics:
        dashboard += f"🏥 FINANCIAL HEALTH\n"
        dashboard += f"   Savings Rate:        {health_metrics['savings_rate']:8.1f}%\n"
        dashboard += f"   Avg Daily Spending:  ${health_metrics['avg_daily_spending']:8.2f}\n"
        dashboard += f"   Balance Trend:       {health_metrics['balance_trend']}\n"
        dashboard += f"   Lowest Balance:      ${health_metrics['lowest_balance']:10,.2f}\n\n"
    
    # Top Spending Categories
    if category_summary:
        dashboard += f"🛒 TOP SPENDING CATEGORIES\n"
        for i, (category, amount) in enumerate(list(category_summary.items())[:5], 1):
            percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
            dashboard += f"   {i}. {category:<15} ${amount:8.2f} ({percentage:4.1f}%)\n"
        dashboard += "\n"
    
    # Monthly Spending Trend
    if monthly_summary:
        dashboard += f"📅 MONTHLY SPENDING\n"
        for month, amount in monthly_summary.items():
            dashboard += f"   {month}:             ${amount:10,.2f}\n"
        dashboard += "\n"
    
    # Recent Transactions
    if transactions:
        dashboard += f"📝 RECENT TRANSACTIONS\n"
        recent = sorted(transactions, key=lambda x: x['date'], reverse=True)[:5]
        for t in recent:
            sign = "+" if t['amount'] > 0 else ""
            dashboard += f"   {t['date']} {sign}${t['amount']:8.2f} {t['category']:<10} {t['description'][:20]}\n"
        dashboard += "\n"
    
    # Financial Insights
    dashboard += f"💡 INSIGHTS & RECOMMENDATIONS\n"
    
    if health_metrics.get('savings_rate', 0) < 0:
        dashboard += f"   • ⚠️  You're spending more than earning\n"
    elif health_metrics.get('savings_rate', 0) < 10:
        dashboard += f"   • 💡 Try to save at least 10% of income\n"
    else:
        dashboard += f"   • ✅ Good savings rate!\n"
    
    if category_summary and patterns:
        largest_cat = patterns.get('largest_category', '')
        largest_pct = patterns.get('largest_percentage', 0)
        if largest_pct > 40:
            dashboard += f"   • ⚠️  {largest_cat} represents {largest_pct:.1f}% of expenses\n"
    
    if health_metrics.get('lowest_balance', 0) < 0:
        dashboard += f"   • ⚠️  Account went negative (${health_metrics['lowest_balance']:.2f})\n"
    
    dashboard += "\n" + "="*65
    
    print(dashboard)
    return dashboard
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QTextEdit, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

title_label = QLabel('Finance Dashboard', parent)
title_font = QFont()
title_font.setPointSize(14)
title_font.setBold(True)
title_label.setFont(title_font)
layout.addWidget(title_label)

widgets['dashboard_display'] = QTextEdit(parent)
widgets['dashboard_display'].setMinimumHeight(280)
widgets['dashboard_display'].setReadOnly(True)
widgets['dashboard_display'].setPlainText('Enter transactions to generate financial dashboard...')
font = QFont('Courier New', 9)
widgets['dashboard_display'].setFont(font)
layout.addWidget(widgets['dashboard_display'])

widgets['export_btn'] = QPushButton('Export Report', parent)
layout.addWidget(widgets['export_btn'])

widgets['budget_alert_btn'] = QPushButton('Set Budget Alerts', parent)
layout.addWidget(widgets['budget_alert_btn'])

widgets['new_period_btn'] = QPushButton('Start New Period', parent)
layout.addWidget(widgets['new_period_btn'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {}

def set_values(widgets, outputs):
    dashboard = outputs.get('output_1', 'No dashboard data')
    widgets['dashboard_display'].setPlainText(dashboard)
```


## Connections

```json
[
  {
    "start_node_uuid": "transaction-input",
    "start_pin_name": "exec_out",
    "end_node_uuid": "category-analyzer",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "transaction-input",
    "start_pin_name": "output_1",
    "end_node_uuid": "category-analyzer",
    "end_pin_name": "transactions"
  },
  {
    "start_node_uuid": "transaction-input",
    "start_pin_name": "exec_out",
    "end_node_uuid": "budget-calculator",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "transaction-input",
    "start_pin_name": "output_1",
    "end_node_uuid": "budget-calculator",
    "end_pin_name": "transactions"
  },
  {
    "start_node_uuid": "transaction-input",
    "start_pin_name": "output_2",
    "end_node_uuid": "budget-calculator",
    "end_pin_name": "starting_balance"
  },
  {
    "start_node_uuid": "category-analyzer",
    "start_pin_name": "exec_out",
    "end_node_uuid": "financial-dashboard",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "transaction-input",
    "start_pin_name": "output_1",
    "end_node_uuid": "financial-dashboard",
    "end_pin_name": "transactions"
  },
  {
    "start_node_uuid": "transaction-input",
    "start_pin_name": "output_2",
    "end_node_uuid": "financial-dashboard",
    "end_pin_name": "starting_balance"
  },
  {
    "start_node_uuid": "category-analyzer",
    "start_pin_name": "output_1",
    "end_node_uuid": "financial-dashboard",
    "end_pin_name": "category_summary"
  },
  {
    "start_node_uuid": "category-analyzer",
    "start_pin_name": "output_2",
    "end_node_uuid": "financial-dashboard",
    "end_pin_name": "monthly_summary"
  },
  {
    "start_node_uuid": "category-analyzer",
    "start_pin_name": "output_3",
    "end_node_uuid": "financial-dashboard",
    "end_pin_name": "patterns"
  },
  {
    "start_node_uuid": "budget-calculator",
    "start_pin_name": "output_1",
    "end_node_uuid": "financial-dashboard",
    "end_pin_name": "total_income"
  },
  {
    "start_node_uuid": "budget-calculator",
    "start_pin_name": "output_2",
    "end_node_uuid": "financial-dashboard",
    "end_pin_name": "total_expenses"
  },
  {
    "start_node_uuid": "budget-calculator",
    "start_pin_name": "output_3",
    "end_node_uuid": "financial-dashboard",
    "end_pin_name": "net_change"
  },
  {
    "start_node_uuid": "budget-calculator",
    "start_pin_name": "output_4",
    "end_node_uuid": "financial-dashboard",
    "end_pin_name": "final_balance"
  },
  {
    "start_node_uuid": "budget-calculator",
    "start_pin_name": "output_5",
    "end_node_uuid": "financial-dashboard",
    "end_pin_name": "health_metrics"
  }
]
```
