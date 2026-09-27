"""
Ford GoBike Analytics Platform
================================
One merged Dash dashboard combining the strongest pieces of every earlier
version: the multi-page sidebar structure, the KPI + computed-insights
panels, the net-flow station map, the fleet/rebalancing operations view,
and the demographics deep-dive — all running on the RAW february 2019
trip file, cleaned in-place when the app starts.

Run:
    pip install dash pandas numpy plotly
    python app.py
Then open http://127.0.0.1:8050
"""

import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, ctx, dash_table

# ============================================================ 1. LOAD + CLEAN
# The source file only ships with a truncated "MM:SS.f" start_time (no
# date/hour survives), so trip-by-hour/day analysis is not recoverable —
# every page below is built to work correctly without it.
HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else "."
CSV_NAME = "fordgobike-tripdataFor201902.csv"
CSV_PATH = CSV_NAME if os.path.exists(CSV_NAME) else os.path.join(HERE, CSV_NAME)

raw = pd.read_csv(CSV_PATH)

df = raw.copy()

# --- text columns: trim whitespace
for col in ["start_station_name", "end_station_name", "user_type",
            "member_gender", "bike_share_for_all_trip"]:
    df[col] = df[col].astype(str).str.strip().replace({"nan": np.nan})

# --- drop trips with no station identity (can't be placed on the map)
df = df.dropna(subset=["start_station_name", "end_station_name",
                        "start_station_id", "end_station_id"]).copy()

# --- duration: keep realistic trips only (1 min to 1 hour)
df = df[(df["duration_sec"] >= 60) & (df["duration_sec"] <= 3600)].copy()
df["duration_min"] = df["duration_sec"] / 60

# --- birth year -> age, dropping impossible years (pre-1940 / post-2001)
df.loc[(df["member_birth_year"] < 1940) | (df["member_birth_year"] > 2001),
       "member_birth_year"] = np.nan
df["age"] = 2019 - df["member_birth_year"]
df.loc[(df["age"] < 18) | (df["age"] > 80), "age"] = np.nan

AGE_LABELS = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
df["age_group"] = pd.cut(df["age"], [0, 24, 34, 44, 54, 64, 120],
                          labels=AGE_LABELS).astype(str)
df.loc[df["age_group"] == "nan", "age_group"] = "Unknown"

# --- gender: fill missing
df["member_gender"] = df["member_gender"].fillna("Unknown")

# --- bike_share flag: normalise
df["bike_share_for_all_trip"] = df["bike_share_for_all_trip"].fillna("No")

# --- region, from start-station coordinates
def assign_region(lat, lon):
    if lat > 37.70 and lon < -122.35:
        return "San Francisco"
    if lat > 37.75 and lon > -122.35:
        return "East Bay"
    if lat < 37.45:
        return "San Jose"
    return "Other Bay Area"

df["region"] = [assign_region(a, b) for a, b in
                 zip(df["start_station_latitude"], df["start_station_longitude"])]

# station coordinate lookup (used by the map + flow tables)
COORDS = pd.concat([
    df.groupby("start_station_name")[["start_station_latitude", "start_station_longitude"]]
      .first().set_axis(["lat", "lon"], axis=1),
    df.groupby("end_station_name")[["end_station_latitude", "end_station_longitude"]]
      .first().set_axis(["lat", "lon"], axis=1),
]).groupby(level=0).first()

N_DROPPED = len(raw) - len(df)
NET_THRESHOLD = 120  # |arrivals - departures| that triggers a rebalance alert

# ============================================================ 2. THEME
BG      = "#f8fafc"
CARD    = "#ffffff"
INK     = "#0f172a"
MUTED   = "#64748b"
GRID    = "#e5eaf1"
TEAL    = "#0f9d8a"
INDIGO  = "#4f46e5"
AMBER   = "#f59e0b"
CORAL   = "#ef4444"
SLATE   = "#94a3b8"
PURPLE  = "#8b5cf6"

USER_COLORS   = {"Subscriber": INDIGO, "Customer": AMBER}
GENDER_COLORS = {"Male": INDIGO, "Female": CORAL, "Other": TEAL, "Unknown": SLATE}
EQUITY_COLORS = {"Yes": TEAL, "No": "#cbd5e1"}

