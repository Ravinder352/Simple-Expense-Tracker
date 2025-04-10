import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import calendar

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Expense Tracker")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Set up database
        self.setup_database()
        
        # Create default categories if none exist
        self.create_default_categories()
        
        # Variables
        self.selected_month = tk.StringVar(value=datetime.now().strftime("%B"))
        self.selected_year = tk.IntVar(value=datetime.now().year)
        self.expense_id = None
        
        # Create the main UI
        self.create_ui()
        
        # Populate initial data
        self.refresh_expense_list()
        self.update_stats()
    
    def setup_database(self):
        """Set up the SQLite database and tables"""
        if not os.path.exists('data'):
            os.makedirs('data')
            
        self.conn = sqlite3.connect('data/expenses.db')
        self.cursor = self.conn.cursor()
        
        # Create tables if they don't exist
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE
        )
        ''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY,
            amount REAL,
            category TEXT,
            date TEXT,
            description TEXT
        )
        ''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY,
            category TEXT,
            amount REAL,
            month TEXT,
            year INTEGER
        )
        ''')
        
        self.conn.commit()
    
    def create_default_categories(self):
        """Create default expense categories if none exist"""
        self.cursor.execute("SELECT COUNT(*) FROM categories")
        count = self.cursor.fetchone()[0]
        
        if count == 0:
            default_categories = ["Food", "Housing", "Transportation", "Entertainment", "Utilities", "Shopping", "Healthcare", "Other"]
            for category in default_categories:
                self.cursor.execute("INSERT INTO categories (name) VALUES (?)", (category,))
            self.conn.commit()
    
    def create_ui(self):
        """Create the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top frame for controls
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Month and year selection
        ttk.Label(control_frame, text="Month:").pack(side=tk.LEFT, padx=(0, 5))
        months = list(calendar.month_name)[1:]
        month_dropdown = ttk.Combobox(control_frame, textvariable=self.selected_month, values=months, width=10, state="readonly")
        month_dropdown.pack(side=tk.LEFT, padx=(0, 10))
        month_dropdown.bind("<<ComboboxSelected>>", lambda e: self.refresh_data())
        
        ttk.Label(control_frame, text="Year:").pack(side=tk.LEFT, padx=(0, 5))
        current_year = datetime.now().year
        years = list(range(current_year - 5, current_year + 2))
        year_dropdown = ttk.Combobox(control_frame, textvariable=self.selected_year, values=years, width=6, state="readonly")
        year_dropdown.pack(side=tk.LEFT)
        year_dropdown.bind("<<ComboboxSelected>>", lambda e: self.refresh_data())
        
        # Buttons for actions
        add_btn = ttk.Button(control_frame, text="Add Expense", command=self.add_expense)
        add_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        add_budget_btn = ttk.Button(control_frame, text="Set Budget", command=self.set_budget)
        add_budget_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Left panel for expense list
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Expense list
        ttk.Label(left_frame, text="Expenses:", font=("", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        # Treeview for expenses
        columns = ("Date", "Category", "Amount", "Description")
        self.expense_tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=15)
        
        # Define headings
        for col in columns:
            self.expense_tree.heading(col, text=col)
            width = 100 if col != "Description" else 150
            self.expense_tree.column(col, width=width)
        
        self.expense_tree.pack(fill=tk.BOTH, expand=True)
        self.expense_tree.bind("<Double-1>", self.edit_expense)
        self.expense_tree.bind("<Delete>", self.delete_selected_expense)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.expense_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.expense_tree.configure(yscrollcommand=scrollbar.set)
        
        # Right panel for summary and charts
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Summary section
        summary_frame = ttk.LabelFrame(right_frame, text="Monthly Summary")
        summary_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.total_label = ttk.Label(summary_frame, text="Total Spent: $0.00")
        self.total_label.pack(anchor=tk.W, pady=2)
        
        self.budget_label = ttk.Label(summary_frame, text="Monthly Budget: $0.00")
        self.budget_label.pack(anchor=tk.W, pady=2)
        
        self.remaining_label = ttk.Label(summary_frame, text="Remaining: $0.00")
        self.remaining_label.pack(anchor=tk.W, pady=2)
        
        # Chart frame
        chart_frame = ttk.LabelFrame(right_frame, text="Spending by Category")
        chart_frame.pack(fill=tk.BOTH, expand=True)
        
        self.chart_canvas = None
        self.figure = plt.Figure(figsize=(5, 4), dpi=100)
        self.chart_subplot = self.figure.add_subplot(111)
        self.chart_canvas = FigureCanvasTkAgg(self.figure, chart_frame)
        self.chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def refresh_data(self):
        """Refresh all data based on selected month/year"""
        self.refresh_expense_list()
        self.update_stats()
    
    def refresh_expense_list(self):
        """Refresh the expense list based on selected month and year"""
        # Clear current items
        for item in self.expense_tree.get_children():
            self.expense_tree.delete(item)
        
        # Get month number from name
        month_num = list(calendar.month_name).index(self.selected_month.get())
        year = self.selected_year.get()
        
        # Format dates for filtering
        start_date = f"{year}-{month_num:02d}-01"
        if month_num == 12:
            end_date = f"{year+1}-01-01"
        else:
            end_date = f"{year}-{month_num+1:02d}-01"
        
        # Get expenses for the selected month
        self.cursor.execute("""
            SELECT id, date, category, amount, description 
            FROM expenses 
            WHERE date >= ? AND date < ?
            ORDER BY date DESC
        """, (start_date, end_date))
        
        expenses = self.cursor.fetchall()
        
        # Add to treeview
        for expense in expenses:
            id, date, category, amount, description = expense
            # Format date for display (YYYY-MM-DD to DD/MM/YYYY)
            display_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d/%m/%Y")
            self.expense_tree.insert("", "end", values=(display_date, category, f"${amount:.2f}", description), tags=(id,))
    
    def update_stats(self):
        """Update statistics and chart"""
        month_num = list(calendar.month_name).index(self.selected_month.get())
        year = self.selected_year.get()
        
        # Format dates for filtering
        start_date = f"{year}-{month_num:02d}-01"
        if month_num == 12:
            end_date = f"{year+1}-01-01"
        else:
            end_date = f"{year}-{month_num+1:02d}-01"
        
        # Calculate total spent
        self.cursor.execute("""
            SELECT SUM(amount) FROM expenses 
            WHERE date >= ? AND date < ?
        """, (start_date, end_date))
        
        total_spent = self.cursor.fetchone()[0] or 0
        
        # Get monthly budget
        self.cursor.execute("""
            SELECT SUM(amount) FROM budgets 
            WHERE month = ? AND year = ?
        """, (self.selected_month.get(), year))
        
        monthly_budget = self.cursor.fetchone()[0] or 0
        remaining = monthly_budget - total_spent
        
        # Update labels
        self.total_label.configure(text=f"Total Spent: ${total_spent:.2f}")
        self.budget_label.configure(text=f"Monthly Budget: ${monthly_budget:.2f}")
        self.remaining_label.configure(text=f"Remaining: ${remaining:.2f}")
        
        # Set label color based on budget status
        if remaining < 0:
            self.remaining_label.configure(foreground="red")
        else:
            self.remaining_label.configure(foreground="green")
        
        # Update chart
        self.update_chart(start_date, end_date)
    
    def update_chart(self, start_date, end_date):
        """Update the pie chart showing expenses by category"""
        self.chart_subplot.clear()
        
        # Get expenses by category
        self.cursor.execute("""
            SELECT category, SUM(amount) 
            FROM expenses 
            WHERE date >= ? AND date < ?
            GROUP BY category
        """, (start_date, end_date))
        
        category_data = self.cursor.fetchall()
        
        if not category_data:
            self.chart_subplot.text(0.5, 0.5, "No data for selected period", 
                                 horizontalalignment='center', verticalalignment='center')
        else:
            categories = [item[0] for item in category_data]
            amounts = [item[1] for item in category_data]
            
            # Create pie chart
            wedges, texts, autotexts = self.chart_subplot.pie(
                amounts, 
                labels=categories, 
                autopct='%1.1f%%',
                startangle=90,
                wedgeprops={'width': 0.5}  # For a donut chart effect
            )
            
            # Make the labels more readable
            for text in texts:
                text.set_fontsize(8)
            for autotext in autotexts:
                autotext.set_fontsize(8)
                autotext.set_color('white')
            
            self.chart_subplot.set_title(f"Spending by Category ({self.selected_month.get()} {self.selected_year.get()})")
            self.chart_subplot.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        
        # Redraw the canvas
        self.chart_canvas.draw()
    
    def add_expense(self):
        """Open a dialog to add a new expense"""
        self.open_expense_dialog()
    
    def edit_expense(self, event):
        """Open a dialog to edit the selected expense"""
        selected_item = self.expense_tree.selection()
        if not selected_item:
            return
        
        item_id = self.expense_tree.item(selected_item)['tags'][0]
        self.cursor.execute("SELECT * FROM expenses WHERE id = ?", (item_id,))
        expense = self.cursor.fetchone()
        
        if expense:
            self.expense_id = expense[0]
            self.open_expense_dialog(expense)
    
    def delete_selected_expense(self, event):
        """Delete the selected expense"""
        selected_item = self.expense_tree.selection()
        if not selected_item:
            return
        
        item_id = self.expense_tree.item(selected_item)['tags'][0]
        
        if messagebox.askyesno("Delete Expense", "Are you sure you want to delete this expense?"):
            self.cursor.execute("DELETE FROM expenses WHERE id = ?", (item_id,))
            self.conn.commit()
            self.refresh_data()
    
    def open_expense_dialog(self, expense=None):
        """Open dialog to add or edit an expense"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Expense" if not expense else "Edit Expense")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        dialog_frame = ttk.Frame(dialog, padding=20)
        dialog_frame.pack(fill=tk.BOTH, expand=True)
        
        # Get categories for dropdown
        self.cursor.execute("SELECT name FROM categories ORDER BY name")
        categories = [row[0] for row in self.cursor.fetchall()]
        
        # Amount
        ttk.Label(dialog_frame, text="Amount ($):").grid(row=0, column=0, sticky=tk.W, pady=5)
        amount_var = tk.StringVar(value=str(expense[1]) if expense else "")
        amount_entry = ttk.Entry(dialog_frame, textvariable=amount_var, width=15)
        amount_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Category
        ttk.Label(dialog_frame, text="Category:").grid(row=1, column=0, sticky=tk.W, pady=5)
        category_var = tk.StringVar(value=expense[2] if expense else categories[0])
        category_dropdown = ttk.Combobox(dialog_frame, textvariable=category_var, values=categories, state="readonly", width=15)
        category_dropdown.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Date
        ttk.Label(dialog_frame, text="Date (YYYY-MM-DD):").grid(row=2, column=0, sticky=tk.W, pady=5)
        if expense:
            default_date = expense[3]
        else:
            default_date = datetime.now().strftime("%Y-%m-%d")
        date_var = tk.StringVar(value=default_date)
        date_entry = ttk.Entry(dialog_frame, textvariable=date_var, width=15)
        date_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Description
        ttk.Label(dialog_frame, text="Description:").grid(row=3, column=0, sticky=tk.W, pady=5)
        description_var = tk.StringVar(value=expense[4] if expense else "")
        description_entry = ttk.Entry(dialog_frame, textvariable=description_var, width=30)
        description_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(dialog_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(
            button_frame, 
            text="Save", 
            command=lambda: self.save_expense(
                expense[0] if expense else None,
                amount_var.get(),
                category_var.get(),
                date_var.get(),
                description_var.get(),
                dialog
            )
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)
        
        # Focus on amount entry
        amount_entry.focus_set()
    
    def save_expense(self, id, amount_str, category, date_str, description, dialog):
        """Save the expense to database"""
        # Validate input
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be positive")
                
            # Validate date format
            datetime.strptime(date_str, "%Y-%m-%d")
            
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            return
        
        # Save to database
        if id:  # Update existing
            self.cursor.execute(
                "UPDATE expenses SET amount = ?, category = ?, date = ?, description = ? WHERE id = ?",
                (amount, category, date_str, description, id)
            )
        else:  # Add new
            self.cursor.execute(
                "INSERT INTO expenses (amount, category, date, description) VALUES (?, ?, ?, ?)",
                (amount, category, date_str, description)
            )
        
        self.conn.commit()
        dialog.destroy()
        self.refresh_data()
    
    def set_budget(self):
        """Set budget for categories"""
        budget_dialog = tk.Toplevel(self.root)
        budget_dialog.title("Set Budget")
        budget_dialog.geometry("400x400")
        budget_dialog.transient(self.root)
        budget_dialog.grab_set()
        
        dialog_frame = ttk.Frame(budget_dialog, padding=20)
        dialog_frame.pack(fill=tk.BOTH, expand=True)
        
        # Month and year selection (same as current view)
        month = self.selected_month.get()
        year = self.selected_year.get()
        
        ttk.Label(dialog_frame, text=f"Setting Budget for {month} {year}", font=("", 12, "bold")).pack(anchor=tk.W, pady=(0, 15))
        
        # Get categories
        self.cursor.execute("SELECT name FROM categories ORDER BY name")
        categories = self.cursor.fetchall()
        
        # Create input fields for each category
        budget_vars = {}
        
        for i, (category,) in enumerate(categories):
            frame = ttk.Frame(dialog_frame)
            frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(frame, text=category, width=15).pack(side=tk.LEFT)
            
            # Get existing budget if any
            self.cursor.execute(
                "SELECT amount FROM budgets WHERE category = ? AND month = ? AND year = ?",
                (category, month, year)
            )
            existing = self.cursor.fetchone()
            default_amount = existing[0] if existing else 0
            
            var = tk.StringVar(value=str(default_amount))
            budget_vars[category] = var
            
            ttk.Entry(frame, textvariable=var, width=10).pack(side=tk.LEFT, padx=5)
            ttk.Label(frame, text="$").pack(side=tk.LEFT)
        
        # Buttons
        button_frame = ttk.Frame(dialog_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(
            button_frame,
            text="Save All",
            command=lambda: self.save_budgets(budget_vars, month, year, budget_dialog)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=budget_dialog.destroy
        ).pack(side=tk.LEFT, padx=5)
    
    def save_budgets(self, budget_vars, month, year, dialog):
        """Save budgets for all categories"""
        try:
            for category, var in budget_vars.items():
                amount = float(var.get())
                if amount < 0:
                    raise ValueError(f"Budget for {category} cannot be negative")
                
                # Check if budget exists
                self.cursor.execute(
                    "SELECT id FROM budgets WHERE category = ? AND month = ? AND year = ?",
                    (category, month, year)
                )
                existing = self.cursor.fetchone()
                
                if existing:
                    self.cursor.execute(
                        "UPDATE budgets SET amount = ? WHERE id = ?",
                        (amount, existing[0])
                    )
                else:
                    self.cursor.execute(
                        "INSERT INTO budgets (category, amount, month, year) VALUES (?, ?, ?, ?)",
                        (category, amount, month, year)
                    )
            
            self.conn.commit()
            dialog.destroy()
            self.update_stats()
            messagebox.showinfo("Success", "Budgets saved successfully!")
            
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
    
    def __del__(self):
        """Clean up database connection when app closes"""
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
# </lov-write>