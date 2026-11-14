
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# -------------------------------
# PAGE CONFIGURATION
# -------------------------------

st.set_page_config(
    page_title="India Energy Analytics",
    page_icon="⚡",
    layout="wide"
)

st.title("India's Renewable Energy Transition")
st.markdown(
    "### Electricity Generation, Renewable Growth and Carbon Emissions"
)

# -------------------------------
# LOAD DATA
# -------------------------------

DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "datasets"
    / "dashboard_data.csv"
)

@st.cache_data
def load_data():
    data = pd.read_csv(DATA_PATH)
    data = data.sort_values("year")
    return data

try:
    df = load_data()
except FileNotFoundError:
    st.error(f"Dataset not found: {DATA_PATH}")
    st.stop()

# -------------------------------
# SIDEBAR FILTERS
# -------------------------------

st.sidebar.header("Dashboard Filters")

min_year = int(df["year"].min())
max_year = int(df["year"].max())

selected_years = st.sidebar.slider(
    "Select year range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

filtered = df[
    (df["year"] >= selected_years[0]) &
    (df["year"] <= selected_years[1])
].copy()

if filtered.empty:
    st.warning("No data available for this selection.")
    st.stop()

latest = filtered.iloc[-1]

# -------------------------------
# KPI METRICS
# -------------------------------

st.subheader("Energy Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Electricity Generation",
    f'{latest["electricity_generation_twh"]:,.1f} TWh'
)

col2.metric(
    "Renewable Generation",
    f'{latest["renewables_electricity_twh"]:,.1f} TWh'
)

col3.metric(
    "Coal Generation",
    f'{latest["coal_electricity_twh"]:,.1f} TWh'
)

col4.metric(
    "Electricity Emissions",
    f'{latest["electricity_emissions_mtco2eq"]:,.1f} MtCO₂e'
)

# -------------------------------
# GENERATION TREND
# -------------------------------

st.divider()
st.subheader("1. Electricity Generation Trends")

generation_columns = {
    "coal_electricity_twh": "Coal",
    "gas_electricity_twh": "Gas",
    "oil_electricity_twh": "Oil",
    "solar_electricity_twh": "Solar",
    "wind_electricity_twh": "Wind",
    "hydro_electricity_twh": "Hydro",
    "nuclear_electricity_twh": "Nuclear"
}

available = {
    col: label
    for col, label in generation_columns.items()
    if col in filtered.columns
}

if available:
    generation = filtered[["year"] + list(available)].melt(
        id_vars="year",
        var_name="source",
        value_name="generation"
    )

    generation["source"] = generation["source"].map(available)

    fig = px.line(
        generation,
        x="year",
        y="generation",
        color="source",
        markers=True,
        title="Electricity Generation by Source",
        labels={
            "year": "Year",
            "generation": "Generation (TWh)",
            "source": "Energy Source"
        }
    )

    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# RENEWABLE VS COAL
# -------------------------------

st.subheader("2. Renewable vs Coal Generation")

comparison_columns = [
    "renewables_electricity_twh",
    "coal_electricity_twh"
]

if all(col in filtered.columns for col in comparison_columns):
    comparison = filtered[
        ["year"] + comparison_columns
    ].melt(
        id_vars="year",
        var_name="source",
        value_name="generation"
    )

    comparison["source"] = comparison["source"].map({
        "renewables_electricity_twh": "Renewables",
        "coal_electricity_twh": "Coal"
    })

    fig = px.area(
        comparison,
        x="year",
        y="generation",
        color="source",
        title="Renewable and Coal Generation",
        labels={"generation": "Generation (TWh)"}
    )

    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# RENEWABLE SHARE
# -------------------------------

st.subheader("3. Renewable Energy Share")

if "renewable_share" in filtered.columns:
    fig = px.line(
        filtered,
        x="year",
        y="renewable_share",
        markers=True,
        title="Renewable Share of Electricity Generation",
        labels={"renewable_share": "Share (%)"}
    )

    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# CARBON EMISSIONS
# -------------------------------

st.subheader("4. Electricity-Related Carbon Emissions")

if "electricity_emissions_mtco2eq" in filtered.columns:
    fig = px.line(
        filtered,
        x="year",
        y="electricity_emissions_mtco2eq",
        markers=True,
        title="Electricity-Related Emissions",
        labels={"electricity_emissions_mtco2eq": "Emissions (MtCO₂e)"}
    )

    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# CARBON INTENSITY
# -------------------------------

st.subheader("5. Electricity Carbon Intensity")

intensity_column = "electricity_carbon_intensity_gco2eq_per_kwh"

if intensity_column in filtered.columns:
    fig = px.line(
        filtered,
        x="year",
        y=intensity_column,
        markers=True,
        title="Carbon Intensity Over Time",
        labels={intensity_column: "gCO₂e/kWh"}
    )

    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# RAW DATA
# -------------------------------

st.divider()
st.subheader("6. Explore Dataset")

st.dataframe(filtered, use_container_width=True)

st.download_button(
    "Download filtered dataset",
    data=filtered.to_csv(index=False),
    file_name="india_energy_filtered.csv",
    mime="text/csv"
)

st.caption(
    "Data source: Our World in Data. "
    "Interpretations are based on the selected dataset and year range."
)
