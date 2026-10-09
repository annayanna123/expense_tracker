import logging

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError
from supabase import create_client

from expense_data import insert_database_expense, load_database_expenses

logger = logging.getLogger(__name__)

st.set_page_config(page_title="Expense Tracker", page_icon="💸")
st.title("Expense Tracker")


@st.cache_resource
def get_supabase_client(url, key):
	return create_client(url, key)


try:
	supabase = get_supabase_client(
		st.secrets["SUPABASE_URL"],
		st.secrets["SUPABASE_KEY"],
	)
except (KeyError, StreamlitSecretNotFoundError):
	supabase = None
	st.error("Supabase secrets are not configured. Add SUPABASE_URL and SUPABASE_KEY to continue.")
	st.stop()


with st.form("add_expense"):
	category = st.text_input("Category")
	amount = st.number_input("Amount (Php)", min_value=0.01, value=0.01, step=1.0)
	expense_date = st.date_input("Date")
	submitted = st.form_submit_button("Add expense")

if submitted:
	try:
		insert_database_expense(supabase, category, amount, expense_date.isoformat())
		st.success("Expense added.")
		st.rerun()
	except ValueError as error:
		st.error(f"Invalid expense: {error}")
	except Exception:
		logger.exception("Supabase expense insert failed")
		st.error("Could not save the expense. Check your database connection and table permissions.")

try:
	expenses = load_database_expenses(supabase)
except Exception:
	logger.exception("Supabase expense query failed")
	st.error("Could not load expenses. Check your database connection and table permissions.")
	st.stop()

if expenses:
	total = sum(expense["amount"] for expense in expenses)
	st.metric("Total expenses", f"Php {total:,.2f}")
	st.dataframe(expenses, hide_index=True, width="stretch")
else:
	st.info("No expenses to display.")
