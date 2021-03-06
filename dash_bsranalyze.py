from urllib.parse import quote_plus
import uuid
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
    select asinsource,domain,seedid,categoryname,currency,asin,crawl_date_bsr,rank rank_bsr
    from
    (
    SELECT 'competitor' asinsource,lower(case when seed.domain ='gb' then 'uk' else seed.domain end) domain,seed.id seedid,seed.name categoryname,seed.currency,info.asin,info.crawl_date crawl_date_bsr,info.rank FROM 
    (select * from `amz_bsr_info` where (bsr_seed_id,asin,crawl_date) in (select bsr_seed_id,asin,max(crawl_date) maxcrawldate from amz_bsr_info group by bsr_seed_id,asin) ) info
      left join  amz_bsr_seed seed on seed.id=info.bsr_seed_id
      ) aa
    group by asinsource,domain,seedid,categoryname,currency,asin,crawl_date_bsr,rank
      
    """, con = conn )
    df_comp_asins.sort_values(['seedid','crawl_date_bsr','rank_bsr'],inplace=True)
    df_own_asins=pd.read_sql(sql=f"""
    SELECT 'our' asinsource,lower(case when seed.domain ='gb' then 'uk' else seed.domain end) domain,seed.id seedid,seed.name categoryname,seed.currency,comp.own_asin asin,'' crawl_date_bsr,'' rank_bsr FROM 
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
         '????????????',
        tuple(set(df_categorys['domain'].to_list())))
    st.write('You selected:', countryoption)

    cateoption = st.radio(
         '????????????',
        tuple(set(df_categorys.loc[df_categorys['domain']==countryoption,:]['name'].to_list())))
    st.write('You selected:', cateoption)

bsrseedid=df_categorys.loc[(df_categorys['domain']==countryoption)&(df_categorys['name']==cateoption),:]['id'].values[0]
# print(bsrseedid)



df_own_asins_c=df_own_asins.loc[df_own_asins['seedid']==bsrseedid,:]
df_comp_asins_c=df_comp_asins.loc[df_comp_asins['seedid']==bsrseedid,:]

st.subheader('??????????????????')
col1,col2=st.columns(2)
# with col1:
#     ms3=st.multiselect('??????????????????asin',set(df_own_asins_c['asin'].to_list()),[])
#     # col1.write(ms)


cbxls = {}
expander_1=col1.expander('??????????????????asin')
for i, asin in enumerate(df_own_asins_c['asin'].to_list()):
    # print(df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['seedid']==bsrseedid),:]['imageUrl'].values[-1])
    if  pd.isna(df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['seedid']==bsrseedid),:]['imageUrl'].values[-1]) \
            or df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['seedid']==bsrseedid),:]['imageUrl'].values[-1]=='None':
        cbxls[asin] = expander_1.checkbox('??????asin', key=f'cbxlkey_{asin}_{str(i)}')
        expander_1.write({'SELLER':df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['seedid']==bsrseedid),:]['sellerName'].values[-1],
                         'asin':df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['seedid']==bsrseedid),:]['asin'].values[-1]})
    else:

        cbxls[asin] = expander_1.checkbox('??????asin', key=f'cbxlkey_{asin}_{str(i)}')
        expander_1.image(df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['seedid']==bsrseedid),:]['imageUrl'].values[-1], width=100,
                     )
        expander_1.write({'SELLER':df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['seedid']==bsrseedid),:]['sellerName'].values[-1],
                         'asin':df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['seedid']==bsrseedid),:]['asin'].values[-1]})
ms1=[]
for k,v in cbxls.items():
    if v==True:
        ms1.append(k)




# with col2:
#     ms2=st.multiselect('????????????asin',set(df_comp_asins_c['asin'].to_list()),[])
#     # col2.write(ms)


