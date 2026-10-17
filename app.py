import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="WILDCARD | Risk Detection", page_icon="🔎", layout="wide")

SAMPLE = pd.DataFrame([
    {"event_id":"E001","transaction_amount":120,"failed_attempts":0,"unusual_activity":0},
    {"event_id":"E002","transaction_amount":250,"failed_attempts":1,"unusual_activity":0},
    {"event_id":"E003","transaction_amount":9800,"failed_attempts":0,"unusual_activity":1},
    {"event_id":"E004","transaction_amount":95,"failed_attempts":4,"unusual_activity":1},
    {"event_id":"E005","transaction_amount":420,"failed_attempts":0,"unusual_activity":0},
    {"event_id":"E006","transaction_amount":14500,"failed_attempts":3,"unusual_activity":1},
    {"event_id":"E007","transaction_amount":60,"failed_attempts":0,"unusual_activity":0},
    {"event_id":"E008","transaction_amount":1750,"failed_attempts":2,"unusual_activity":0},
    {"event_id":"E009","transaction_amount":7200,"failed_attempts":5,"unusual_activity":1},
    {"event_id":"E010","transaction_amount":340,"failed_attempts":0,"unusual_activity":0},
    {"event_id":"E011","transaction_amount":11200,"failed_attempts":2,"unusual_activity":1},
    {"event_id":"E012","transaction_amount":180,"failed_attempts":1,"unusual_activity":0},
    {"event_id":"E013","transaction_amount":530,"failed_attempts":0,"unusual_activity":0},
    {"event_id":"E014","transaction_amount":6400,"failed_attempts":3,"unusual_activity":0},
    {"event_id":"E015","transaction_amount":75,"failed_attempts":0,"unusual_activity":0},
    {"event_id":"E016","transaction_amount":2800,"failed_attempts":1,"unusual_activity":1},
    {"event_id":"E017","transaction_amount":9300,"failed_attempts":4,"unusual_activity":1},
    {"event_id":"E018","transaction_amount":210,"failed_attempts":0,"unusual_activity":0},
    {"event_id":"E019","transaction_amount":5800,"failed_attempts":3,"unusual_activity":1},
    {"event_id":"E020","transaction_amount":150,"failed_attempts":0,"unusual_activity":0},
])

def analyze(frame):
    df = frame.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    aliases = {"amount":"transaction_amount", "failed_login_attempts":"failed_attempts",
               "failed_logins":"failed_attempts", "unusual":"unusual_activity"}
    for old, new in aliases.items():
        if old in df.columns and new not in df.columns:
            df.rename(columns={old:new}, inplace=True)
    if "event_id" not in df.columns:
        df.insert(0, "event_id", [f"E{i:03d}" for i in range(1, len(df)+1)])
    for col, default in {"transaction_amount":0, "failed_attempts":0, "unusual_activity":0}.items():
        if col not in df.columns:
            df[col] = default
        if col == "unusual_activity":
            df[col] = df[col].astype(str).str.lower().map(
                {"true":1,"yes":1,"y":1,"1":1,"false":0,"no":0,"n":0,"0":0}
            ).fillna(pd.to_numeric(df[col], errors="coerce")).fillna(0)
        else:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(default).clip(lower=0)
    df["unusual_activity"] = (pd.to_numeric(df["unusual_activity"], errors="coerce").fillna(0) > 0).astype(int)
    amount_threshold = max(float(df["transaction_amount"].quantile(.90)), 5000)
    df["risk_score"] = (
        (df["transaction_amount"] >= amount_threshold).astype(int) * 2
        + (df["failed_attempts"] >= 3).astype(int) * 2
        + (df["unusual_activity"] == 1).astype(int) * 2
    )
    df["risk_level"] = df["risk_score"].map(lambda n: "High Risk" if n >= 4 else ("Medium Risk" if n >= 2 else "Low Risk"))
    def explain(row):
        reasons = []
        if row["failed_attempts"] >= 3: reasons.append("Repeated failed attempts")
        if row["transaction_amount"] >= amount_threshold: reasons.append("High amount compared with this dataset")
        if row["unusual_activity"] == 1: reasons.append("Unusual activity flag present")
        return "; ".join(reasons) if reasons else "No demonstration rule triggered"
    df["warning"] = df.apply(explain, axis=1)
    df["recommended_action"] = df["risk_level"].map({
        "High Risk":"Prioritize human review and verify the record",
        "Medium Risk":"Review the flagged signals",
        "Low Risk":"Continue routine monitoring"
    })
    return df

