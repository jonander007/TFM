import json, sys
sys.path.insert(0, "pylib")
import plotly.graph_objects as go
res = json.load(open("/home/user/TFM/datos/ahp/resultados_ahp.json"))
model = json.load(open("/home/user/TFM/datos/ahp/TFM_KP-FHR_final.smt"))
rt = model["Alternative Rating"]["Rating Table"]
COL = {"Decommissioning & Waste": "rgb(127,201,127)", "Fuel Cycle Characteristics": "rgb(190,174,212)",
       "Licensing Status": "rgb(253,192,134)", "Maritime Operational Challenges": "rgb(56,108,176)",
       "Political Considerations": "rgb(240,2,127)", "Reactor Core Characteristics": "rgb(191,91,22)",
       "Reactor System Characteristics": "rgb(102,102,102)"}
SHAPES = ["/", "\\", "|", "+", "x", "."]
tree = model["Criteria"]["Criteria"]["Selection of SMR for maritime propulsion"]["children"]
alts = sorted(res["puntuaciones"], key=lambda a: -res["puntuaciones"][a])
fig = go.Figure()
for node in tree:
    (crit, d), = node.items()
    for k, sub in enumerate(d["children"]):
        g = res["subcriterios"][sub]["global"]
        y = [g * res["intensidades"][sub][rt[a][sub]] for a in alts]
        fig.add_bar(x=alts, y=y, name="<b>%s</b>" % sub, legendgroup=crit, legendgrouptitle_text="<b>%s</b>" % crit,
                    marker=dict(color=COL[crit], opacity=0.75, line=dict(color="white", width=0.5),
                                pattern=dict(shape=SHAPES[k], fgcolor="black", fgopacity=0.5, solidity=0.15)))
tot = [res["puntuaciones"][a] for a in alts]
fig.add_scatter(x=alts, y=[t + 0.008 for t in tot], text=["%.3f" % t for t in tot], mode="text",
                textposition="top center", showlegend=False, textfont=dict(size=15, color="rgb(42,63,95)"), texttemplate="<b>%{text}</b>")
fig.update_layout(barmode="stack", width=1400, height=823, template="plotly_white",
                  title=dict(text="<b>Alternative Ranking</b>", x=0.5, font=dict(size=20)),
                  font=dict(family="Courier New", size=13, color="rgb(42,63,95)"),
                  xaxis=dict(title="<b>Alternatives</b>", tickangle=-30, showline=True, linecolor="rgb(42,63,95)"),
                  yaxis=dict(title="<b>Scores</b>", showline=True, linecolor="rgb(42,63,95)", range=[0, 0.68]),
                  legend=dict(groupclick="toggleitem", tracegroupgap=8, traceorder="grouped"), margin=dict(l=70, r=20, t=70, b=90))
fig.update_xaxes(tickfont=dict(size=14)); fig.update_layout(xaxis_ticktext=["<b>%s</b>" % a for a in alts], xaxis_tickvals=alts)
fig.write_html("fig_final.html", include_plotlyjs=True, full_html=True, config={"displayModeBar": False})
fig.write_image if False else None