cbxrs = {}
datelist=list(set(df_comp_asins_c['crawl_date_bsr'].to_list()))
datelist.sort()
expander_2=col2.expander('??????????????????asin')
startdate,end_date=expander_2.select_slider(
    '??????bsr????????????',
    options=datelist,
    value=(datelist[-1],datelist[-1])
)
for i, asin in enumerate(df_comp_asins_c.loc[(df_comp_asins_c['crawl_date_bsr']>=startdate)&(df_comp_asins_c['crawl_date_bsr']<=end_date),:]['asin'].to_list()):
    # print(df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['seedid']==bsrseedid),:]['imageUrl'].values[-1])
    if  pd.isna(df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['seedid']==bsrseedid),:]['imageUrl'].values[-1]) \
            or df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['seedid']==bsrseedid),:]['imageUrl'].values[-1]=='None':
        cbxrs[asin] = expander_2.checkbox('??????asin', key=f'cbxrkey_{asin}_{str(i)}')
        expander_2.write({'SELLER':df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['seedid']==bsrseedid),:]['sellerName'].values[-1],
                         'asin':df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['seedid']==bsrseedid),:]['asin'].values[-1],
                         'crawl_date':df_jsinfo.loc[(df_jsinfo['asin'] == asin) & (df_jsinfo['seedid'] == bsrseedid), :]['crawl_date_bsr'].values[-1],
                         'rank':df_jsinfo.loc[(df_jsinfo['asin'] == asin) & (df_jsinfo['seedid'] == bsrseedid), :]['rank_bsr'].values[-1]},

        )
    else:

        cbxrs[asin] = expander_2.checkbox('??????asin', key=f'cbxrkey_{asin}_{str(i)}')
        expander_2.image(df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['seedid']==bsrseedid),:]['imageUrl'].values[-1], width=100,
                     )
        expander_2.write({'SELLER':df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['seedid']==bsrseedid),:]['sellerName'].values[-1],
                         'asin':df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['seedid']==bsrseedid),:]['asin'].values[-1],
                         'crawl_date':df_jsinfo.loc[(df_jsinfo['asin'] == asin) & (df_jsinfo['seedid'] == bsrseedid), :]['crawl_date_bsr'].values[-1],
                         'rank':df_jsinfo.loc[(df_jsinfo['asin'] == asin) & (df_jsinfo['seedid'] == bsrseedid), :]['rank_bsr'].values[-1]},


                         )
ms2=[]
for k,v in cbxrs.items():
    if v==True:
        ms2.append(k)









showasin=st.checkbox('?????????asin',True)
showavg=st.checkbox('????????????',True)
df_jsinfo_ms1=df_jsinfo.loc[(df_jsinfo['asin'].isin(ms1))&(df_jsinfo['domain']==countryoption.lower())&(df_jsinfo['asinsource']=='our')]
# print('>>>>>>>>>>>>>>>ms1df')
dfjsinfoms1_avg=df_jsinfo_ms1.groupby('crawl_date').agg({'price':'mean','rank':'mean','estimatedsales_daily':'mean'}).reset_index()
# print(dfjsinfoms1_avg)

df_jsinfo_ms2=df_jsinfo.loc[(df_jsinfo['asin'].isin(ms2))&(df_jsinfo['domain']==countryoption.lower())&(df_jsinfo['asinsource']=='competitor')]
# print('>>>>>>>>>>>>>>>ms2df')
dfjsinfoms2_avg=df_jsinfo_ms2.groupby('crawl_date').agg({'price':'mean','rank':'mean','estimatedsales_daily':'mean'}).reset_index()
# print(dfjsinfoms2_avg)

owncolors=['#fa8072','#ff73b3','#ff7f50','#ff8033','#e68ab8','#e9a867','#f3e1ae']
compcolors=['#c0c0c0','#5686bf','#5f9ea0','#2a52be','#73b839','#5c50e6','#0e6551']

pricetraces=[]
ranktraces=[]
salestraces=[]

for i,asin in enumerate(ms1):
    if showasin:
        pricetraces.append(
            go.Scatter(
                x=df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['domain']==countryoption.lower())]['crawl_date'],
                y=df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['domain']==countryoption.lower())]['price'],
                name='??????-'+asin,
                mode='lines',
                # line=('longdashdot'),
                line=dict(dash='solid',color=owncolors[i], width=3, ),
                # line=dict(color=colors[i], width=line_size[i]),
                connectgaps=True,
            ))
        ranktraces.append(
            go.Scatter(
                x=df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['domain']==countryoption.lower())]['crawl_date'],
                y=df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['domain']==countryoption.lower())]['rank'],
                name='??????-' + asin,
                mode='lines',
                line=dict(dash='solid',color=owncolors[i], width=3, ),

                # line=dict(color=colors[i], width=line_size[i]),
                connectgaps=True,
                # yaxis='y2'
            ))
        salestraces.append(
            go.Scatter(
                x=df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['domain']==countryoption.lower())]['crawl_date'],
                y=df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['domain']==countryoption.lower())]['estimatedsales_daily'],
                name='??????-' + asin,
                mode='lines',
                line=dict(dash='solid',color=owncolors[i], width=3, ),

                # line=dict(color=colors[i], width=line_size[i]),
                connectgaps=True,
            ))

