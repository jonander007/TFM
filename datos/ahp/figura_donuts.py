"""Figura de la memoria (AHP) con el estilo de SMART (Plotly). Lee resultados_ahp.json y TFM_KP-FHR_final_v2.smt
y escribe un HTML; la imagen se obtiene haciendo captura del gráfico a 2x."""
import json, sys
sys.path.insert(0, "pylib")  # plotly 5.24 (pip install plotly)
import plotly.graph_objects as go
from plotly.subplots import make_subplots
res = json.load(open("/home/user/TFM/datos/ahp/resultados_ahp.json"))
model = json.load(open("/home/user/TFM/datos/ahp/TFM_KP-FHR_final_v2.smt"))
rt = model["Alternative Rating"]["Rating Table"]
COL = {"Decommissioning & Waste": "127, 201, 127", "Fuel Cycle Characteristics": "190, 174, 212",
       "Licensing Status": "253, 192, 134", "Maritime Operational Challenges": "56, 108, 176",
       "Political Considerations": "240, 2, 127", "Reactor Core Characteristics": "191, 91, 22",
       "Reactor System Characteristics": "102, 102, 102"}
SHAPES = ["/", "\\", "|", "+", "x", "."]
tree = model["Criteria"]["Criteria"]["Selection of SMR for maritime propulsion"]["children"]
subs, cols, shapes = [], [], []
for node in tree:
    (crit, d), = node.items()
    for k, s in enumerate(d["children"]):
        subs.append(s); cols.append("rgba(%s, 0.75)" % COL[crit]); shapes.append(SHAPES[k])
alts = sorted(res["puntuaciones"], key=lambda a: -res["puntuaciones"][a])
fig = make_subplots(rows=2, cols=2, specs=[[{"type": "domain"}] * 2] * 2,
                    subplot_titles=["<b>%s</b>" % a for a in alts], vertical_spacing=0.16, horizontal_spacing=0.08)
for i, a in enumerate(alts):
    v = [res["subcriterios"][s]["global"] * res["intensidades"][s][rt[a][s]] for s in subs]
    tot = sum(v)
    txt = ["%.1f%%" % (100 * x / tot) if x / tot >= 0.04 else "" for x in v]
    fig.add_trace(go.Pie(labels=subs, values=v, hole=0.3, text=txt, textinfo="text", textposition="outside",
                         sort=False, direction="clockwise", rotation=0,
                         textfont=dict(family="Courier New", size=13, color="rgb(42,63,95)"),
                         title=dict(text="<b>%.2f</b>" % tot, font=dict(family="Courier New", size=17)),
                         marker=dict(colors=cols, line=dict(color="white", width=0.5),
                                     pattern=dict(shape=shapes, fgcolor="black", fillmode="overlay", size=12, solidity=0.15)),
                         showlegend=False), row=i // 2 + 1, col=i % 2 + 1)
fig.update_layout(width=1300, height=1250, template="plotly_white", margin=dict(l=40, r=40, t=110, b=40),
                  font=dict(family="Courier New", size=16, color="rgb(42,63,95)"))
fig.update_annotations(font=dict(family="Courier New", size=20, color="rgb(42,63,95)"), yshift=28)
fig.write_html("donuts.html", include_plotlyjs=True, full_html=True, config={"displayModeBar": False})