st.sidebar.title("🔎 WILDCARD")
st.sidebar.caption("Risk Detection System")
page = st.sidebar.radio("Navigation", ["Dashboard", "Risk Analysis", "Early Warnings", "Download Report"])
st.sidebar.divider()
st.sidebar.caption("Prototype Version 1.0")

st.title("WILDCARD: BEYOND THE OBVIOUS")
st.subheader("AI-Powered Intelligent Risk Detection")
st.write("Discover hidden patterns • Detect unusual activity • Act early")
st.info("Prototype notice: default data is synthetic. The current scoring uses demonstration rules; labels are not proof of fraud or validated predictions.")

uploaded = st.file_uploader("Upload a CSV file (optional)", type=["csv"])
st.caption("Suggested columns: event_id, transaction_amount, failed_attempts, unusual_activity.")
try:
    if uploaded is not None:
        raw = pd.read_csv(uploaded)
        if raw.empty:
            st.error("The uploaded CSV is empty.")
            st.stop()
        source = uploaded.name
    else:
        raw = SAMPLE.copy()
        source = "Built-in sample data"
    df = analyze(raw)
except Exception as err:
    st.error(f"Could not read or analyze this CSV: {err}")
    st.stop()

st.caption(f"Data source: {source}")
high = int((df.risk_level == "High Risk").sum())
medium = int((df.risk_level == "Medium Risk").sum())
low = int((df.risk_level == "Low Risk").sum())

if page == "Dashboard":
    st.markdown("### 📊 Risk Detection Dashboard")
    a,b,c,d = st.columns(4)
    a.metric("Records analyzed", len(df))
    b.metric("🔴 High risk", high)
    c.metric("🟠 Medium risk", medium)
    d.metric("🟢 Low risk", low)
    left,right = st.columns(2)
    with left:
        dist = df["risk_level"].value_counts().reindex(["High Risk","Medium Risk","Low Risk"], fill_value=0).rename_axis("Risk level").reset_index(name="Records")
        st.plotly_chart(px.bar(dist, x="Risk level", y="Records", color="Risk level"), use_container_width=True)
    with right:
        st.plotly_chart(px.histogram(df, x="transaction_amount", nbins=12, title="Transaction amount distribution"), use_container_width=True)
    st.dataframe(df.head(10), use_container_width=True, hide_index=True)
elif page == "Risk Analysis":
    st.markdown("### 🔎 Detailed Risk Analysis")
    levels = st.multiselect("Filter by risk level", ["High Risk","Medium Risk","Low Risk"], default=["High Risk","Medium Risk","Low Risk"])
    filtered = df[df["risk_level"].isin(levels)]
    st.caption(f"Showing {len(filtered)} of {len(df)} records")
    st.dataframe(filtered, use_container_width=True, hide_index=True)
elif page == "Early Warnings":
    st.markdown("### ⚠️ Early Warnings")
    warnings = df[df.risk_level != "Low Risk"].sort_values(["risk_score","transaction_amount"], ascending=False)
    if warnings.empty:
        st.success("No records were flagged by the demonstration rules.")
    for _, row in warnings.iterrows():
        with st.container(border=True):
            st.markdown(f"**{row['event_id']} · {row['risk_level']} · Score {row['risk_score']}**")
            st.write(row["warning"])
            st.caption(f"Suggested action: {row['recommended_action']}")
    st.caption("Warnings are demonstration signals and require human review.")
else:
    st.markdown("### 📥 Download Analysis Report")
    st.write("Review the results, then download the analysis as a CSV.")
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button("⬇️ Download risk analysis report (CSV)", df.to_csv(index=False).encode("utf-8-sig"),
                       "wildcard_risk_analysis_report.csv", "text/csv", use_container_width=True)

st.divider()
st.caption("WILDCARD prototype · Demonstration rules only · Human review required")