for j,asin in enumerate(ms2):
    if showasin:
        pricetraces.append(
            go.Scatter(
                x=df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['domain']==countryoption.lower())]['crawl_date'],
                y=df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['domain']==countryoption.lower())]['price'],
                name='??????-'+asin,
                mode='lines',
                line=dict(dash='solid', color=compcolors[j],width=3, ),

                # line=dict(color=colors[i], width=line_size[i]),
                connectgaps=True,
            ))
        ranktraces.append(
            go.Scatter(
                x=df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['domain']==countryoption.lower())]['crawl_date'],
                y=df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['domain']==countryoption.lower())]['rank'],
                name='??????-' + asin,
                mode='lines',
                line=dict(dash='solid', color=compcolors[j], width=3, ),

                # line=dict(color=colors[i], width=line_size[i]),
                connectgaps=True,
                # yaxis='y2'

            ))
        salestraces.append(
            go.Scatter(
                x=df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['domain']==countryoption.lower())]['crawl_date'],
                y=df_jsinfo.loc[(df_jsinfo['asin']==asin)&(df_jsinfo['domain']==countryoption.lower())]['estimatedsales_daily'],
                name='??????-' + asin,
                mode='lines',
                line=dict(dash='solid', color=compcolors[j], width=3, ),

                # line=dict(color=colors[i], width=line_size[i]),
                connectgaps=True,
            ))


