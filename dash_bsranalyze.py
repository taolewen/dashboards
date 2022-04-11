from urllib.parse import quote_plus

import streamlit as st
import pandas as pd
import numpy as np
from pyecharts.charts import Scatter, HeatMap, Bar
from pyecharts.faker import Faker
from pyecharts.globals import ThemeType
import streamlit_echarts
import random
import plotly.graph_objs as go
import sqlalchemy as sa
from plotly.subplots import make_subplots

from pyecharts import options as opts

@st.cache(allow_output_mutation=True)
def getorigindf():
    # connstr = f"mysql+pymysql://{st.secrets['mysql']['user']}:{quote_plus(st.secrets['mysql']['password'])}@{st.secrets['mysql']['host']}:3306/{st.secrets['mysql']['database']}?charset=utf8"
    # print(connstr)
    connstr = "mysql+pymysql://onlyreader:%s@124.71.174.53:3306/crawl_data?charset=utf8" % quote_plus('csbd@123')

    engine = sa.create_engine(connstr)
    conn = engine.connect()

    # sqlo = 'select * from ns_ordercountrymailamount'
    # dfo = pd.read_sql(sqlo, con = conn )

    df_categorys = pd.read_sql('select * from amz_bsr_seed', con = conn )
    df_comp_asins=pd.read_sql(sql=f"""
    SELECT 'competitor' asinsource,lower(case when seed.domain ='gb' then 'uk' else seed.domain end) domain,seed.id seedid,seed.name categoryname,seed.currency,info.asin FROM 
    (select * from `amz_bsr_info` ) info
      left join  amz_bsr_seed seed on seed.id=info.bsr_seed_id
    """, con = conn )
    df_own_asins=pd.read_sql(sql=f"""
    SELECT 'our' asinsource,lower(case when seed.domain ='gb' then 'uk' else seed.domain end) domain,seed.id seedid,seed.name categoryname,seed.currency,comp.own_asin asin FROM 
    (select * from `kp_competitor` ) comp
     left join  amz_bsr_seed seed on seed.id=comp.bsr_seed_id
    """, con = conn )
    df_jsinfo=pd.read_sql('select * from js_product_info', con = conn )
    #
    df_concatowncomp=pd.concat([df_comp_asins,df_own_asins])
    df_jsinfo=pd.merge(df_concatowncomp,df_jsinfo,on=['domain','asin'],how='left')





    return df_categorys,df_comp_asins,df_own_asins,df_jsinfo
df_categorys,df_comp_asins,df_own_asins,df_jsinfo=getorigindf()
df_categorys['domain']=df_categorys['domain'].apply(lambda x:x if x!='GB' else 'UK')
df_jsinfo['estimatedsales_daily']=df_jsinfo['estimatedSales'].apply(lambda x:x/30)
df_jsinfo.sort_values(['domain','asin','crawl_date'],inplace=True)
with st.sidebar:

    countryoption = st.selectbox(
         '选择国家',
        tuple(set(df_categorys['domain'].to_list())))
    st.write('You selected:', countryoption)

    cateoption = st.radio(
         '选择品类',
        tuple(set(df_categorys.loc[df_categorys['domain']==countryoption,:]['name'].to_list())))
    st.write('You selected:', cateoption)

bsrseedid=df_categorys.loc[(df_categorys['domain']==countryoption)&(df_categorys['name']==cateoption),:]['id'].values[0]
# print(bsrseedid)



df_own_asins_c=df_own_asins.loc[df_own_asins['seedid']==bsrseedid,:]
df_comp_asins_c=df_comp_asins.loc[df_comp_asins['seedid']==bsrseedid,:]

st.subheader('竞对价格曲线')

col1,col2=st.columns(2)
with col1:
    ms1=st.multiselect('选择自有产品asin',set(df_own_asins_c['asin'].to_list()),[])
    # col1.write(ms)
    showprice=st.checkbox('显示价格',True)
    showrank=st.checkbox('显示排名',True)
    showsalesqty=st.checkbox('显示预估日销',True)
with col2:
    ms2=st.multiselect('选择竞对asin',set(df_comp_asins_c['asin'].to_list()),[])
    # col2.write(ms)

owncolors=['#fa8072','#ff73b3','#ff7f50','#ff8033','#e68ab8','#e9a867','#f3e1ae']
compcolors=['#c0c0c0','#5686bf','#5f9ea0','#2a52be','#73b839','#5c50e6','#0e6551']

