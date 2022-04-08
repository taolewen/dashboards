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


def getbasketana(origindf,country,isfilter,sp_filter,isfilter_skupreword,abtogetimesfilter,afilter):
    desc={}
    df_c= origindf.loc[(origindf['country']==country)&(origindf['qty']!=0)&(origindf['qty'] is not None), :]
    basket = (df_c
              .groupby(['orderid', 'sku'])['qty']
              .sum().unstack().reset_index().fillna(0)
              .set_index('orderid'))
    print(f'num of orders>>>{str(len(list(set(basket.index.to_list()))))}')
    # basket = (df_c
    #           .groupby(['email', 'sku'])['qty']
    #           .sum().unstack().reset_index().fillna(0)
    #           .set_index('email'))
    # print(f'num of email>>>{str(len(list(set(basket.index.to_list()))))}')

    def encode_units(x):
        if x <= 0:
            return 0
        if x >= 1:
            return 1

    basket_sets = basket.applymap(encode_units)
    basket_sets['sumo']=basket_sets.sum(axis=1)
    basket_sets.to_csv(filepath+'basket_sets0.csv')

    basketsets_all=basket_sets
    desc['总订单数']=len(basketsets_all.index)
    orders=desc['总订单数']
    if isfilter:
        basket_sets=basket_sets.loc[basket_sets['sumo']!=1,:]
        desc['过滤只买一件物品订单数']=len(basket_sets.index)
        orders=desc['过滤只买一件物品订单数']

    basket_sets.drop('sumo', axis=1, inplace=True)
    # basket_sets.to_csv(filepath+'basket_sets1.csv')
    print('sp过滤>>>>>>>>>>>>'+str(sp_filter))
    sp_filter_float=float(sp_filter)
    print('sp过滤>>>>>>>>>>>>'+str(sp_filter_float))

    frequent_itemsets = apriori(basket_sets, min_support=sp_filter_float,use_colnames=True)#0.015#0.0000001
    if frequent_itemsets.empty:
        return None,None,None,None,'无支持度超过阈值数据 1'
    # frequent_itemsets.to_csv(filepath+'frequent_itemsets.csv')
    rules = association_rules(frequent_itemsets, metric="support", min_threshold=0)
    print('calculate finish')
    if rules.empty:
        return None,None,None,None,'无支持度超过阈值数据 2'
    rules['support1']=rules.apply(lambda x:round(x.support*1000,5),axis=1)

    rules['antecedentsskunum']=rules.apply(lambda x:len(list(x.antecedents)),axis=1)
    rules['consequentsskunum']=rules.apply(lambda x:len(list(x.consequents)),axis=1)
    #获取a和b sku都为1的
    rules=rules.loc[(rules['antecedentsskunum']==1)&(rules['consequentsskunum']==1),:]
    rules['antecedents1']=rules.apply(lambda x:str(list(x.antecedents)[0]),axis=1)
    rules['consequents1']=rules.apply(lambda x:str(list(x.consequents)[0]),axis=1)
    def getorderabtimes_nf(asku,bsku):
        abtimes=len(basket_sets.loc[(basket_sets[asku]!=0)&(basket_sets[bsku]!=0),:].index)
        return abtimes
    def getorderatimes_nf(asku):
        atimes=len(basket_sets.loc[(basket_sets[asku]!=0),:].index)
        return atimes
    def getorderabtimes_f(asku,bsku):
        abtimes=len(basket_sets.loc[(basket_sets[asku]!=0)&(basket_sets[bsku]!=0),:].index)
        return abtimes
    def getorderatimes_f(asku):
        atimes=len(basket_sets.loc[(basket_sets[asku]!=0),:].index)
        return atimes
    if isfilter:
        rules['abtimes']=rules.apply(lambda x:getorderabtimes_f(x.antecedents1,x.consequents1),axis=1)
        rules['atimes']=rules['antecedents1'].apply(lambda x:getorderatimes_f(x))
    else:
        rules['abtimes']=rules.apply(lambda x:getorderabtimes_nf(x.antecedents1,x.consequents1),axis=1)
        rules['atimes']=rules['antecedents1'].apply(lambda x:getorderatimes_nf(x))
    rules['alltimes']=orders
    #过滤sku - 前一样的
    if isfilter_skupreword:

        rules['antecedents_pre']= rules.apply(lambda x:(list(x.antecedents)[0]).split('-')[0],axis=1)
        rules['consequents_pre']= rules.apply(lambda x:(list(x.consequents)[0]).split('-')[0],axis=1)
        rules=rules.loc[rules['antecedents_pre']!=rules['consequents_pre']]
    rules['skus']=rules.apply(lambda x:str(list(x.antecedents))+"-"+str(list(x.consequents)),axis=1)
    rules.to_csv(filepath+'rules.csv')

    # rules.head()
    rules=rules.loc[(rules['abtimes']>=abtogetimesfilter)&(rules['atimes']>=afilter),:]



    return desc,basketsets_all,frequent_itemsets,rules,''