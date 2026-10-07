import streamlit as st
import pandas as pd

st.title("SECURITISATION")

try:
    if "securitisation" == "executive":
        st.write("Executive Summary")
        loans = pd.read_csv('data/raw/loans.csv')
        st.metric("Total Loans", f"{len(loans):,}")
        st.metric("Total Principal", f"")
    elif "securitisation" == "credit_risk":
        pd_preds = pd.read_csv('data/outputs/pd_predictions.csv')
        st.write("Average PD:", pd_preds['pd_estimate'].mean())
        st.line_chart(pd_preds['pd_estimate'].head(100))
    elif "securitisation" == "securitisation":
        pools = pd.read_csv('data/outputs/pool_risk_output.csv')
        st.dataframe(pools)
    elif "securitisation" == "waterfall":
        waterfall = pd.read_csv('data/outputs/waterfall_output.csv')
        st.bar_chart(waterfall.set_index('tranche_name')['allocated_cash'])
    elif "securitisation" == "stress_testing":
        stress = pd.read_csv('data/outputs/stress_test_pivot.csv')
        st.dataframe(stress)
    elif "securitisation" == "risk_arena":
        st.subheader("Interactive Risk Arena")
        st.write("Choose your pool and tranche strategy.")
        capital = st.slider("Initial Capital", 1000, 100000)
        pools = pd.read_csv('data/outputs/pool_risk_output.csv')
        selected_pool = st.selectbox("Select Pool to Invest", pools['pool_id'])
        score = capital / 1000
        st.write(f"Your calculated score: {score}")
    elif "securitisation" == "crisis_lab":
        st.subheader("Simulate 2008 Subprime Crisis")
        st.button("Trigger Housing Crash")
    else:
        st.write("Module coming soon.")
except Exception as e:
    st.error(f"Data not fully generated yet. Run the pipeline first. Error: {e}")
