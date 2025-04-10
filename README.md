# Simple Expense Tracker

Simple Expense Tracker is a lightweight, user-friendly desktop application designed to help you manage your personal finances. Built using Python's `tkinter` library for the GUI and `sqlite3` for data storage, this application allows you to track expenses, set budgets, and visualize spending patterns with ease.

---

## Features

1. **Expense Management**
   - Add, edit, and delete expenses with details such as amount, category, date, and description.
   - Input validation ensures accurate data entry (e.g., positive amounts, valid dates).

2. **Budget Management**
   - Set monthly budgets for each expense category.
   - View total spending, monthly budget, and remaining balance for the selected month and year.

3. **Data Visualization**
   - A pie chart (donut chart) displays spending distribution across categories for the selected period.
   - If no data exists for the selected period, the chart shows a "No data" message.

4. **Dynamic Filtering**
   - Filter expenses by month and year using dropdown menus.
   - Automatically refreshes data and charts when the selection changes.

5. **Default Categories**
   - Predefined categories like Food, Housing, Transportation, Entertainment, etc., are created automatically if none exist.

6. **Persistent Storage**
   - All data is stored in an SQLite database (`expenses.db`) located in the `data/` directory.

7. **Responsive Design**
   - The application adjusts its layout dynamically to fit the window size.
   - Scrollbars are added to the expense list for better usability.

8. **Resource Cleanup**
   - Ensures proper closure of the database connection when the application exits.

---

## Requirements

To run this project, you need the following:

- **Python 3.6 or higher**
- Required Python libraries:
  - `tkinter` (usually included with Python)
  - `sqlite3` (usually included with Python)
  - `matplotlib`
  - `datetime`
  - `calendar`

# Simple Expense Tracker

A simple, user-friendly desktop application to manage personal expenses, set budgets, and visualize spending habits. Built using Python's `Tkinter`, `SQLite`, and `Matplotlib`.

---

## 📦 Installation and Setup

### 1. Clone the Repository

Clone the project repository to your local machine:

```bash
git clone https://github.com/your-username/simple-expense-tracker.git
```

### 2. Navigate to the Project Directory

```bash
cd simple-expense-tracker
```

### 3. Install Dependencies

Install the required dependencies using pip:

```bash
pip install -r requirements.txt
```

> Note: If `matplotlib` is not installed, you can also install it separately:
```bash
pip install matplotlib
```

### 4. Run the Application

```bash
python expense_tracker.py
```

---

## 🧑‍💻 Usage Instructions

### ✅ Adding Expenses
- Click the **"Add Expense"** button.
- Fill in the details (amount, category, date, description).
- Click **"Save"**.

### ✏️ Editing Expenses
- Double-click an expense in the list to open the edit dialog.
- Modify the details and click **"Save"**.

### ❌ Deleting Expenses
- Select an expense from the list.
- Press the **"Delete"** key on your keyboard.

### 💰 Setting Budgets
- Click the **"Set Budget"** button.
- Enter budget amounts for each category.
- Click **"Save All"**.

### 📊 Viewing Data
- Use the **month** and **year** dropdowns to filter expenses.
- The summary section displays:
  - Total spending
  - Budget
  - Remaining balance
- A pie chart visualizes spending by category.

---

## 📁 Project Structure

```
simple-expense-tracker/
├── data/                  # Directory for SQLite database
│   └── expenses.db        # SQLite database file
├── expense_tracker.py     # Main application script
├── README.md              # Project documentation
└── requirements.txt       # List of required Python packages
```

---

## 📌 Features

- Track daily expenses by category
- Set and monitor monthly budgets
- Visualize data with charts
- Edit/delete expenses anytime
- Lightweight and easy to use

---

## 📋 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙌 Contributions

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

---

## 🧠 Credits

Developed with ❤️ using Python, Tkinter, SQLite, and Matplotlib.
