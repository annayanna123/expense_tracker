import streamlit as st


def render_authentication(client):
	st.subheader("Account")
	login_tab, signup_tab = st.tabs(["Log in", "Sign up"])

	with login_tab:
		with st.form("login_form"):
			email = st.text_input("Email", key="login_email")
			password = st.text_input("Password", type="password", key="login_password")
			submitted = st.form_submit_button("Log in", type="primary")
		if submitted:
			try:
				response = client.auth.sign_in_with_password({
					"email": email.strip(),
					"password": password,
				})
				if response.user is None or response.session is None:
					st.error("Login did not return an authenticated session.")
				else:
					st.session_state["auth_user_id"] = str(response.user.id)
					st.session_state["auth_email"] = response.user.email or email.strip()
					st.rerun()
			except Exception:
				st.error("Could not log in. Check the email and password, then try again.")

	with signup_tab:
		with st.form("signup_form"):
			username = st.text_input("Username", key="signup_username")
			email = st.text_input("Email", key="signup_email")
			password = st.text_input("Password", type="password", key="signup_password")
			confirm_password = st.text_input(
				"Confirm password", type="password", key="signup_confirm_password"
			)
			submitted = st.form_submit_button("Create account", type="primary")
		if submitted:
			if not username.strip() or not email.strip() or not password:
				st.error("Enter a username, email address, and password.")
			elif len(password) < 8:
				st.error("Use a password with at least 8 characters.")
			elif password != confirm_password:
				st.error("The passwords do not match.")
			else:
				try:
					response = client.auth.sign_up({
						"email": email.strip(),
						"password": password,
						"options": {"data": {"username": username.strip()}},
					})
					if response.session is not None and response.user is not None:
						st.session_state["auth_user_id"] = str(response.user.id)
						st.session_state["auth_email"] = response.user.email or email.strip()
						st.rerun()
					st.success("Account created. Check your email to confirm it, then log in.")
				except Exception:
					st.error("Could not create the account. Check the email and Supabase Auth settings.")

	return st.session_state.get("auth_user_id")