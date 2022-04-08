import numpy
import streamlit as st
import plotly.graph_objs as go
from dataexcute_salesrelate import *
st.title('商品关联分析')


dfo,dfcountry=getorigindf()
with st.sidebar:
    countryoption = st.selectbox(
         '请选择国家',
         tuple(dfcountry['country'].to_list()))
    st.write('You selected:', countryoption)
    isfilter_oneorder=st.checkbox('过滤只购买一种商品订单',True)
    isfilter_skupre=st.checkbox('过滤前部相同sku',True)
    abtogetimesfilter=st.slider('AB最低同时购买次数',1,20,1)
    afilter=st.slider('A最低购买次数',1,50,1)

    # spvalue_filter=st.slider('选择最低支持度',0.0000001,0.015,0.0000001)
    spfilter=st.text_input('输入最低支持度',value='0.0000001')
#
desc,basketsets_all,frequent_itemsets,basket,status=getbasketana(dfo,countryoption,isfilter_oneorder,spfilter,isfilter_skupre,abtogetimesfilter,afilter)
st.sidebar.write(desc)
# scatter = Scatter()
# scatter.add_xaxis(basket['support'])
# scatter.add_yaxis('',basket['confidence'])
#
# streamlit_echarts.st_pyecharts(
#     scatter,
#     theme=ThemeType.DARK
# )
# st.markdown('testtesttest')


############################
# antecedents1=basket.antecedents1 if basket is not None else []
# consiquencts1=basket.consequents1 if basket is not None else []
#
#
# valuesup = [[iindex, jindex,
#           0 if
#           basket.loc[(basket['antecedents1']==ivalue)&(basket['consequents1']==jvalue)]['support'].size==0
#           else
#           basket.loc[(basket['antecedents1']==ivalue)&(basket['consequents1']==jvalue)]['support'].values[0]
#
#           ] for iindex,ivalue in enumerate(antecedents1) for jindex,jvalue in enumerate(consiquencts1)]
# heatsupport=HeatMap()
# heatsupport.add_xaxis(antecedents1.to_list())
# heatsupport.add_yaxis('支持度',consiquencts1.to_list(),valuesup,
#                         is_selected= True,
#                       label_opts=opts.LabelOpts(is_show=False, position="inside"),)#basket.support1.to_list() if basket is not None else [])
# heatsupport.set_global_opts(
#     title_opts=opts.TitleOpts(title=""),
#     visualmap_opts=opts.VisualMapOpts(min_=0,max_=0.1),
#     axispointer_opts=opts.AxisPointerOpts(is_show=True)
# )
# streamlit_echarts.st_pyecharts(
#     heatsupport,
#     theme=ThemeType.DARK
# )
##############
st.subheader("支持度热力图")

supportheatfigure = {
    'data': [
        go.Heatmap(z=basket.support if basket is not None else [],
                   x=basket.antecedents1 if basket is not None else [],
                   y=basket.consequents1 if basket is not None else [],
                   customdata=numpy.transpose(numpy.array([basket["abtimes"], basket["atimes"], basket["alltimes"]])),
                   hovertemplate='a: %{x}'+'<br>'+'b: %{y}'+'<br>'+'支持度: %{z}'+'<br>'+'a、b同时购买次数: %{customdata[0]}'+'<br>'+'a购买次数: %{customdata[1]}'+'<br>'+'所有订单数: %{customdata[2]}',
                   colorscale='YlGnBu')],
    'layout': go.Layout(margin=dict(l=100, b=100, t=50),
                        xaxis={
                            'title': 'A',
                            'hoverformat': ''  # 如果想显示小数点后两位'.2f'，显示百分比'.2%'
                        },
                        yaxis={
                            'title':'B',
                            'hoverformat': ''  # 如果想显示小数点后两位'.2f'，显示百分比'.2%'
                        })
}
st.plotly_chart(supportheatfigure, use_container_width=True)
st.markdown('''
*「支持度」：A商品和B商品同时被购买的概率，显然支持度越大，商品间关联性越强。计算公式：同时购买A和B订单数 / 总购买订单数*

''')

