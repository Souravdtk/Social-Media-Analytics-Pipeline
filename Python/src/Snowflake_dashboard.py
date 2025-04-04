import os
import streamlit as st
import snowflake.connector
import pandas as pd
import configparser

# Load Configuration
config_file = 'config.ini'
dir_path = os.path.abspath(os.path.dirname(__file__))
config_path = os.path.abspath(os.path.join(dir_path, '..', 'config', config_file))

config = configparser.ConfigParser()
config.read(config_path)

# Connect to Snowflake
conn = snowflake.connector.connect(
    user=config.get('SNOWFLAKE_CONN', 'user'),
    password=config.get('SNOWFLAKE_CONN', 'pass'),
    account=config.get('SNOWFLAKE_CONN', 'account')
)

cur = conn.cursor()

# Fetch column names dynamically
cur.execute('''
    SELECT COLUMN_NAME 
    FROM SnowDemo.information_schema.columns 
    WHERE table_schema = upper('Snow1') 
    AND table_name = 'CUSTOMER';
''')
columns = [col[0] for col in cur.fetchall()]

# Fetch data
cur.execute("SELECT * FROM SnowDemo.Snow1.Customer;")
data = cur.fetchall()

# Close cursor & connection
cur.close()
conn.close()

# Convert to DataFrame
df = pd.DataFrame(data, columns=columns)

# Streamlit UI
st.set_page_config(page_title="Snowflake Dashboard", layout="wide")

st.markdown(
    """
    <style>
    .big-font { font-size:20px !important; font-weight: bold; }
    .metric-box { 
        padding: 10px; 
        border-radius: 10px; 
        background-color: #f4f4f4; 
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True
)

# Header
st.title("📊 Snowflake Customer Dashboard")
st.subheader("Real-time Customer Insights from Snowflake")

# Sidebar Filters
st.sidebar.header("🔍 Filters")
company_filter = st.sidebar.text_input("Search by Company Name", "")
name_filter = st.sidebar.text_input("Search by Customer Name", "")

# Apply filters
filtered_df = df.copy()
if company_filter:
    filtered_df = filtered_df[filtered_df["COMPANY"].str.contains(company_filter, case=False, na=False)]
if name_filter:
    filtered_df = filtered_df[
        filtered_df["FIRST_NAME"].str.contains(name_filter, case=False, na=False) |
        filtered_df["LAST_NAME"].str.contains(name_filter, case=False, na=False)
    ]

# Display Key Metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
    st.metric("Total Customers", len(df))
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    unique_companies = df["COMPANY"].nunique()
    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
    st.metric("Unique Companies", unique_companies)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
    st.metric("Total Records", len(filtered_df))
    st.markdown('</div>', unsafe_allow_html=True)

# Display Filtered Data
st.subheader("📋 Customer Details")
st.dataframe(filtered_df, height=400)

# Visualization: Customer Distribution by Company
st.subheader("🏢 Customer Count by Company")
company_counts = df["COMPANY"].value_counts().reset_index()
company_counts.columns = ["Company", "Customer Count"]

st.bar_chart(company_counts.set_index("Company"))

# Footer
st.markdown("---")
st.caption("🔹 Built with Streamlit | Data from Snowflake")

