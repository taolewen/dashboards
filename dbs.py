import pymysql as pymysql
# import pyodbc
import streamlit as st



mysqlconn = pymysql.connect(host=st.secrets["mysql"]['host'],
                             user=st.secrets["mysql"]['user'],
                             password=st.secrets["mysql"]['password'],
                             db=st.secrets["mysql"]['database'])