CSS = f"""
body{{margin:0;font-family:'Plus Jakarta Sans',Inter,'Segoe UI',Arial,sans-serif;background:{BG};color:{INK}}}
.card{{background:{CARD};border:1px solid {GRID};border-radius:14px;padding:18px 20px;min-width:0;
       box-shadow:0 1px 3px rgba(15,23,42,.03)}}
.card-title{{font-weight:700;font-size:15.5px}}
.card-sub{{color:{MUTED};font-size:12.5px;margin:2px 0 12px}}
.kpi-label{{color:{MUTED};font-size:12.5px;font-weight:600;display:flex;justify-content:space-between}}
.kpi-value{{font-size:27px;font-weight:800;margin:8px 0 10px;letter-spacing:-.5px}}
.kpi-foot{{font-size:11.5px;font-weight:600;border-top:1px solid #f1f5f9;padding-top:10px;
           display:flex;justify-content:space-between;align-items:center}}
.badge{{display:inline-flex;align-items:center;gap:4px;font-size:11px;font-weight:700;
        padding:3px 9px;border-radius:20px;white-space:nowrap}}
.badge-teal{{background:#ecfdf5;color:#059669}}
.badge-indigo{{background:#eef2ff;color:#4338ca}}
.badge-amber{{background:#fffbeb;color:#b45309}}
.badge-slate{{background:#f1f5f9;color:{MUTED}}}
.insight{{background:#f8fafc;border-radius:10px;padding:12px 14px;font-size:13.5px}}
.nav-btn{{display:block;width:100%;text-align:left;background:none;border:0;color:#cbd5e1;font-size:14.5px;
 font-weight:600;padding:12px 16px;border-radius:10px;margin-bottom:5px;cursor:pointer;font-family:inherit}}
.nav-btn:hover{{background:#111c33}}
.nav-btn.active{{background:#0d2f2b;color:#2dd4bf}}
.flabel{{font-size:10.5px;font-weight:700;color:{MUTED};letter-spacing:.06em;margin-right:8px;
         text-transform:uppercase}}
.btn{{border:1px solid {GRID};background:#fff;border-radius:8px;padding:8px 15px;font-weight:600;
      cursor:pointer;font-family:inherit;font-size:13px}}
.btn-primary{{background:{TEAL};color:#fff;border-color:{TEAL}}}
.rank-row{{display:flex;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid #f1f5f9;font-size:13.5px}}
.dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner table{{font-family:inherit}}
"""

# ============================================================ 3. HELPERS
def fig_style(fig, h=320, legend=True):
    fig.update_layout(
        template="plotly_white", height=h, margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=legend,
        font=dict(family="Plus Jakarta Sans, Inter, Arial", size=12, color="#334155"),
        legend=dict(orientation="h", y=-0.18, x=0.5, xanchor="center"))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#eef2f7")
    return fig


def graph(fig):
    return dcc.Graph(figure=fig, config={"displayModeBar": False})


def card(title, subtitle, body, span=None):
    style = {"gridColumn": f"span {span}"} if span else {}
    return html.Div(className="card", style=style, children=[
        html.Div(title, className="card-title"),
        html.Div(subtitle, className="card-sub"), body])


def kpi(label, value, foot, badge_text=None, badge_class="badge-slate"):
    badge = html.Span(badge_text, className=f"badge {badge_class}") if badge_text else None
    return html.Div(className="card", children=[
        html.Div([label, html.Span("\u24d8", style={"color": "#cbd5e1"})], className="kpi-label"),
        html.Div(value, className="kpi-value"),
        html.Div([html.Span(foot), badge], className="kpi-foot")])


def insight(title, text, color):
    return html.Div(className="insight", style={"borderLeft": f"4px solid {color}"}, children=[
        html.Div(title, style={"fontWeight": 700, "marginBottom": "4px"}),
        html.Div(text, style={"color": MUTED, "fontSize": "13px", "lineHeight": "1.5"})])


