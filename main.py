from expense_data import load_expenses, save_expenses, validate_expense

def welcome():
    print("---------------------------------")
    print("Welcome to your Personal Expense Tracker!")
    print("You can add, view, and manage your expenses.")
    print("What would you like to do today?")
    print("1. Add an expense")
    print("2. View expenses")
    print("3. Calculate total expenses")
    print("4. Delete an expense")
    print("5. Filter expenses")
    print("6. Summarize expenses")
    print("7. Exit")

def add_expense(expenses):
    try:
        category = input("Enter the expense category: ")
        amount = input("Enter the expense amount: ")
        expense_date = input("Enter the expense date (YYYY-MM-DD): ")
        expense = validate_expense(category, amount, expense_date)
        expenses.append(expense)
        save_expenses(expenses)
        print("Expense added successfully!")

    except ValueError as e:
        print(f"Invalid expense: {e}")

def view_expense(expenses):
    if not expenses:
        print("No expenses to display.")
        return
    print("Your Expenses:")
    i = 1
    for e in expenses:
        print(f"{i}. {e['category']} - Php{e['amount']} on {e['date']}")
    print("---------------------------------")

def total_expenses(expenses):
    total = 0 
    for e in expenses:
        total += e['amount']
    print(f"Total expenses: Php{total}")


def delete_expense(expenses):
    view_expense(expenses)
    if not expenses:
        print("No expenses to delete.")
        return
    try:
        index = int(input("Enter the number of the expense to delete: ")) - 1
        if 0 <= index < len(expenses):
            deleted_expense = expenses.pop(index)
            save_expenses(expenses)
            print(f"Deleted expense: {deleted_expense['category']} - Php{deleted_expense['amount']} on {deleted_expense['date']}")
        else:
            print("Invalid index. Please try again.")
    except ValueError:
        print("Invalid input. Please enter a valid number.")
    except Exception as e:
        print(e)

def filter_expenses(expenses):
    category = input("Enter the category to filter by: ")
    filtered = [expense for expense in expenses if expense['category'].lower() == category.lower()]
    if not filtered:
        print(f"No expenses found for category '{category}'.")
        return
    print(f"Expenses in category '{category}':")
    for expense in filtered:
        print(f"{expense['category']} - Php{expense['amount']} on {expense['date']}")

def summarize_expenses(expenses):
    total = sum(expense['amount'] for expense in expenses)
    print(f"Total expenses: Php{total}")

def main():
    expenses = load_expenses()
    while True:
        welcome()
        print("---------------------------------")
        print()
        print()
        choice = input("Enter your choice: ")
        if choice == "1":
            add_expense(expenses)
        elif choice == "2":
            view_expense (expenses)
        elif choice == "3":
            total_expenses(expenses)
        elif choice == "4":
            delete_expense(expenses)
        elif choice == "5":
            filter_expenses(expenses)
        elif choice == "6":
            summarize_expenses(expenses)
        elif choice == "7":
            print("Exiting the Expense Tracker. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()