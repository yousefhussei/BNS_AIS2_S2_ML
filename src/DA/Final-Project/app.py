"""
Ford GoBike (February 2019) dashboard built with Dash.

Run:
    pip install dash pandas plotly
    python app.py
Then open http://127.0.0.1:8050

Put fordgobike_cleaned.csv in the same folder as this file.
"""
import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html

# ------------------------------------------------------------------ data
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fordgobike_cleaned.csv")
df = pd.read_csv(DATA_PATH)
df["age_group"] = pd.cut(
    df["age"], bins=[17, 25, 35, 45, 55, 100], labels=["18-25", "26-35", "36-45", "46-55", "56+"]
)

AGE_MIN, AGE_MAX = int(df["age"].min()), int(df["age"].max())

# ------------------------------------------------------------------ style
INK = "#12263A"
MUTED = "#5B6B7A"
BG = "#EEF2F5"
PANEL = "#FFFFFF"
LINE = "#D8E0E7"
COLORS = {
    "Subscriber": "#1F6F8B",
    "Customer": "#F2A541",
    "Male": "#1F6F8B",
    "Female": "#E4572E",
    "Other": "#8A9BA8",
}
FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"

PANEL_STYLE = {
    "background": PANEL,
    "border": f"1px solid {LINE}",
    "borderRadius": "6px",
    "padding": "8px",
}


def style_fig(fig, title, height=340):
    fig.update_layout(
        title=dict(text=title, x=0.01, font=dict(size=15, color=INK)),
        template="plotly_white",
        height=height,
        margin=dict(l=48, r=16, t=48, b=44),
        font=dict(family=FONT, color=INK),
        legend=dict(orientation="h", y=-0.22, x=0),
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
    )
    return fig


def empty_fig(title):
    fig = go.Figure()
    fig.add_annotation(
        text="No trips match these filters. Widen a filter to see data.",
        showarrow=False, font=dict(size=13, color=MUTED),
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return style_fig(fig, title)


# ------------------------------------------------------------------ layout
def control(label, component):
    return html.Div(
        [html.Label(label, style={"fontSize": "13px", "color": MUTED, "marginBottom": "6px", "display": "block"}), component],
        style={"flex": "1", "minWidth": "200px"},
    )


def kpi(id_, label):
    return html.Div(
        [
            html.Div(id=id_, style={"fontSize": "28px", "fontWeight": 650, "color": INK}),
            html.Div(label, style={"fontSize": "13px", "color": MUTED, "marginTop": "2px"}),
        ],
        style={**PANEL_STYLE, "flex": "1", "minWidth": "150px", "padding": "14px 16px"},
    )


def graph(id_, span=1):
    return html.Div(
        dcc.Graph(id=id_, config={"displaylogo": False}),
        style={**PANEL_STYLE, "gridColumn": f"span {span}"},
    )


app = Dash(__name__, title="Ford GoBike, February 2019")

app.layout = html.Div(
    style={"background": BG, "minHeight": "100vh", "fontFamily": FONT, "color": INK, "padding": "24px"},
    children=[
        html.Div(
            style={"maxWidth": "1300px", "margin": "0 auto"},
            children=[
                html.H1("Who rides Ford GoBike, and for how long?",
                        style={"fontSize": "30px", "margin": "0 0 4px", "fontWeight": 700}),
                html.P("San Francisco Bay Area bike share, February 2019. Use the filters to slice every chart.",
                       style={"margin": "0 0 20px", "color": MUTED, "fontSize": "15px"}),

                # ---- filters
                html.Div(
                    style={**PANEL_STYLE, "display": "flex", "gap": "24px", "flexWrap": "wrap", "padding": "16px", "marginBottom": "16px"},
                    children=[
                        control("User type", dcc.Checklist(
                            id="f-user", options=sorted(df["user_type"].unique()),
                            value=sorted(df["user_type"].unique()), inline=True,
                            inputStyle={"marginRight": "6px"}, labelStyle={"marginRight": "16px"})),
                        control("Gender", dcc.Checklist(
                            id="f-gender", options=["Male", "Female", "Other"],
                            value=["Male", "Female", "Other"], inline=True,
                            inputStyle={"marginRight": "6px"}, labelStyle={"marginRight": "16px"})),
                        control("Bike Share for All member", dcc.RadioItems(
                            id="f-bsfa", options=[{"label": "All", "value": "All"},
                                                  {"label": "Yes", "value": "Yes"},
                                                  {"label": "No", "value": "No"}],
                            value="All", inline=True,
                            inputStyle={"marginRight": "6px"}, labelStyle={"marginRight": "16px"})),
                        control("Age range", dcc.RangeSlider(
                            id="f-age", min=AGE_MIN, max=AGE_MAX, step=1, value=[AGE_MIN, AGE_MAX],
                            marks={a: str(a) for a in range(20, AGE_MAX + 1, 10)},
                            tooltip={"placement": "bottom", "always_visible": False})),
                        control("Longest trip shown in duration charts (minutes)", dcc.Slider(
                            id="f-dur", min=10, max=120, step=5, value=60,
                            marks={m: str(m) for m in (10, 30, 60, 90, 120)},
                            tooltip={"placement": "bottom", "always_visible": False})),
                    ],
                ),

                # ---- KPIs
                html.Div(
                    style={"display": "flex", "gap": "12px", "flexWrap": "wrap", "marginBottom": "16px"},
                    children=[
                        kpi("k-trips", "Trips"),
                        kpi("k-sub", "Trips by subscribers"),
                        kpi("k-age", "Average rider age"),
                        kpi("k-med", "Median trip (minutes)"),
                        kpi("k-stations", "Stations used to start a trip"),
                    ],
                ),

                # ---- charts
                html.Div(
                    style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(420px, 1fr))", "gap": "16px"},
                    children=[
                        graph("g-stations", span=1),
                        graph("g-top"),
                        graph("g-user"),
                        graph("g-gender"),
                        graph("g-age"),
                        graph("g-dur"),
                        graph("g-box"),
                        graph("g-agegroup"),
                        graph("g-corr"),
                    ],
                ),
                html.P("Data: Ford GoBike trip data, February 2019 (cleaned: missing values, duplicates and impossible ages removed).",
                       style={"color": MUTED, "fontSize": "12px", "marginTop": "16px"}),
            ],
        )
    ],
)