def grid(cols, children):
    return html.Div(children, style={"display": "grid", "gap": "16px", "marginBottom": "16px",
                                      "gridTemplateColumns": cols})


def hbar(series, color, x_title="Trips"):
    s = series.sort_values()
    fig = px.bar(x=s.values, y=s.index, orientation="h", color_discrete_sequence=[color],
                 labels={"x": x_title, "y": ""})
    return fig_style(fig, 330, legend=False)


def data_table(d, cols):
    return dash_table.DataTable(
        data=d.to_dict("records"), columns=[{"name": c, "id": c} for c in cols],
        style_as_list_view=True, page_size=8,
        style_header={"backgroundColor": "#f8fafc", "fontWeight": "700", "border": "none",
                      "fontSize": "12.5px", "color": MUTED, "textTransform": "uppercase"},
        style_cell={"fontFamily": "inherit", "fontSize": "13px", "padding": "9px 10px",
                    "border": "none", "borderBottom": f"1px solid {GRID}"},
        style_data={"backgroundColor": CARD})


def net_flow(d):
    flow = pd.concat([d.groupby("start_station_name").size().rename("Departures"),
                       d.groupby("end_station_name").size().rename("Arrivals")], axis=1).fillna(0)
    flow["net"] = flow["Arrivals"] - flow["Departures"]
    flow["total"] = flow["Arrivals"] + flow["Departures"]
    return flow.join(COORDS, how="left")


def make_map(flow):
    f = flow.dropna(subset=["lat", "lon"]).reset_index(names="station")
    f["size"] = f["net"].abs() + 12
    kw = dict(lat="lat", lon="lon", size="size", color="net", hover_name="station",
              hover_data={"size": False, "lat": False, "lon": False, "net": True, "total": True},
              color_continuous_scale="RdBu", color_continuous_midpoint=0,
              size_max=26, zoom=10.5, center=dict(lat=37.78, lon=-122.30))
    if hasattr(px, "scatter_map"):
        fig = px.scatter_map(f, **kw)
        fig.update_layout(map_style="carto-positron")
    else:
        fig = px.scatter_mapbox(f, **kw)
        fig.update_layout(mapbox_style="carto-positron")
    return fig_style(fig, 460, legend=False)


def apply_filters(rider, region, gender, equity, dur_range):
    d = df
    if rider != "all":
        d = d[d["user_type"] == rider]
    if region != "all":
        d = d[d["region"] == region]
    if gender != "all":
        d = d[d["member_gender"] == gender]
    if equity == "yes":
        d = d[d["bike_share_for_all_trip"] == "Yes"]
    if dur_range:
        d = d[(d["duration_min"] >= dur_range[0]) & (d["duration_min"] <= dur_range[1])]
    return d