if showavg:
    if len(ms1)>1:
        pricetraces.append(
            go.Scatter(
                x=dfjsinfoms1_avg['crawl_date'],
                y=dfjsinfoms1_avg['price'],
                name='??????-????????????',
                mode='lines',
                # line=('longdashdot'),
                line=dict(dash='longdashdot',color='#cc0033', width=3, ),
                # line=dict(color=colors[i], width=line_size[i]),
                connectgaps=True,
            ))
    if len(ms2)>1:
        pricetraces.append(
            go.Scatter(
                x=dfjsinfoms2_avg['crawl_date'],
                y=dfjsinfoms2_avg['price'],
                name='??????-????????????',
                mode='lines',
                # line=('longdashdot'),
                line=dict(dash='longdashdot',color='#0000ff', width=3, ),
                # line=dict(color=colors[i], width=line_size[i]),
                connectgaps=True,
            ))
    if len(ms1)>1:
        ranktraces.append(
            go.Scatter(
                x=dfjsinfoms1_avg['crawl_date'],
                y=dfjsinfoms1_avg['rank'],
                name='??????-??????????????????',
                mode='lines',
                # line=('longdashdot'),
                line=dict(dash='longdashdot',color='#cc0033', width=3, ),
                # line=dict(color=colors[i], width=line_size[i]),
                connectgaps=True,
            ))
    if len(ms2) > 1:
        ranktraces.append(
            go.Scatter(
                x=dfjsinfoms2_avg['crawl_date'],
                y=dfjsinfoms2_avg['rank'],
                name='??????-??????????????????',
                mode='lines',
                # line=('longdashdot'),
                line=dict(dash='longdashdot',color='#0000ff', width=3, ),
                # line=dict(color=colors[i], width=line_size[i]),
                connectgaps=True,
            ))
    if len(ms1)>1:
        salestraces.append(
            go.Scatter(
                x=dfjsinfoms1_avg['crawl_date'],
                y=dfjsinfoms1_avg['estimatedsales_daily'],
                name='??????-??????????????????',
                mode='lines',
                # line=('longdashdot'),
                line=dict(dash='longdashdot',color='#cc0033', width=3, ),
                # line=dict(color=colors[i], width=line_size[i]),
                connectgaps=True,
            ))
    if len(ms2)>1:
        salestraces.append(
            go.Scatter(
                x=dfjsinfoms2_avg['crawl_date'],
                y=dfjsinfoms2_avg['estimatedsales_daily'],
                name='??????-??????????????????',
                mode='lines',
                # line=('longdashdot'),
                line=dict(dash='longdashdot',color='#0000ff', width=3, ),
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
#         title='??????',
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
#         title='??????',
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
# st.plotly_chart(rankfig)

salesfig=go.Figure(data=salestraces)
metric_figure = make_subplots(
    rows=3, cols=1,
    # specs=[[{}, {}],
    #        [{}, {}],
    #        [{'colspan': 2}, {}]]
# subplot_titles=tuple(['??????','??????','???????????????'])
)


for t in pricefig.data:
    metric_figure.append_trace(t, row=1, col=1)
for t in rankfig.data:
    metric_figure.append_trace(t, row=2, col=1)
for t in salesfig.data:
    metric_figure.append_trace(t, row=3, col=1)
# metric_figure["layout"]["xaxis"].update({"title": "trace0???x???", "titlefont": {"color": "red"}})
metric_figure["layout"]["yaxis"].update({"title": "??????"})
# metric_figure["layout"]["xaxis2"].update({"title": "trace1???x???", "titlefont": {"color": "green"}})
metric_figure["layout"]["yaxis2"].update({"title": "??????","autorange":"reversed"})
# metric_figure["layout"]["xaxis3"].update({"title": "trace2???x???", "titlefont": {"color": "pink"}})
metric_figure["layout"]["yaxis3"].update({"title": "????????????"})

st.plotly_chart(metric_figure, use_container_width=True)

#
# ############
# st.subheader('????????????3D?????????')
# df_jsinfo_size=df_jsinfo.loc[(df_jsinfo['seedid']==bsrseedid)&(df_jsinfo['domain']==countryoption.lower())&((df_jsinfo['dimensionUnit'] =='centimetres') |(df_jsinfo['dimensionUnit'] =='Zentimeter') ),:]
# fig1 = go.Figure(data=[
#      go.Scatter3d(x=df_jsinfo_size['length'], y=df_jsinfo_size['width'], z=df_jsinfo_size['height'],
#                   mode='markers',
#                   marker=dict(size=2)
#                  ),
#
#     ])
# st.plotly_chart(fig1, use_container_width=True)
#
# def getrangedf(df,granularity=20):
#     lmax=df['length'].max()
#     wmax=df['width'].max()
#     hmax=df['height'].max()
#     # print('lwh>>>>>')
#     # print(lmax,wmax,hmax)
#     # print(max([lmax,wmax,hmax]))
#     amax=max([lmax, wmax, hmax])
#     def get_inwhichrange(v):
#         rangenum=round(amax/granularity)
#         for i in range(0,rangenum):
#             if i*granularity<v<=(i+1)*granularity:
#                 return f'{str(i*granularity)}~{str((i+1)*granularity)}'
#     def get_inwhichrange_midv(v):
#         rangenum=round(amax/granularity)
#         for i in range(0,rangenum):
#             if i*granularity<v<=(i+1)*granularity:
#                 return (i*granularity+(i+1)*granularity)/2
#     def gettickvals():
#         rangenum=round(amax/granularity)
#         tvlist=[]
#         for i in range(0,rangenum):
#             tvlist.append(f'{str(i*granularity)}~{str((i+1)*granularity)}')
#         return tvlist
#     df['length_iwr']=df['length'].apply(lambda x:get_inwhichrange(x))
#     df['width_iwr']=df['width'].apply(lambda x:get_inwhichrange(x))
#     df['height_iwr']=df['height'].apply(lambda x:get_inwhichrange(x))
#     df['length_iwr_midv']=df['length'].apply(lambda x:get_inwhichrange_midv(x))
#     df['width_iwr_midv']=df['width'].apply(lambda x:get_inwhichrange_midv(x))
#     df['height_iwr_midv']=df['height'].apply(lambda x:get_inwhichrange_midv(x))
#     df=(df[['length','length_iwr','width','width_iwr','length_iwr_midv','width_iwr_midv','height_iwr_midv','height','height_iwr']])
#     df= df.groupby(['length_iwr','width_iwr','height_iwr','length_iwr_midv','width_iwr_midv','height_iwr_midv']).count().reset_index()
#     return df,gettickvals()
#
#
# df_sizerange,tvlist=getrangedf(df_jsinfo_size,20)
# print(tvlist)
# print(df_sizerange)
#
# ############
# st.subheader('????????????3D?????????')
# fig2 = go.Figure(data=[
#      go.Scatter3d(x=df_sizerange['length_iwr'], y=df_sizerange['width_iwr'], z=df_sizerange['height_iwr'],
#                   mode='markers',
#                   # marker=dict(size=2),
#
#                     marker = dict(
#                           size = 4,
#                           color = df_sizerange['length'], # set color to an array/list of desired values
#                           colorscale = 'Viridis'
#                           )
#
#                  ),
#     ])
# # fig2 = go.Figure(data=[
# #      go.Scatter3d(x=df_sizerange['length_iwr_midv'], y=df_sizerange['width_iwr_midv'], z=df_sizerange['height_iwr_midv'],
# #                   mode='markers',
# #                   # marker=dict(size=2),
# #
# #                     marker = dict(
# #                           size = 4,
# #                           color = df_sizerange['length'], # set color to an array/list of desired values
# #                           colorscale = 'Viridis'
# #                           )
# #
# #                  ),
# #     ])
# fig2.update_layout(
#     xaxis=dict(
# linecolor='red',
#         tickmode='array',
#         tickvals=tvlist+['fdfd'],
#         ticktext=tvlist+['fdfd','123','111','22','333','444','55','66'],
#
#     ),
#     yaxis=dict(
#
#         tickmode='array',
#         tickvals=tvlist + ['fdfd'],
#         ticktext=tvlist + ['fdfd'],
#     ),
#     # zaxis=dict(
#     #
#     #     tickmode='array',
#     #     tickvals=tvlist + ['fdfd'],
#     #     ticktext=tvlist + ['fdfd'],
#     # ),
# )
# st.plotly_chart(fig2, use_container_width=True)
