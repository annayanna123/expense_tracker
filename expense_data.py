import csv
import math
from datetime import date
from pathlib import Path

EXPENSES_FILE = Path(__file__).resolve().with_name("expenses.txt")


def load_expenses():
    expenses = []
    try:
        with EXPENSES_FILE.open("r", newline="") as f:
            for line_number, row in enumerate(csv.reader(f), start=1):
                if not row:
                    continue
                if len(row) != 3:
                    print(f"Skipping invalid expense on line {line_number}: expected category, amount, and date.")
                    continue
                try:
                    expenses.append(validate_expense(*row))
                except ValueError as e:
                    print(f"Skipping invalid expense on line {line_number}: {e}")
    except FileNotFoundError:
        return expenses
    except (OSError, csv.Error) as e:
        print(e)
    return expenses


def validate_expense(category, amount, expense_date):
    category = category.strip()
    if not category:
        raise ValueError("Category cannot be empty.")

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        raise ValueError("Amount must be a valid number.") from None
    if not math.isfinite(amount) or amount <= 0:
        raise ValueError("Amount must be a finite number greater than zero.")

    expense_date = expense_date.strip()
    try:
        parsed_date = date.fromisoformat(expense_date)
    except (AttributeError, ValueError):
        raise ValueError("Date must be a real date in YYYY-MM-DD format.") from None
    if parsed_date.isoformat() != expense_date:
        raise ValueError("Date must be a real date in YYYY-MM-DD format.")

    return {"category": category.capitalize(), "amount": amount, "date": expense_date}


def save_expenses(expenses):
    try:
        validated_expenses = [
            validate_expense(expense["category"], expense["amount"], expense["date"])
            for expense in expenses
        ]
        with EXPENSES_FILE.open("w", newline="") as f:
            writer = csv.writer(f)
            for expense in validated_expenses:
                writer.writerow([expense["category"], expense["amount"], expense["date"]])
    except (OSError, ValueError) as e:
        print(e)