# ============================================================ 4. PAGES
def page_overview(d):
    flow = net_flow(d)
    alerts = flow[flow["net"].abs() >= NET_THRESHOLD]
    sub, cus = d[d["user_type"] == "Subscriber"], d[d["user_type"] == "Customer"]

    kpis = grid("repeat(6, 1fr)", [
        kpi("Total Trips", f"{len(d):,}", f"{d['bike_id'].nunique():,} bikes used", "Active", "badge-teal"),
        kpi("Active Stations",
            f"{pd.concat([d['start_station_id'], d['end_station_id']]).nunique():,}",
            "Currently in use", "100% Up", "badge-teal"),
        kpi("Subscriber Ratio", f"{len(sub) / len(d) * 100:.1f}%" if len(d) else "0%",
            f"{len(sub):,} subscriber trips", "Commuters", "badge-indigo"),
        kpi("Avg Trip Duration", f"{d['duration_min'].mean():.1f} min" if len(d) else "—",
            f"Median {d['duration_min'].median():.1f} min" if len(d) else "—"),
        kpi("Equity Program", f"{(d['bike_share_for_all_trip'] == 'Yes').mean() * 100:.1f}%" if len(d) else "0%",
            "Bike Share For All", "Inclusion", "badge-amber"),
        kpi("Rebalance Alerts", f"{len(alerts)}",
            "Needs van dispatch" if len(alerts) else "All balanced",
            "Action needed" if len(alerts) else "Stable",
            "badge-amber" if len(alerts) else "badge-teal")])

    # main chart — trip-duration profile by rider type (no reliable date/hour to trend on)
    bins = np.arange(0, 61, 2)
    fig = go.Figure()
    for u in ["Subscriber", "Customer"]:
        v = d.loc[d["user_type"] == u, "duration_min"]
        if len(v):
            cnt, _ = np.histogram(v, bins=bins)
            fig.add_bar(x=bins[:-1], y=cnt / len(v) * 100, name=u, marker_color=USER_COLORS[u], opacity=0.75)
    fig.update_layout(barmode="overlay", xaxis_title="Trip duration (min)", yaxis_title="% of rider type's trips")
    main = card("Trip Duration Profile by Rider Type",
                "Share of each membership tier's trips across duration buckets",
                graph(fig_style(fig, 380)))

    # rider profile narrative
    if len(d):
        main_user = d["user_type"].mode()[0]
        main_gender = d["member_gender"].mode()[0]
        avg_age = d["age"].mean()
        top_station = d["start_station_name"].value_counts().index[0]
        profile = html.Div([
            html.Div("RIDER PROFILE", style={"color": TEAL, "fontWeight": 700, "fontSize": "11px",
                                             "letterSpacing": ".08em", "marginBottom": "6px"}),
            html.Div(f"{main_user} rider, {main_gender.lower()}",
                     style={"fontSize": "20px", "fontWeight": 800, "marginBottom": "8px"}),
            html.P(f"This selection typically takes trips around {d['duration_min'].mean():.1f} minutes long, "
                   f"with an average rider age of {avg_age:.0f}." if not pd.isna(avg_age) else
                   f"This selection typically takes trips around {d['duration_min'].mean():.1f} minutes long.",
                   style={"color": MUTED, "fontSize": "13.5px", "lineHeight": 1.6}),
            html.P(f"Busiest departure point: {top_station}.",
                   style={"color": MUTED, "fontSize": "13.5px", "lineHeight": 1.6})])
    else:
        profile = html.Div("No trips match the current filters.", style={"color": MUTED})

    ins = [insight("Fleet Redistribution Demand",
                    (f"{len(alerts)} stations need van dispatch (|net flow| ≥ {NET_THRESHOLD} rides) to restore "
                     "bay capacity.") if len(alerts) else f"No station exceeds a net flow of {NET_THRESHOLD} rides.",
                    AMBER)]
    if len(sub) and len(cus):
        ins.append(insight("Rider Cohort Dynamic",
                            f"Casual customers take {cus['duration_min'].mean() / sub['duration_min'].mean():.1f}x "
                            f"longer trips ({cus['duration_min'].mean():.1f}m vs {sub['duration_min'].mean():.1f}m), "
                            "suggesting recreational rather than commute use.", PURPLE))
    if len(d):
        top = d["start_station_name"].value_counts()
        ins.append(insight("Busiest Station",
                            f"{top.index[0]} starts {top.iloc[0]:,} trips "
                            f"({top.iloc[0] / len(d) * 100:.1f}% of all trips in this slice).", TEAL))

    side = card("Rider Profile & Computed Insights", "Synthesized live from the current filtered slice",
                html.Div([profile, html.Hr(style={"border": "none", "borderTop": f"1px solid {GRID}",
                                                    "margin": "14px 0"})] + ins,
                         style={"display": "grid", "gap": "10px"}))
    return html.Div([kpis, grid("2fr 1fr", [main, side])])