#########################
# valueconf = [[iindex, jindex,
#           0 if
#           basket.loc[(basket['antecedents1']==ivalue)&(basket['consequents1']==jvalue)]['confidence'].size==0
#           else
#           basket.loc[(basket['antecedents1']==ivalue)&(basket['consequents1']==jvalue)]['confidence'].values[0]
#
#           ] for iindex,ivalue in enumerate(antecedents1) for jindex,jvalue in enumerate(consiquencts1)]
# heatconfidence=HeatMap()
# heatconfidence.add_xaxis(antecedents1.to_list())
# heatconfidence.add_yaxis('置信度',consiquencts1.to_list(),valueconf,
#                         is_selected= True,
#                       label_opts=opts.LabelOpts(is_show=False, position="inside"),)#basket.support1.to_list() if basket is not None else [])
# heatconfidence.set_global_opts(
#     title_opts=opts.TitleOpts(title=""),
#     visualmap_opts=opts.VisualMapOpts(min_=0,max_=1),
#     axispointer_opts=opts.AxisPointerOpts(is_show=True)
# )
# streamlit_echarts.st_pyecharts(
#     heatconfidence,
#     theme=ThemeType.DARK
# )

#############

st.subheader("置信度热力图")

confidenceheatfigure = {
    'data': [
        go.Heatmap(z=basket.confidence if basket is not None else [],
                   x=basket.antecedents1 if basket is not None else [],
                   y=basket.consequents1 if basket is not None else [],
                   customdata=numpy.transpose(numpy.array([basket["abtimes"], basket["atimes"], basket["alltimes"]])),
                   hovertemplate='a: %{x}' + '<br>' + 'b: %{y}' + '<br>' + '置信度: %{z}' + '<br>' + 'a、b同时购买次数: %{customdata[0]}' + '<br>' + 'a购买次数: %{customdata[1]}' + '<br>' + '所有订单数: %{customdata[2]}',

                   colorscale='YlGnBu')],
    'layout': go.Layout(margin=dict(l=100, b=100, t=50),
                        xaxis={
                            'title': 'A',
                            'hoverformat': ''  # 如果想显示小数点后两位'.2f'，显示百分比'.2%'
                        },
                        yaxis={
                            'title':'B',
                            'hoverformat': ''  # 如果想显示小数点后两位'.2f'，显示百分比'.2%'
                        })}

st.plotly_chart(confidenceheatfigure, use_container_width=True)

st.markdown('''
*「置信度」：因为购买了A所以购买了B的概率，注意与支持度区分。计算公式：同时购买A和B订单数 / 购买A的订单数*
''')



#############
# valuelift = [[iindex, jindex,
#           0 if
#           basket.loc[(basket['antecedents1']==ivalue)&(basket['consequents1']==jvalue)]['lift'].size==0
#           else
#           basket.loc[(basket['antecedents1']==ivalue)&(basket['consequents1']==jvalue)]['lift'].values[0]
#
#           ] for iindex,ivalue in enumerate(antecedents1) for jindex,jvalue in enumerate(consiquencts1)]
# heatlift=HeatMap()
# heatlift.add_xaxis(antecedents1.to_list())
# heatlift.add_yaxis('提升度',consiquencts1.to_list(),valuelift,
#                         is_selected= True,
#                       label_opts=opts.LabelOpts(is_show=False, position="inside"),)#basket.support1.to_list() if basket is not None else [])
# heatlift.set_global_opts(
#     title_opts=opts.TitleOpts(title=""),
#     visualmap_opts=opts.VisualMapOpts(min_=0,max_=20),
#     axispointer_opts=opts.AxisPointerOpts(is_show=True)
# )
# streamlit_echarts.st_pyecharts(
#     heatlift,
#     theme=ThemeType.DARK
# )

#############
st.subheader("提升度热力图")