# ------------------------------------------------------------------ logic
def filter_data(users, genders, bsfa, age_range):
    dff = df[df["user_type"].isin(users or []) & df["member_gender"].isin(genders or [])]
    dff = dff[dff["age"].between(age_range[0], age_range[1])]
    if bsfa != "All":
        dff = dff[dff["bike_share_for_all_trip"] == bsfa]
    return dff


def build_figures(dff, max_dur):
    titles = {
        "stations": "Where trips start (bigger dot = more trips)",
        "top": "10 busiest start stations",
        "user": "Trips by user type",
        "gender": "Trips by gender",
        "age": "Rider age",
        "dur": "Trip duration",
        "box": "Trip duration by user type and gender",
        "agegroup": "Median trip duration by age group",
        "corr": "Correlation between numeric variables",
    }
    if dff.empty:
        return [empty_fig(t) for t in titles.values()]

    # 1. station map (no basemap needed, works offline)
    st = (dff.groupby(["start_station_name", "start_station_latitude", "start_station_longitude"])
             .size().reset_index(name="trips"))
    f1 = px.scatter(st, x="start_station_longitude", y="start_station_latitude", size="trips",
                    size_max=28, hover_name="start_station_name", hover_data={"trips": True,
                    "start_station_longitude": False, "start_station_latitude": False},
                    color_discrete_sequence=[COLORS["Subscriber"]], opacity=0.6)
    f1.update_yaxes(title="Latitude", scaleanchor=None)
    f1.update_xaxes(title="Longitude")
    style_fig(f1, titles["stations"], height=420)

    # 2. top stations
    top = dff["start_station_name"].value_counts().head(10).sort_values()
    f2 = px.bar(x=top.values, y=top.index, orientation="h", color_discrete_sequence=[COLORS["Subscriber"]])
    f2.update_xaxes(title="Trips")
    f2.update_yaxes(title=None)
    style_fig(f2, titles["top"], height=420)
    f2.update_layout(margin=dict(l=230, r=16, t=48, b=44))

    # 3. user type
    ut = dff["user_type"].value_counts().reset_index()
    ut.columns = ["user_type", "trips"]
    f3 = px.bar(ut, x="user_type", y="trips", color="user_type", color_discrete_map=COLORS, text_auto=".3s")
    f3.update_layout(showlegend=False)
    f3.update_xaxes(title=None)
    f3.update_yaxes(title="Trips")
    style_fig(f3, titles["user"])

    # 4. gender
    ge = dff["member_gender"].value_counts().reset_index()
    ge.columns = ["gender", "trips"]
    f4 = px.bar(ge, x="gender", y="trips", color="gender", color_discrete_map=COLORS, text_auto=".3s")
    f4.update_layout(showlegend=False)
    f4.update_xaxes(title=None)
    f4.update_yaxes(title="Trips")
    style_fig(f4, titles["gender"])

    # 5. age histogram
    f5 = px.histogram(dff, x="age", nbins=36, color_discrete_sequence=[COLORS["Subscriber"]])
    f5.update_xaxes(title="Age (years)")
    f5.update_yaxes(title="Trips")
    f5.update_traces(marker_line_width=0.5, marker_line_color="white")
    style_fig(f5, titles["age"])

    # 6. duration histogram (capped for readability)
    short = dff[dff["duration_min"] <= max_dur]
    f6 = px.histogram(short, x="duration_min", color="user_type", nbins=max(10, int(max_dur / 2)),
                      color_discrete_map=COLORS, barmode="overlay", opacity=0.75)
    f6.update_xaxes(title="Minutes")
    f6.update_yaxes(title="Trips")
    style_fig(f6, f"{titles['dur']} (trips up to {max_dur} min)")
    f6.update_layout(legend_title_text="")

    # 7. box plot
    if short.empty:
        f7 = empty_fig(titles["box"])
    else:
        f7 = px.box(short, x="member_gender", y="duration_min", color="user_type",
                    color_discrete_map=COLORS, category_orders={"member_gender": ["Male", "Female", "Other"]})
        f7.update_xaxes(title=None)
        f7.update_yaxes(title="Minutes")
        style_fig(f7, f"{titles['box']} (up to {max_dur} min)")
        f7.update_layout(legend_title_text="")

    # 8. median duration by age group
    ag = (dff.groupby(["age_group", "user_type"], observed=True)["duration_min"].median().reset_index())
    f8 = px.bar(ag, x="age_group", y="duration_min", color="user_type", barmode="group",
                color_discrete_map=COLORS)
    f8.update_xaxes(title="Age group")
    f8.update_yaxes(title="Median minutes")
    style_fig(f8, titles["agegroup"])
    f8.update_layout(legend_title_text="")

    # 9. correlation
    cols = ["age", "duration_min", "start_station_latitude", "start_station_longitude"]
    labels = ["Age", "Duration", "Start lat", "Start lon"]
    corr = dff[cols].corr()
    f9 = go.Figure(go.Heatmap(z=corr.values, x=labels, y=labels, zmin=-1, zmax=1,
                              colorscale="RdBu", reversescale=True,
                              text=corr.round(2).values, texttemplate="%{text}"))
    style_fig(f9, titles["corr"])

    return [f1, f2, f3, f4, f5, f6, f7, f8, f9]


@app.callback(
    [Output("k-trips", "children"), Output("k-sub", "children"), Output("k-age", "children"),
     Output("k-med", "children"), Output("k-stations", "children"),
     Output("g-stations", "figure"), Output("g-top", "figure"), Output("g-user", "figure"),
     Output("g-gender", "figure"), Output("g-age", "figure"), Output("g-dur", "figure"),
     Output("g-box", "figure"), Output("g-agegroup", "figure"), Output("g-corr", "figure")],
    [Input("f-user", "value"), Input("f-gender", "value"), Input("f-bsfa", "value"),
     Input("f-age", "value"), Input("f-dur", "value")],
)
def update(users, genders, bsfa, age_range, max_dur):
    dff = filter_data(users, genders, bsfa, age_range)
    figs = build_figures(dff, max_dur)
    if dff.empty:
        kpis = ["0", "-", "-", "-", "0"]
    else:
        kpis = [
            f"{len(dff):,}",
            f"{(dff['user_type'] == 'Subscriber').mean():.0%}",
            f"{dff['age'].mean():.1f}",
            f"{dff['duration_min'].median():.1f}",
            f"{dff['start_station_name'].nunique():,}",
        ]
    return kpis + figs


if __name__ == "__main__":
    app.run(debug=False)
