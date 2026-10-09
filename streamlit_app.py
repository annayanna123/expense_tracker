import logging
from datetime import date

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError
from supabase import create_client

from auth_ui import render_authentication
from expense_data import insert_database_expense, load_database_expenses

logger = logging.getLogger(__name__)

st.set_page_config(page_title="Expense Tracker", page_icon="💸", layout="wide")
st.markdown(
	"<style>"
	"@import url(https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,600&display=swap);"
	":root { --ink: #20312d; --muted: #687873; --paper: #f5f7f4; --surface: #fff; --line: #dce5df; --green: #28715a; --green-dark: #1e5947; }"
	"[data-testid=stAppViewContainer] { background: var(--paper); color: var(--ink); }"
	"[data-testid=stHeader] { background: rgba(245, 247, 244, .94); }"
	".block-container { max-width: 1120px; padding-top: 2.2rem; padding-bottom: 3rem; }"
	"h1, h2, h3, p, label, button, input { font-family: DM Sans, sans-serif; }"
	"h1 { color: var(--ink); font-weight: 600; }"
	".app-masthead { display: flex; align-items: center; gap: 14px; margin: 0 0 2.2rem; }"
	".brand-mark { display: grid; place-items: center; width: 44px; height: 44px; border-radius: 12px; background: var(--green); color: white; font: 600 22px Fraunces, serif; }"
	".eyebrow { color: var(--green); font: 700 11px DM Sans, sans-serif; letter-spacing: 1.4px; text-transform: uppercase; }"
	".app-name { margin: 1px 0 0; color: var(--ink); font: 600 28px Fraunces, serif; }"
	".section-title { margin: 1.6rem 0 .7rem; color: var(--ink); font: 600 20px DM Sans, sans-serif; }"
	"[data-testid=stMetric] { padding: 16px 18px; border: 1px solid var(--line); border-bottom: 3px solid var(--green); border-radius: 8px; background: var(--surface); }"
	"[data-testid=stMetricLabel] { color: var(--muted); }"
	"[data-testid=stMetricValue] { color: var(--ink); font-family: DM Sans, sans-serif; font-weight: 700; }"
	"[data-testid=stForm] { padding: 18px 20px 10px; border: 1px solid var(--line); border-radius: 8px; background: var(--surface); }"
	"[data-testid=stTextInput] input, [data-testid=stNumberInput] input, [data-testid=stDateInput] input { border-color: var(--line); border-radius: 6px; }"
	"button[kind=primary] { border: 0; border-radius: 6px; background: var(--green); color: white; font-weight: 600; }"
	"button[kind=primary]:hover { background: var(--green-dark); color: white; }"
	"[data-testid=stTabs] [role=tab] { color: var(--muted); }"
	"[data-testid=stTabs] [aria-selected=true] { color: var(--green); }"
	"[data-testid=stDataFrame] { border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }"
	"[data-testid=stSidebar] { background: #edf2ee; }"
	"</style>"
	'<div class="app-masthead"><div class="brand-mark">E</div><div><div class="eyebrow">PERSONAL FINANCE</div><div class="app-name">Expense tracker</div></div></div>',
	unsafe_allow_html=True,
)


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

user_id = st.session_state.get("auth_user_id")
if user_id is None:
	account_tab, expenses_tab = st.tabs(["Account", "Expenses"])
else:
	expenses_tab, account_tab = st.tabs(["Expenses", "Account"])

with account_tab:
	if user_id is None:
		user_id = render_authentication(supabase)
	else:
		st.markdown('<div class="section-title">Your account</div>', unsafe_allow_html=True)
		st.write(st.session_state.get("auth_username") or "Expense tracker member")
		st.caption(st.session_state.get("auth_email", ""))
		if st.button("Log out", key="logout"):
			try:
				supabase.auth.sign_out()
			finally:
				st.session_state.pop("auth_user_id", None)
				st.session_state.pop("auth_username", None)
				st.session_state.pop("auth_email", None)
				st.session_state.pop("supabase_client", None)
				st.rerun()

with expenses_tab:
	if user_id is None:
		st.info("Log in or create an account in the Account tab to view and add expenses.")
	else:
		st.markdown('<div class="eyebrow">YOUR OVERVIEW</div>', unsafe_allow_html=True)
		st.markdown('<div class="section-title">Add an expense</div>', unsafe_allow_html=True)
		with st.form("add_expense"):
			category_column, amount_column, date_column, submit_column = st.columns([2, 1.2, 1.5, 1])
			category = category_column.text_input("Category", placeholder="e.g. Groceries")
			amount = amount_column.number_input("Amount (Php)", min_value=0.01, value=0.01, step=1.0)
			expense_date = date_column.date_input("Date", value=date.today())
			submitted = submit_column.form_submit_button("Add expense", type="primary")

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
			month_prefix = date.today().strftime("%Y-%m")
			month_total = sum(
				expense["amount"] for expense in expenses
				if str(expense["date"]).startswith(month_prefix)
			)
			st.markdown('<div class="section-title">At a glance</div>', unsafe_allow_html=True)
			metric_month, metric_total, metric_count = st.columns(3)
			metric_month.metric("This month", f"Php {month_total:,.2f}")
			metric_total.metric("All time", f"Php {total:,.2f}")
			metric_count.metric("Expenses", f"{len(expenses):,}")

			st.markdown('<div class="section-title">Recent expenses</div>', unsafe_allow_html=True)
			categories = sorted({expense["category"] for expense in expenses})
			selected_category = st.selectbox("Filter by category", ["All categories", *categories])
			visible_expenses = expenses
			if selected_category != "All categories":
				visible_expenses = [expense for expense in expenses if expense["category"] == selected_category]
			display_rows = [
				{"Date": expense["date"], "Category": expense["category"], "Amount": expense["amount"]}
				for expense in visible_expenses
			]
			st.dataframe(
				display_rows,
				hide_index=True,
				width="stretch",
				column_config={"Amount": st.column_config.NumberColumn("Amount", format="Php %.2f")},
			)
		else:
			st.markdown('<div class="section-title">At a glance</div>', unsafe_allow_html=True)
			st.metric("Expenses", "0")
			st.markdown('<div class="section-title">Recent expenses</div>', unsafe_allow_html=True)
			st.info("No expenses yet. Add your first expense above.")
