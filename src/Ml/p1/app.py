"""
Boston Housing Price Predictor  -  Streamlit GUI
Run:  streamlit run app.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.metrics import make_scorer, r2_score
from sklearn.model_selection import (GridSearchCV, ShuffleSplit,
                                     train_test_split, validation_curve)
from sklearn.tree import DecisionTreeRegressor

FEATURES = ["RM", "LSTAT", "PTRATIO"]
TARGET = "MEDV"
DATA_PATH = Path(__file__).parent / "housing.csv"
ACCENT = "#7c5cff"

st.set_page_config(page_title="Boston Housing Predictor", page_icon="🏠",
                   layout="wide", initial_sidebar_state="expanded")

# --------------------------------------------------------------------------- #
# Styling
# --------------------------------------------------------------------------- #
st.markdown(
    """
    <style>
    .block-container {padding-top: 1.5rem; max-width: 1300px;}
    .hero {
        background: linear-gradient(120deg, #7c5cff 0%, #2dd4bf 100%);
        padding: 1.6rem 2rem; border-radius: 18px; margin-bottom: 1.2rem;
        box-shadow: 0 10px 30px rgba(124,92,255,.25);
    }
    .hero h1 {color: #fff; margin: 0; font-size: 2rem;}
    .hero p  {color: rgba(255,255,255,.9); margin: .3rem 0 0 0;}
    .price-card {
        background: #171b26; border: 1px solid #262c3d; border-radius: 18px;
        padding: 1.4rem 1.6rem; text-align: center;
    }
    .price-card .label {color: #9aa3b8; font-size: .9rem; letter-spacing: .08em; text-transform: uppercase;}
    .price-card .value {font-size: 3rem; font-weight: 800;
        background: linear-gradient(120deg, #7c5cff, #2dd4bf);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
    .price-card .sub {color: #9aa3b8; font-size: .95rem;}
    div[data-testid="stMetric"] {
        background: #171b26; border: 1px solid #262c3d; padding: .9rem 1rem; border-radius: 14px;
    }
    .stTabs [data-baseweb="tab"] {font-size: 1rem; padding: .6rem 1.2rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------- #
# Data & model  (same pipeline as the notebook)
# --------------------------------------------------------------------------- #
@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


def fit_model(X, y):
    """Grid search over max_depth (1-10) with ShuffleSplit CV - as in the notebook."""
    cv_sets = ShuffleSplit(n_splits=10, test_size=0.20, random_state=0)
    grid = GridSearchCV(
        DecisionTreeRegressor(random_state=0),
        {"max_depth": list(range(1, 11))},
        scoring=make_scorer(r2_score),
        cv=cv_sets,
    ).fit(X, y)
    return grid.best_estimator_


@st.cache_resource(show_spinner="Training the model...")
def train_everything():
    data = load_data()
    X, y = data[FEATURES], data[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)

    model = fit_model(X_train, y_train)

    # 10 models on different splits -> used for the "prediction range" (model sensitivity)
    ensemble = []
    for k in range(10):
        a, _, b, _ = train_test_split(X, y, test_size=0.2, random_state=k)
        ensemble.append(fit_model(a, b))

    depths = np.arange(1, 11)
    tr, te = validation_curve(
        DecisionTreeRegressor(random_state=0), X_train, y_train,
        param_name="max_depth", param_range=depths,
        cv=ShuffleSplit(n_splits=10, test_size=0.2, random_state=0), scoring="r2")
    curve = pd.DataFrame({
        "depth": depths,
        "train": tr.mean(axis=1), "train_std": tr.std(axis=1),
        "val": te.mean(axis=1), "val_std": te.std(axis=1),
    })
    return dict(model=model, ensemble=ensemble, X_test=X_test, y_test=y_test, curve=curve)


def predict(model, rm, lstat, ptratio) -> float:
    return float(model.predict(pd.DataFrame([[rm, lstat, ptratio]], columns=FEATURES))[0])


data = load_data()
art = train_everything()
model = art["model"]
test_r2 = r2_score(art["y_test"], model.predict(art["X_test"]))
fmt = lambda v: f"${v:,.0f}"

# --------------------------------------------------------------------------- #
# Header + sidebar
# --------------------------------------------------------------------------- #
st.markdown(
    """<div class="hero"><h1>🏠 Boston Housing Price Predictor</h1>
    <p>Decision-tree regression · tuned with grid search · explore the data and price any neighbourhood</p></div>""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("🎛️ Neighbourhood features")
    rm = st.slider("🛏️ RM — average rooms per home", float(data.RM.min()), float(data.RM.max()),
                   float(data.RM.median()), 0.1)
    lstat = st.slider("📉 LSTAT — % lower-status population", float(data.LSTAT.min()),
                      float(data.LSTAT.max()), float(round(data.LSTAT.median(), 1)), 0.1)
    ptratio = st.slider("🎓 PTRATIO — students per teacher", float(data.PTRATIO.min()),
                        float(data.PTRATIO.max()), float(data.PTRATIO.median()), 0.1)
    st.divider()
    st.caption("Model")
    st.metric("Optimal max_depth", model.get_params()["max_depth"])
    st.metric("R² on test set", f"{test_r2:.3f}")
    st.caption(f"Trained on {len(data)} neighbourhoods")

pred = predict(model, rm, lstat, ptratio)
ens_preds = [predict(m, rm, lstat, ptratio) for m in art["ensemble"]]
lo, hi = min(ens_preds), max(ens_preds)
percentile = (data[TARGET] < pred).mean() * 100

tab_pred, tab_data, tab_model, tab_clients = st.tabs(
    ["🏠 Predict", "📊 Data explorer", "📈 Model analysis", "👥 Compare clients"])

# --------------------------------------------------------------------------- #
# Tab 1: prediction
# --------------------------------------------------------------------------- #
with tab_pred:
    c1, c2 = st.columns([1, 1.15], gap="large")
    with c1:
        st.markdown(
            f"""<div class="price-card"><div class="label">Estimated median home value</div>
            <div class="value">{fmt(pred)}</div>
            <div class="sub">Likely range across 10 re-trained models: {fmt(lo)} – {fmt(hi)}</div></div>""",
            unsafe_allow_html=True)
        st.write("")
        m1, m2, m3 = st.columns(3)
        m1.metric("vs. dataset mean", fmt(pred), f"{(pred / data[TARGET].mean() - 1) * 100:+.1f}%")
        m2.metric("vs. dataset median", fmt(pred), f"{(pred / data[TARGET].median() - 1) * 100:+.1f}%")
        m3.metric("Price percentile", f"{percentile:.0f}th")
        verdict = ("premium" if percentile >= 75 else "above average" if percentile >= 50
                   else "below average" if percentile >= 25 else "budget")
        st.info(f"This neighbourhood falls in the **{verdict}** segment of Boston housing.")
    with c2:
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=pred,
            number={"prefix": "$", "valueformat": ",.0f"},
            gauge={"axis": {"range": [data[TARGET].min(), data[TARGET].max()]},
                   "bar": {"color": ACCENT},
                   "steps": [
                       {"range": [data[TARGET].min(), data[TARGET].quantile(.25)], "color": "#1f2433"},
                       {"range": [data[TARGET].quantile(.25), data[TARGET].quantile(.75)], "color": "#262c3d"},
                       {"range": [data[TARGET].quantile(.75), data[TARGET].max()], "color": "#2f3750"}],
                   "threshold": {"line": {"color": "#2dd4bf", "width": 4}, "value": data[TARGET].median()}},
        ))
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=0), paper_bgcolor="rgba(0,0,0,0)",
                          font_color="#e8eaf0")
        st.plotly_chart(fig, width="stretch")
        st.caption("Teal line = dataset median. Shaded bands = bottom 25% / middle 50% / top 25%.")

    st.subheader("How does each feature move the price?")
    cols = st.columns(3)
    current = {"RM": rm, "LSTAT": lstat, "PTRATIO": ptratio}
    for col, feat in zip(cols, FEATURES):
        grid = np.linspace(data[feat].min(), data[feat].max(), 60)
        ys = [predict(model, *[g if f == feat else current[f] for f in FEATURES]) for g in grid]
        f = go.Figure(go.Scatter(x=grid, y=ys, mode="lines", line=dict(color=ACCENT, width=3), name="model"))
        f.add_trace(go.Scatter(x=[current[feat]], y=[pred], mode="markers",
                               marker=dict(size=13, color="#2dd4bf", line=dict(width=2, color="white")),
                               name="you"))
        f.update_layout(height=260, title=feat, showlegend=False, margin=dict(l=10, r=10, t=40, b=10),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        yaxis_tickprefix="$", font_color="#e8eaf0")
        col.plotly_chart(f, width="stretch")

# --------------------------------------------------------------------------- #
# Tab 2: data explorer
# --------------------------------------------------------------------------- #
with tab_data:
    a, b, c, d = st.columns(4)
    a.metric("Neighbourhoods", len(data))
    b.metric("Min price", fmt(data[TARGET].min()))
    c.metric("Median price", fmt(data[TARGET].median()))
    d.metric("Max price", fmt(data[TARGET].max()))

    l, r = st.columns(2, gap="large")
    with l:
        feat = st.selectbox("Feature vs. price", FEATURES)
        fig = px.scatter(data, x=feat, y=TARGET, color=TARGET, color_continuous_scale="Viridis", opacity=.8)
        fig.add_trace(go.Scatter(x=[current[feat]], y=[pred], mode="markers", name="your selection",
                                 marker=dict(size=16, symbol="star", color="#ff5c8a",
                                             line=dict(width=1.5, color="white"))))
        fig.update_layout(height=380, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          coloraxis_showscale=False, font_color="#e8eaf0")
        st.plotly_chart(fig, width="stretch")
    with r:
        st.markdown("**Correlation matrix**")
        corr = data.corr().round(2)
        fig = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r", zmin=-1, zmax=1)
        fig.update_layout(height=380, paper_bgcolor="rgba(0,0,0,0)", font_color="#e8eaf0")
        st.plotly_chart(fig, width="stretch")

    fig = px.histogram(data, x=TARGET, nbins=40, color_discrete_sequence=[ACCENT])
    fig.add_vline(x=pred, line_color="#2dd4bf", line_width=3, annotation_text="your prediction")
    fig.update_layout(height=300, title="Distribution of home values", bargap=.05,
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e8eaf0")
    st.plotly_chart(fig, width="stretch")

    with st.expander("Browse the raw data"):
        st.dataframe(data, width="stretch", height=300)
        st.download_button("⬇️ Download CSV", data.to_csv(index=False), "housing.csv", "text/csv")

# --------------------------------------------------------------------------- #
# Tab 3: model analysis
# --------------------------------------------------------------------------- #
with tab_model:
    curve = art["curve"]
    l, r = st.columns(2, gap="large")
    with l:
        st.markdown("**Complexity curve (bias–variance trade-off)**")
        fig = go.Figure()
        for key, name, color in (("train", "Training", "#ff5c8a"), ("val", "Validation", "#2dd4bf")):
            fig.add_trace(go.Scatter(x=curve.depth, y=curve[key] + curve[key + "_std"], mode="lines",
                                     line=dict(width=0), showlegend=False, hoverinfo="skip"))
            fig.add_trace(go.Scatter(x=curve.depth, y=curve[key] - curve[key + "_std"], mode="lines",
                                     line=dict(width=0), fill="tonexty", showlegend=False, hoverinfo="skip",
                                     fillcolor="rgba(255,92,138,.15)" if key == "train" else "rgba(45,212,191,.15)"))
            fig.add_trace(go.Scatter(x=curve.depth, y=curve[key], mode="lines+markers", name=name,
                                     line=dict(color=color, width=3)))
        fig.add_vline(x=model.get_params()["max_depth"], line_dash="dash", line_color="#9aa3b8",
                      annotation_text="chosen depth")
        fig.update_layout(height=380, xaxis_title="max_depth", yaxis_title="R² score", yaxis_range=[-0.05, 1.05],
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e8eaf0")
        st.plotly_chart(fig, width="stretch")
        st.caption("Depth 1 under-fits (high bias). Depth 10 over-fits (high variance). Validation peaks around 4–6.")
    with r:
        st.markdown("**Predicted vs. actual (test set)**")
        pv = pd.DataFrame({"Actual": art["y_test"].values, "Predicted": model.predict(art["X_test"])})
        fig = px.scatter(pv, x="Actual", y="Predicted", opacity=.8, color_discrete_sequence=["#f59e0b"])
        lim = [data[TARGET].min(), data[TARGET].max()]
        fig.add_trace(go.Scatter(x=lim, y=lim, mode="lines", line=dict(dash="dash", color="#9aa3b8"),
                                 name="perfect"))
        fig.update_layout(height=380, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font_color="#e8eaf0")
        st.plotly_chart(fig, width="stretch")

    imp = pd.Series(model.feature_importances_, index=FEATURES).sort_values()
    fig = px.bar(imp, orientation="h", color_discrete_sequence=[ACCENT])
    fig.update_layout(height=250, showlegend=False, xaxis_title="importance", yaxis_title="",
                      title="Feature importance", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font_color="#e8eaf0")
    st.plotly_chart(fig, width="stretch")

# --------------------------------------------------------------------------- #
# Tab 4: clients
# --------------------------------------------------------------------------- #
with tab_clients:
    st.markdown("Edit the table to price your own clients (this is Question 10 of the project).")
    default = pd.DataFrame({"Client": ["Client 1", "Client 2", "Client 3"],
                            "RM": [5.0, 4.0, 8.0], "LSTAT": [17.0, 32.0, 3.0], "PTRATIO": [15.0, 22.0, 12.0]})
    edited = st.data_editor(default, num_rows="dynamic", width="stretch", hide_index=True)
    edited = edited.dropna()
    if len(edited):
        edited = edited.assign(**{"Predicted price": model.predict(edited[FEATURES])})
        l, r = st.columns([1, 1.2], gap="large")
        l.dataframe(edited.style.format({"Predicted price": "${:,.0f}"}), width="stretch",
                    hide_index=True)
        fig = px.bar(edited, x="Client", y="Predicted price", color="Predicted price",
                     color_continuous_scale="Purples", text_auto="$,.0f")
        fig.add_hline(y=data[TARGET].mean(), line_dash="dash", line_color="#2dd4bf",
                      annotation_text="dataset mean")
        fig.update_layout(height=340, coloraxis_showscale=False, paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)", font_color="#e8eaf0")
        r.plotly_chart(fig, width="stretch")
