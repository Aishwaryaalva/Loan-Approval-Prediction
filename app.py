import streamlit as st
import pandas as pd
import pickle
import sqlite3
import bcrypt

# -------------------- CONFIG --------------------
st.set_page_config(page_title="Bank Loan System", layout="wide")

# -------------------- DATABASE --------------------
def create_user_table():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users(username TEXT, password BLOB)''')
    conn.commit()
    conn.close()

def add_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    c.execute("INSERT INTO users VALUES (?, ?)", (username, hashed))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    data = c.fetchone()
    conn.close()

    if data:
        return bcrypt.checkpw(password.encode(), data[0])
    return False

create_user_table()

# -------------------- LOAD MODEL --------------------
model = pickle.load(open('loan_pipeline.pkl', 'rb'))

# -------------------- SESSION --------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# -------------------- UI STYLE --------------------
st.markdown("""
<style>
.main { background-color: #0f172a; }
.stButton>button {
    background-color: #2563eb;
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
}
.card {
    background-color: #1e293b;
    padding: 20px;
    border-radius: 15px;
}
</style>
""", unsafe_allow_html=True)

# -------------------- SIDEBAR --------------------
menu = st.sidebar.selectbox("Menu", ["Login", "Signup"])

# -------------------- SIGNUP --------------------
if menu == "Signup":
    st.title("📝 Create Account")

    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type="password")

    if st.button("Signup"):
        add_user(new_user, new_pass)
        st.success("Account Created Successfully")

# -------------------- LOGIN --------------------
elif menu == "Login":
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if login_user(username, password):
            st.session_state.logged_in = True
            st.success("Login Successful")
        else:
            st.error("Invalid Credentials")

# -------------------- DASHBOARD --------------------
if st.session_state.logged_in:

    st.title("🏦 Loan Approval Dashboard")

    col1, col2 = st.columns(2)

    # LEFT SIDE
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        age = st.number_input("Age", 18, 100)
        gender = st.selectbox("Gender", ["Male", "Female"])
        marital = st.selectbox("Marital Status", ["Single", "Married"])
        dependents = st.selectbox("Dependents", ["0", "1", "2", "3+"])
        employment = st.selectbox("Employment Status",
                                 ["Employed", "Unemployed", "Self-employed"])

        st.markdown("</div>", unsafe_allow_html=True)

    # RIGHT SIDE
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        income = st.number_input("Annual Income")
        credit_score = st.number_input("Credit Score")
        loan_amount = st.number_input("Loan Amount")
        loan_term = st.number_input("Loan Term (Months)")
        interest_rate = st.number_input("Interest Rate")
        dti = st.number_input("Debt to Income Ratio")

        st.markdown("</div>", unsafe_allow_html=True)

    # EXTRA
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    collateral = st.selectbox("Has Collateral", ["Yes", "No"])
    existing_loans = st.number_input("Existing Loans")
    purpose = st.selectbox("Loan Purpose",
                           ["Home", "Car", "Education", "Business"])
    missed = st.number_input("Missed Payments Last Year")
    channel = st.selectbox("Application Channel",
                           ["Online", "Branch"])
    coapplicant = st.selectbox("Co-Applicant", ["Yes", "No"])

    st.markdown("</div>", unsafe_allow_html=True)

    # -------------------- PREDICTION --------------------
    if st.button("Check Loan Status"):

      input_data = pd.DataFrame([{
        "Age": age,
        "Gender": gender,
        "Marital_Status": marital,
        "Dependents": dependents,
        "Employment_Status": employment,
        "Annual_Income": income,
        "Credit_Score": credit_score,
        "Loan_Amount": loan_amount,
        "Loan_Term_Months": loan_term,
        "Interest_Rate": interest_rate,
        "Debt_to_Income_Ratio": dti,
        "Has_Collateral": collateral,
        "Existing_Loans": existing_loans,
        "Loan_Purpose": purpose,
        "Missed_Payments_Last_Year": missed,
        "Loan_Application_Channel": channel,
        "Co-Applicant": coapplicant
       }])

    # RULE FIRST (IMPORTANT)
    if income == 0:
        st.error("❌ Loan Not Approved (Income cannot be zero)")

    else:
        # ML prediction only if income valid
        prob = model.predict_proba(input_data)[0][1]

        st.write(f"Approval Probability: {prob*100:.2f}%")

        if prob > 0.6:
            st.success("✅ Loan Approved")
        else:
            st.error("❌ Loan Not Approved")