def page_network(d):
    flow = net_flow(d)
    surplus = flow.loc[flow["net"] > 0, "net"].nlargest(10)
    deficit = (-flow.loc[flow["net"] < 0, "net"]).nlargest(10)
    routes = d.groupby(["start_station_name", "end_station_name"]).size().nlargest(10)
    routes.index = [f"{a[:22]} → {b[:22]}" for a, b in routes.index]
    ranking = d["start_station_name"].value_counts().head(8).reset_index()
    ranking.columns = ["Station", "Trips"]

    return html.Div([
        grid("1fr", [card("Net Bike Flow by Station",
                          "Blue = more arrivals than departures (fills up). Red = more departures (drains). "
                          "Bubble size = size of the imbalance.",
                          graph(make_map(flow)))]),
        grid("1fr 1fr 1fr", [
            card("Top 10 Routes", "Most frequent start → end pairs", graph(hbar(routes, INDIGO))),
            card("Stations Filling Up", "Highest net arrivals — bikes need pickup", graph(hbar(surplus, TEAL))),
            card("Stations Draining", "Highest net departures — bikes need refill", graph(hbar(deficit, AMBER)))]),
        grid("1fr", [card("Station Leaderboard", "Top 8 stations by total trips started",
                          data_table(ranking, ["Station", "Trips"]))])])


def page_fleet(d):
    flow = net_flow(d).reset_index(names="Station")
    deficit = flow.sort_values("net")[["Station", "Departures", "Arrivals", "net"]].head(10)
    deficit.columns = ["Station", "Departures", "Arrivals", "Net Inventory Change"]
    surplus = flow.sort_values("net", ascending=False)[["Station", "Departures", "Arrivals", "net"]].head(10)
    surplus.columns = ["Station", "Departures", "Arrivals", "Net Inventory Change"]

    bike_usage = (d.groupby("bike_id")
                    .agg(trips=("duration_sec", "count"), hours=("duration_sec", lambda s: s.sum() / 3600))
                    .reset_index().sort_values("hours", ascending=False).head(15))
    fig_bikes = px.bar(bike_usage, x="bike_id", y="hours", color="hours", color_continuous_scale="Tealgrn",
                       labels={"bike_id": "Bike ID", "hours": "Total Operating Hours"})
    fig_bikes.update_layout(coloraxis_showscale=False, xaxis_type="category")

    return html.Div([
        grid("1fr 1fr", [
            card("Top Depleted Stations", "Needs restocking — largest negative net flow",
                 data_table(deficit, list(deficit.columns))),
            card("Top Overflow Stations", "Needs bike extraction — largest positive net flow",
                 data_table(surplus, list(surplus.columns)))]),
        grid("1fr", [card("Top 15 High-Mileage Bikes", "Maintenance queue — bikes with the most operating hours",
                          graph(fig_style(fig_bikes, 340, legend=False)))])])


def page_demographics(d):
    a = d.dropna(subset=["age"])
    f_age = fig_style(px.histogram(a, x="age", nbins=25, color_discrete_sequence=[INDIGO],
                                    labels={"age": "Rider Age"}), 300, False) if len(a) else \
        fig_style(go.Figure().add_annotation(text="No age data for this selection", showarrow=False,
                                             x=0.5, y=0.5, xref="paper", yref="paper"), 300, False)

    g = d["member_gender"].value_counts()
    f_gen = px.pie(names=g.index, values=g.values, hole=0.55, color=g.index, color_discrete_map=GENDER_COLORS)

    f_grp = go.Figure([go.Bar(name=u, x=AGE_LABELS, marker_color=c,
                              y=d[d["user_type"] == u].groupby("age_group").size()
                                .reindex(AGE_LABELS, fill_value=0).values)
                       for u, c in USER_COLORS.items()])
    f_grp.update_layout(barmode="group")

    b = d["bike_share_for_all_trip"].value_counts()
    f_bsa = px.pie(names=b.index, values=b.values, hole=0.55, color=b.index, color_discrete_map=EQUITY_COLORS)

    equity = d.groupby(["member_gender", "bike_share_for_all_trip"]).size().reset_index(name="count")
    f_equity = px.bar(equity, x="member_gender", y="count", color="bike_share_for_all_trip", barmode="stack",
                      color_discrete_map=EQUITY_COLORS,
                      labels={"member_gender": "", "count": "Trips", "bike_share_for_all_trip": "Equity Program"})

    sample = d.sample(min(len(d), 20000), random_state=1) if len(d) else d
    f_box = px.box(sample, x="user_type", y="duration_min", color="user_type", color_discrete_map=USER_COLORS,
                   labels={"user_type": "", "duration_min": "Minutes"})

    return html.Div([
        grid("1fr 1fr 1fr", [card("Age Distribution", "Trips by rider age", graph(f_age)),
                             card("Gender Split", "Share of trips by gender", graph(fig_style(f_gen, 300))),
                             card("Bike Share For All", "Equity program enrollment", graph(fig_style(f_bsa, 300)))]),
        grid("1fr 1fr", [card("Age Group by Rider Type", "Who rides, by age bracket and membership",
                              graph(fig_style(f_grp, 320))),
                         card("Gender vs Equity Adoption", "Enrollment in the equity program by gender",
                              graph(fig_style(f_equity, 320)))]),
        grid("1fr", [card("Trip Duration by Rider Type", "Distribution of trip minutes",
                          graph(fig_style(f_box, 300, False)))])])


