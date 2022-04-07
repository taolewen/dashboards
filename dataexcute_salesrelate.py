import os
from datetime import timedelta, datetime, date
from urllib.parse import quote_plus

import pandas as pd
import streamlit as st
import sqlalchemy as sa
from mlxtend.frequent_patterns import apriori, association_rules
from numpy import NaN
from pandas import DateOffset, NaT

# import dbs

# from dbs import nsconn
filepath=os.getcwd()+'\\files\\'

@st.cache(allow_output_mutation=True)
def getorigindf():
    # connstr = f"mysql+pymysql://{st.secrets['mysql']['user']}:{quote_plus(st.secrets['mysql']['password'])}@{st.secrets['mysql']['host']}:3306/{st.secrets['mysql']['database']}?charset=utf8"
    # print(connstr)
    connstr = "mysql+pymysql://onlyreader:%s@124.71.174.53:3306/crawl_data?charset=utf8" % quote_plus('csbd@123')

    engine = sa.create_engine(connstr)
    conn = engine.connect()

    sqlo = 'select * from ns_ordercountrymailamount'
    dfo = pd.read_sql(sqlo, con = conn )

    sqlcountry="""select id,custrecord_hc_country_area area,name country from ns_customrecord_hc_list_country"""
    dfcountry = pd.read_sql(sqlcountry, con = conn )

    dfo=pd.merge(dfo,dfcountry,left_on=['countryid'],right_on=['id'],how='left')

    return dfo,dfcountry

def getpareto_amount(origindf,country,startdate,enddate):
    df_c= origindf.loc[(origindf['country']==country)&(origindf['qty']!=0)&(origindf['qty'] is not None), :]
    df_a=df_c.groupby(['sku'])['amount'].sum().reset_index()

    df_a.sort_values('amount', ascending=False, inplace=True)
    df_a['amount_leiji'] = df_a.amount.cumsum() / df_a.amount.sum()

    print(df_a)
    return df_a


def getbasketana(origindf,country):
    df_c= origindf.loc[(origindf['country']==country)&(origindf['qty']!=0)&(origindf['qty'] is not None), :]
    # basket = (df_c
    #           .groupby(['orderid', 'sku'])['qty']
    #           .sum().unstack().reset_index().fillna(0)
    #           .set_index('orderid'))
    # print(f'num of orders>>>{str(len(list(set(basket.index.to_list()))))}')

    basket = (df_c
              .groupby(['email', 'sku'])['qty']
              .sum().unstack().reset_index().fillna(0)
              .set_index('email'))
    print(f'num of email>>>{str(len(list(set(basket.index.to_list()))))}')

    def encode_units(x):
        if x <= 0:
            return 0
        if x >= 1:
            return 1

    basket_sets = basket.applymap(encode_units)
    basket_sets['sumo']=basket_sets.sum(axis=1)
    basket_sets=basket_sets.loc[basket_sets['sumo']!=1,:]
    basket_sets.drop('sumo', axis=1, inplace=True)
    # basket_sets.to_csv(filepath+'basket_sets.csv')

    frequent_itemsets = apriori(basket_sets, min_support=0.015,use_colnames=True)
    if frequent_itemsets.empty:
        return None,'无支持度超过阈值数据 1'
    # frequent_itemsets.to_csv(filepath+'frequent_itemsets.csv')
    rules = association_rules(frequent_itemsets, metric="support", min_threshold=0)
    print('calculate finish')
    if rules.empty:
        return None,'无支持度超过阈值数据 2'
    # rules.to_csv(filepath+'rules.csv')
    rules['support1']=rules.apply(lambda x:round(x.support*1000,5),axis=1)

    rules['antecedents1']=rules.apply(lambda x:str(list(x.antecedents)),axis=1)
    rules['consequents1']=rules.apply(lambda x:str(list(x.consequents)),axis=1)

    rules['skus']=rules.apply(lambda x:str(list(x.antecedents))+"-"+str(list(x.consequents)),axis=1)
    rules.head()

    return rules,''