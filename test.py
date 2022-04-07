# # streamlit_app.py
#
from urllib.parse import quote_plus

import pandas as pd
import streamlit as st
import sqlalchemy as sa

# import mysql.connector
#
# # Initialize connection.
# # Uses st.experimental_singleton to only run once.
# @st.experimental_singleton
# def init_connection():
#     return mysql.connector.connect(**st.secrets["mysql"])
#
# conn = init_connection()
#
# # Perform query.
# # Uses st.experimental_memo to only rerun when the query changes or after 10 min.
# @st.experimental_memo(ttl=600)
# def run_query(query):
#
#     with conn.cursor() as cur:
#         cur.execute(query)
#         return cur.fetchall(),cur.description
#
#
# title,rows = run_query("SELECT * from asin_seed limit 10;")
# print(title)
# print(rows)
#
# # Print results.
# for row in rows:
#     st.write(f"{row[0]} has a :{row[1]}:")

@st.cache(allow_output_mutation=True)
def load_data():
    connstr = "mysql+pymysql://developer:%s@124.71.174.53:3306/crawl_data?charset=utf8" % quote_plus('csbd@123')

    engine = sa.create_engine(connstr)
    conn = engine.connect()
    sql = 'select * from asin_seed limit 10'
    df = pd.read_sql(sql, con = conn )
    return df

st.write(load_data())