liftheatfigure = {
    'data': [
        go.Heatmap(z=basket.lift if basket is not None else [],
                   x=basket.antecedents1 if basket is not None else [],
                   y=basket.consequents1 if basket is not None else [],
                   customdata=numpy.transpose(numpy.array([basket["abtimes"], basket["atimes"], basket["alltimes"]])),
                   hovertemplate='a: %{x}' + '<br>' + 'b: %{y}' + '<br>' + '提升度: %{z}' + '<br>' + 'a、b同时购买次数: %{customdata[0]}' + '<br>' + 'a购买次数: %{customdata[1]}' + '<br>' + '所有订单数: %{customdata[2]}',

                   colorscale='YlGnBu')],
    'layout': go.Layout(margin=dict(l=100, b=100, t=50),
                        xaxis={
                            'title': 'A',
                            'hoverformat': ''  # 如果想显示小数点后两位'.2f'，显示百分比'.2%'
                        },
                        yaxis={
                            'title':'B',
                            'hoverformat': ''  # 如果想显示小数点后两位'.2f'，显示百分比'.2%'
                        })}


st.plotly_chart(liftheatfigure, use_container_width=True)
st.markdown('''
*「提升度」：先购买A对购买B的提升作用，用来判断商品组合方式是否具有实际价值，大于1说明该组合方式有效，小于1则说明无效甚至反效果 公式：“包含A的事务中同时包含B事务的比例”与“包含B事务的比例”的比值*
''')


################散点图
figure_scatter = {
    'data': [go.Scatter(
        x=basket.support if basket is not None else [],
        y=basket.confidence if basket is not None else [],
        text=basket.skus if basket is not None else [],
        name="",
        mode="markers")],
    'layout': go.Layout(
        xaxis={
            'title': '支持度',
            'hoverformat': ''  # 如果想显示小数点后两位'.2f'，显示百分比'.2%'
        },
        yaxis={
            'title':'置信度',
            'hoverformat': ''  # 如果想显示小数点后两位'.2f'，显示百分比'.2%'
        }
    )
}
st.subheader("支持度-置信度散点图")
st.plotly_chart(figure_scatter, use_container_width=True)

######
st.subheader('购物篮分析数据')
if type(basket) !=type(None):
    basket.drop('antecedents', axis=1, inplace=True)
    basket.drop('consequents', axis=1, inplace=True)

st.write(basket)

def convert_df(df):
 # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')
if type(basket) !=type(None):

    basketcsv = convert_df(basket)
    st.download_button('下载数据',basketcsv)
#pareto
st.subheader('销售额帕累托图')

dfpareto=getpareto_amount(dfo,countryoption,'','')
# bar_pareto=Bar()
#
# bar_pareto.add_xaxis(xaxis_data=dfpareto['sku'].to_list())
#
# # 使用add_yaxis函数，设置图例名称参数series_name为"扣分"，传入scoreList作为y轴数据
# bar_pareto.add_yaxis(
#     series_name="salesamount",
#     y_axis=dfpareto['amount'].to_list()
# )
# streamlit_echarts.st_pyecharts(
#     bar_pareto,
#     theme=ThemeType.DARK
# )
#################
paretoamountfigure = {
    'data': [
        go.Bar(
            x=dfpareto['sku'],
            y=dfpareto['amount'],

        ),
        go.Line(
            x=dfpareto['sku'],
            y=dfpareto['amount_leiji'],
            yaxis='y2'
        )],
    'layout': go.Layout(margin=dict(l=100, b=100, t=50),
                        yaxis=dict(
                            title='销售额'
                        ),
                        yaxis2=dict(
                            title='累计百分比',
                            overlaying='y',
                            side='right'
                        ))
}

st.plotly_chart(paretoamountfigure, use_container_width=True)

st.markdown('''
*世界上80%的资源被20%的人消耗了；美国20%的人垄断了全国80%的财富；一个企业20%的资源投入产生了80%的效益...其实这些现象的背后都存在着一个定理——二八法则（20/80定理）。所谓的二八法则就是说，在任何群体当中，较少的重要因子带来了绝大多数的影响，较多的不重要因子带来了很小的影响.帕累托图的核心思想就是少数项目贡献了大部分价值。以款式和销售量为例：A 款式数量占总体 10% ，却贡献了 80% 的销售额*
''')