pricetraces=[]
ranktraces=[]
salestraces=[]
for i,asin in enumerate(ms1):
    if showprice:
        pricetraces.append(
            go.Scatter(
                x=df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['domain']==countryoption.lower())]['crawl_date'],
                y=df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['domain']==countryoption.lower())]['price'],
                name='价格-'+asin,
                mode='lines',
                # line=('longdashdot'),
                line=dict(dash='longdashdot',color=owncolors[i], width=3, ),
                # line=dict(color=colors[i], width=line_size[i]),
                connectgaps=True,
            ))
    if showrank:
        ranktraces.append(
            go.Scatter(
                x=df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['domain']==countryoption.lower())]['crawl_date'],
                y=df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['domain']==countryoption.lower())]['rank'],
                name='排名-' + asin,
                mode='lines',
                line=dict(dash='longdash',color=owncolors[i], width=3, ),

                # line=dict(color=colors[i], width=line_size[i]),
                connectgaps=True,
                # yaxis='y2'
            ))
    if showsalesqty:
        salestraces.append(
            go.Scatter(
                x=df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['domain']==countryoption.lower())]['crawl_date'],
                y=df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['domain']==countryoption.lower())]['estimatedsales_daily'],
                name='销量-' + asin,
                mode='lines',
                line=dict(dash='solid',color=owncolors[i], width=3, ),

                # line=dict(color=colors[i], width=line_size[i]),
                connectgaps=True,
            ))
for j,asin in enumerate(ms2):
    if showprice:
        pricetraces.append(
            go.Scatter(
                x=df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['domain']==countryoption.lower())]['crawl_date'],
                y=df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['domain']==countryoption.lower())]['price'],
                name='价格-'+asin,
                mode='lines',
                line=dict(dash='longdashdot', color=compcolors[j],width=3, ),

                # line=dict(color=colors[i], width=line_size[i]),
                connectgaps=True,
            ))
    if showrank:
        ranktraces.append(
            go.Scatter(
                x=df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['domain']==countryoption.lower())]['crawl_date'],
                y=df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['domain']==countryoption.lower())]['rank'],
                name='排名-' + asin,
                mode='lines',
                line=dict(dash='longdash', color=compcolors[j], width=3, ),

                # line=dict(color=colors[i], width=line_size[i]),
                connectgaps=True,
                # yaxis='y2'

            ))
    if showsalesqty:
        salestraces.append(
            go.Scatter(
                x=df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['domain']==countryoption.lower())]['crawl_date'],
                y=df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['domain']==countryoption.lower())]['estimatedsales_daily'],
                name='销量-' + asin,
                mode='lines',
                line=dict(dash='solid', color=compcolors[j], width=3, ),

                # line=dict(color=colors[i], width=line_size[i]),
                connectgaps=True,
            ))
# layout = go.Layout(
#     xaxis=dict(
#         showline=True,
#         showgrid=False,
#         showticklabels=True,
#         linecolor='rgb(204, 204, 204)',
#         linewidth=2,
#         title='日期',
#         # autotick=False,
#         ticks='outside',
#         tickcolor='rgb(204, 204, 204)',
#         tickwidth=2,
#         ticklen=5,
#         tickfont=dict(
#             family='Arial',
#             size=12,
#             color='rgb(82, 82, 82)',
#         ),
#     ),
#     yaxis=dict(
#         showgrid=False,
#         zeroline=False,
#         showline=True,
#         showticklabels=True,
#     ),
#     yaxis2=dict(
#         title='排名',
#         side='right',
#         anchor='x',
#         overlaying='y',
#         showline = True,
#         showticklabels = True,
#         autorange='reversed'
#     ),
#     autosize=False,
#     margin=dict(
#         autoexpand=False,
#         l=100,
#         r=20,
#         t=110,
#     ),
#     showlegend=False,
# )
# fig = go.Figure(data=traces, layout=layout)
pricefig=go.Figure(data=pricetraces)
rankfig=go.Figure(data=ranktraces)
salesfig=go.Figure(data=salestraces)
metric_figure = make_subplots(
    rows=3, cols=1,
    # specs=[[{}, {}],
    #        [{}, {}],
    #        [{'colspan': 2}, {}]]
)
for t in pricefig.data:
    metric_figure.append_trace(t, row=1, col=1)
for t in rankfig.data:
    metric_figure.append_trace(t, row=2, col=1)
for t in salesfig.data:
    metric_figure.append_trace(t, row=3, col=1)

st.plotly_chart(metric_figure, use_container_width=True)


############
st.subheader('尺寸分布3D散点图')
df_jsinfo_size=df_jsinfo.loc[(df_jsinfo['seedid']==bsrseedid)&(df_jsinfo['domain']==countryoption.lower())&((df_jsinfo['dimensionUnit'] =='centimetres') |(df_jsinfo['dimensionUnit'] =='Zentimeter') ),:]
fig1 = go.Figure(data=[
     go.Scatter3d(x=df_jsinfo_size['length'], y=df_jsinfo_size['width'], z=df_jsinfo_size['height'],
                  mode='markers',
                  marker=dict(size=2)
                 ),

    ])
st.plotly_chart(fig1, use_container_width=True)