PAGES = {
    "overview": ("Executive Overview", page_overview),
    "network": ("Station & Network Flow", page_network),
    "fleet": ("Fleet Operations & Rebalancing", page_fleet),
    "demo": ("Demographics & Inclusion", page_demographics),
}

# ============================================================ 5. LAYOUT
def dd(id_, all_label, options, width):
    opts = [{"label": all_label, "value": "all"}] + [{"label": str(o), "value": o} for o in options]
    return dcc.Dropdown(id=id_, options=opts, value="all", clearable=False, style={"width": width})


def flt(label, control):
    return html.Div([html.Span(label, className="flabel"), control],
                    style={"display": "flex", "alignItems": "center", "gap": "6px"})


app = Dash(__name__)
app.title = "Ford GoBike Analytics Platform"
app.index_string = app.index_string.replace(
    "</head>",
    f"<style>{CSS}</style>"
    "<link rel='preconnect' href='https://fonts.googleapis.com'>"
    "<link href='https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap' "
    "rel='stylesheet'></head>")

app.layout = html.Div(style={"display": "flex", "minHeight": "100vh"}, children=[
    dcc.Store(id="page", data="overview"),
    dcc.Download(id="download"),

    # ---- sidebar
    html.Div(style={"width": "260px", "background": "#0b1220", "padding": "22px 16px", "flexShrink": 0,
                    "display": "flex", "flexDirection": "column"}, children=[
        html.Div([html.Div("🚲 Ford GoBike", style={"color": "#fff", "fontSize": "19px", "fontWeight": 800}),
                  html.Div("ANALYTICS & OPERATIONS", style={"color": "#2dd4bf", "fontSize": "10.5px",
                                                            "letterSpacing": ".12em", "fontWeight": 700})],
                 style={"padding": "0 8px 18px", "borderBottom": "1px solid #1e293b", "marginBottom": "18px"}),
        html.Div("MODULES", style={"color": "#94a3b8", "fontSize": "11px", "fontWeight": 700,
                                   "letterSpacing": ".08em", "padding": "0 8px 12px"}),
        *[html.Button(v[0], id=f"nav-{k}", className="nav-btn") for k, v in PAGES.items()],
        html.Div(style={"flex": 1}),
        html.Div([html.Div("Dataset", style={"color": "#fff", "fontWeight": 700, "fontSize": "13px"}),
                  html.Div(f"{len(df):,} clean trips  ·  {N_DROPPED:,} dropped", style={"color": "#94a3b8", "fontSize": "11.5px"}),
                  html.Div("Feb 2019  ·  start_time has no usable date/hour, so time-of-day views are omitted.",
                           style={"color": "#64748b", "fontSize": "10.5px", "marginTop": "6px", "lineHeight": 1.4})],
                 style={"border": "1px solid #1e293b", "borderRadius": "10px", "padding": "12px 14px"}),
    ]),

    # ---- main
    html.Div(style={"flex": 1, "minWidth": 0}, children=[
        html.Div(style={"display": "flex", "justifyContent": "space-between", "alignItems": "center",
                        "padding": "16px 28px", "background": CARD, "borderBottom": f"1px solid {GRID}"}, children=[
            html.Div([html.Span("Ford GoBike Analytics  ›  ", style={"color": MUTED}),
                      html.Span(id="crumb", style={"fontWeight": 700})]),
            html.Button("Export Summary", id="btn-export", className="btn btn-primary")]),

        html.Div(style={"background": CARD, "borderBottom": f"1px solid {GRID}", "padding": "14px 28px 18px"}, children=[
            html.Div(style={"display": "flex", "flexWrap": "wrap", "gap": "14px 22px", "alignItems": "center"}, children=[
                flt("RIDER", dd("f-rider", "All Memberships", sorted(df["user_type"].unique()), "170px")),
                flt("REGION", dd("f-region", "All Regions", sorted(df["region"].unique()), "170px")),
                flt("GENDER", dd("f-gender", "All Genders", sorted(df["member_gender"].unique()), "150px")),
                flt("EQUITY", dcc.Dropdown(id="f-equity", clearable=False, value="all", style={"width": "190px"},
                                           options=[{"label": "All Trips", "value": "all"},
                                                    {"label": "Bike Share For All Only", "value": "yes"}])),
            ]),
            html.Div(style={"display": "flex", "flexWrap": "wrap", "gap": "18px 24px", "alignItems": "center",
                            "marginTop": "16px"}, children=[
                html.Button("Reset", id="btn-reset", className="btn"),
                flt("DURATION (MIN)", html.Div(dcc.RangeSlider(
                    id="f-dur", min=1, max=60, step=1, value=[1, 60],
                    marks={1: "1", 15: "15", 30: "30", 45: "45", 60: "60"},
                    tooltip={"placement": "bottom", "always_visible": False}),
                    style={"width": "260px"})),
                html.Span(id="f-note", style={"color": SLATE, "fontStyle": "italic", "fontSize": "12.5px"}),
            ]),
        ]),

        html.Div(id="content", style={"padding": "22px 28px"}),
    ]),
])

