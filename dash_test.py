
import plotly.graph_objs as go



fig = go.Figure()

line_dash = ['solid', 'dot', 'dash', 'longdash', 'dashdot', 'longdashdot']
for i, d in enumerate(line_dash):
    fig.add_trace(
        go.Scatter(
            x=[0, 10], y=[i, i], mode='lines', 
            line=dict(dash=d, width=3,),
            showlegend=False
    ))


fig.update_layout(
    width=600, height=500,
    yaxis=dict(
        type='category',
        tickvals=list(range(len(line_dash))),
        ticktext=line_dash,
        showgrid=False
    ),
    xaxis_showticklabels=False,
    xaxis_showgrid=False,
)

# fig.write_image('../pic/lines_1.png', scale=10)
fig.show()
