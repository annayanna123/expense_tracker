import logging

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError
from supabase import create_client

from auth_ui import render_authentication
from expense_data import insert_database_expense, load_database_expenses

logger = logging.getLogger(__name__)

st.set_page_config(page_title="Expense Tracker", page_icon="💸")
st.title("Expense Tracker")


try:
	if "supabase_client" not in st.session_state:
		st.session_state["supabase_client"] = create_client(
			st.secrets["SUPABASE_URL"],
			st.secrets["SUPABASE_KEY"],
		)
	supabase = st.session_state["supabase_client"]
except (KeyError, StreamlitSecretNotFoundError):
	supabase = None
	st.error("Supabase secrets are not configured. Add SUPABASE_URL and SUPABASE_KEY to continue.")
	st.stop()

user_id = render_authentication(supabase)
if user_id is None:
	st.stop()

st.sidebar.write(f"Signed in as {st.session_state.get('auth_email', '')}")
if st.sidebar.button("Log out"):
	try:
		supabase.auth.sign_out()
	finally:
		st.session_state.pop("auth_user_id", None)
		st.session_state.pop("auth_email", None)
		st.session_state.pop("supabase_client", None)
		st.rerun()


with st.form("add_expense"):
	category = st.text_input("Category")
	amount = st.number_input("Amount (Php)", min_value=0.01, value=0.01, step=1.0)
	expense_date = st.date_input("Date")
	submitted = st.form_submit_button("Add expense")

if submitted:
	try:
		insert_database_expense(supabase, user_id, category, amount, expense_date.isoformat())
		st.success("Expense added.")
		st.rerun()
	except ValueError as error:
		st.error(f"Invalid expense: {error}")
	except Exception:
		logger.exception("Supabase expense insert failed")
		st.error("Could not save the expense. Check your database connection and table permissions.")

try:
	expenses = load_database_expenses(supabase, user_id)
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