# ============================================================ 6. CALLBACKS
FILTER_IDS = ["f-rider", "f-region", "f-gender", "f-equity", "f-dur"]
FILTER_DEFAULTS = ["all", "all", "all", "all", [1, 60]]


@app.callback(Output("page", "data"), [Input(f"nav-{k}", "n_clicks") for k in PAGES],
              prevent_initial_call=True)
def set_page(*_):
    return ctx.triggered_id.replace("nav-", "")


@app.callback([Output(i, "value") for i in FILTER_IDS], Input("btn-reset", "n_clicks"),
              prevent_initial_call=True)
def reset(_):
    return FILTER_DEFAULTS


@app.callback([Output("content", "children"), Output("crumb", "children"), Output("f-note", "children")] +
              [Output(f"nav-{k}", "className") for k in PAGES],
              [Input("page", "data")] + [Input(i, "value") for i in FILTER_IDS])
def render(page, *filters):
    d = apply_filters(*filters)
    title, builder = PAGES[page]
    active = [f for f, dflt in zip(filters[:-1], FILTER_DEFAULTS[:-1]) if f != dflt]
    if list(filters[-1]) != FILTER_DEFAULTS[-1]:
        active.append(f"{filters[-1][0]}–{filters[-1][1]} min")
    note = "Filters: " + ", ".join(map(str, active)) if active else "No active filters applied"
    nav = ["nav-btn active" if k == page else "nav-btn" for k in PAGES]
    if d.empty:
        body = html.Div("No trips match these filters. Click Reset to start over.",
                        style={"padding": "60px", "textAlign": "center", "color": MUTED})
    else:
        body = builder(d)
    return [body, title, note] + nav


@app.callback(Output("download", "data"), Input("btn-export", "n_clicks"),
              [State(i, "value") for i in FILTER_IDS], prevent_initial_call=True)
def export(_, *filters):
    d = apply_filters(*filters)
    s = (d.groupby("user_type")
          .agg(trips=("bike_id", "size"), avg_duration_min=("duration_min", "mean"),
               median_duration_min=("duration_min", "median"), avg_age=("age", "mean"))
          .round(2).reset_index())
    return dcc.send_data_frame(s.to_csv, "gobike_summary.csv", index=False)


if __name__ == "__main__":
    app.run(debug=True)
