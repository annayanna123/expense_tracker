import streamlit as st

from expense_data import load_expenses

st.set_page_config(page_title="Expense Tracker", page_icon="💸")
st.title("Expense Tracker")

expenses = load_expenses()
if expenses:
	total = sum(expense["amount"] for expense in expenses)
	st.metric("Total expenses", f"Php {total:,.2f}")
	st.dataframe(expenses, hide_index=True, use_container_width=True)
else:
	st.info("No valid expenses to display.")
