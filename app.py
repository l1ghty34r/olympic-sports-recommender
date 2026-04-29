import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from database import get_engine
from queries import (
    get_filter_countries,
    get_filter_disciplines,
    get_filter_sports,
    get_filter_years,
    get_filtered_medal_summary,
    get_filtered_winner_events,
    get_filtered_winners,
    get_recommendation_profiles,
    get_top_countries_by_filters,
)

st.set_page_config(page_title="Olympic Sports Recommender", layout="wide")


@st.cache_resource
def load_engine():
    return get_engine()


@st.cache_data
def load_recommendation_profiles():
    return get_recommendation_profiles(load_engine())


@st.cache_data
def load_filter_countries():
    return get_filter_countries(load_engine())


@st.cache_data
def load_filter_years(country_name):
    return get_filter_years(load_engine(), country_name)


@st.cache_data
def load_filter_sports(country_name, year):
    return get_filter_sports(load_engine(), country_name, year)


@st.cache_data
def load_filter_disciplines(country_name, year, sport_name):
    return get_filter_disciplines(load_engine(), country_name, year, sport_name)


@st.cache_data
def load_filtered_medal_summary(country_name, year, sport_name, discipline_name):
    return get_filtered_medal_summary(
        load_engine(),
        country_name=country_name,
        year=year,
        sport_name=sport_name,
        discipline_name=discipline_name,
    )


@st.cache_data
def load_top_countries(country_name, year, sport_name, discipline_name):
    return get_top_countries_by_filters(
        load_engine(),
        country_name=country_name,
        year=year,
        sport_name=sport_name,
        discipline_name=discipline_name,
    )


@st.cache_data
def load_filtered_winners(country_name, year, sport_name, discipline_name):
    return get_filtered_winners(
        load_engine(),
        country_name=country_name,
        year=year,
        sport_name=sport_name,
        discipline_name=discipline_name,
    )


@st.cache_data
def load_filtered_winner_events(country_name, year, sport_name, discipline_name):
    return get_filtered_winner_events(
        load_engine(),
        country_name=country_name,
        year=year,
        sport_name=sport_name,
        discipline_name=discipline_name,
    )


def prepare_recommendation_scores(df, user_height, user_weight, user_age):
    df = df.copy()

    if df.empty:
        return df

    std_height = df["avg_height"].std(ddof=0)
    std_weight = df["avg_weight"].std(ddof=0)
    std_age = df["avg_age"].std(ddof=0)

    std_height = 1 if pd.isna(std_height) or std_height == 0 else std_height
    std_weight = 1 if pd.isna(std_weight) or std_weight == 0 else std_weight
    std_age = 1 if pd.isna(std_age) or std_age == 0 else std_age

    df["z_height"] = (df["avg_height"] - user_height) / std_height
    df["z_weight"] = (df["avg_weight"] - user_weight) / std_weight
    df["z_age"] = (df["avg_age"] - user_age) / std_age

    df["std_distance"] = np.sqrt(
        df["z_height"] ** 2
        + df["z_weight"] ** 2
        + df["z_age"] ** 2
    )

    df["similarity_score"] = 1 / (1 + df["std_distance"])
    df["similarity_score"] = df["similarity_score"].round(3)

    def classify_score(score):
        if score >= 0.60:
            return "Very good match"
        elif score >= 0.50:
            return "Good match"
        elif score >= 0.40:
            return "Moderate match"
        else:
            return "Low match"

    df["match_level"] = df["similarity_score"].apply(classify_score)

    return df.sort_values("similarity_score", ascending=False).reset_index(drop=True)


def get_bar_color(score, rank):
    if rank == 0:
        return "#1f77b4"
    if rank == 1:
        return "#4f9ddf"
    if rank == 2:
        return "#82bcea"

    if score >= 0.60:
        return "#5DAE6F"
    elif score >= 0.50:
        return "#A6D96A"
    elif score >= 0.40:
        return "#F4D35E"
    else:
        return "#EE6C6C"


def plot_recommender_chart(df):
    df_plot = (
        df[["sport_name", "similarity_score"]]
        .sort_values("similarity_score", ascending=True)
        .reset_index(drop=True)
        .copy()
    )

    descending = df[["sport_name", "similarity_score"]].reset_index(drop=True)
    rank_map = {row["sport_name"]: idx for idx, (_, row) in enumerate(descending.iterrows())}
    colors = [
        get_bar_color(score, rank_map.get(sport, 999))
        for sport, score in zip(df_plot["sport_name"], df_plot["similarity_score"])
    ]

    fig_height = max(3.2, len(df_plot) * 0.36)
    fig, ax = plt.subplots(figsize=(7.2, fig_height), facecolor="white")
    ax.set_facecolor("white")

    bars = ax.barh(
        df_plot["sport_name"],
        df_plot["similarity_score"],
        color=colors,
        edgecolor="none",
    )

    ax.set_title("Top 10 passende Sportarten", fontsize=12)
    ax.set_xlabel("Similarity Score (0–1)")
    ax.set_ylabel("")
    ax.set_xlim(0, 1)
    ax.grid(axis="x", linestyle="--", alpha=0.22)

    for bar, score in zip(bars, df_plot["similarity_score"]):
        ax.text(
            bar.get_width() + 0.015,
            bar.get_y() + bar.get_height() / 2,
            f"{score:.3f}",
            va="center",
            fontsize=9,
            color="#222222",
        )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_alpha(0.25)

    fig.tight_layout()
    return fig


def plot_medal_summary_chart(gold, silver, bronze):
    labels = ["Bronze", "Silber", "Gold"]
    values = [bronze, silver, gold]
    colors = ["#CD7F32", "silver", "gold"]

    fig, ax = plt.subplots(figsize=(5.6, 2.4), facecolor="white")
    ax.set_facecolor("white")

    bars = ax.barh(labels, values, color=colors, edgecolor="none")

    ax.set_title("Medaillenverteilung", fontsize=12)
    ax.set_xlabel("Anzahl einzigartiger Medaillenentscheidungen")
    ax.set_ylabel("")
    max_val = max(values) if max(values) > 0 else 1
    ax.set_xlim(0, max_val * 1.18)
    ax.grid(axis="x", linestyle="--", alpha=0.18)

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_width() + (max_val * 0.03),
            bar.get_y() + bar.get_height() / 2,
            f"{value}",
            va="center",
            fontsize=9,
            color="#222222",
        )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_alpha(0.25)

    fig.tight_layout()
    return fig


def render_score_badge(score):
    if score >= 0.60:
        return "Very good match"
    if score >= 0.50:
        return "Good match"
    if score >= 0.40:
        return "Moderate match"
    return "Low match"


def apply_table_filters(df):
    if df.empty:
        return df

    filtered_df = df.copy()

    st.markdown("**Zusätzliche Tabellenfilter**")
    cols = st.columns(5)

    if "medal" in filtered_df.columns:
        with cols[0]:
            medal_options = ["Alle"] + sorted(filtered_df["medal"].dropna().unique().tolist())
            selected_medal = st.selectbox("Medaille", medal_options)
        if selected_medal != "Alle":
            filtered_df = filtered_df[filtered_df["medal"] == selected_medal]

    if "year" in filtered_df.columns:
        with cols[1]:
            year_options = ["Alle"] + sorted(filtered_df["year"].dropna().astype(str).unique().tolist())
            selected_year = st.selectbox("Jahr (Tabelle)", year_options)
        if selected_year != "Alle":
            filtered_df = filtered_df[filtered_df["year"].astype(str) == selected_year]

    if "country" in filtered_df.columns:
        with cols[2]:
            country_options = ["Alle"] + sorted(filtered_df["country"].dropna().unique().tolist())
            selected_country = st.selectbox("Land (Tabelle)", country_options)
        if selected_country != "Alle":
            filtered_df = filtered_df[filtered_df["country"] == selected_country]

    if "sport_name" in filtered_df.columns:
        with cols[3]:
            sport_options = ["Alle"] + sorted(filtered_df["sport_name"].dropna().unique().tolist())
            selected_sport = st.selectbox("Sportart (Tabelle)", sport_options)
        if selected_sport != "Alle":
            filtered_df = filtered_df[filtered_df["sport_name"] == selected_sport]

    if "discipline" in filtered_df.columns:
        with cols[4]:
            discipline_options = ["Alle"] + sorted(filtered_df["discipline"].dropna().unique().tolist())
            selected_discipline = st.selectbox("Disziplin (Tabelle)", discipline_options)
        if selected_discipline != "Alle":
            filtered_df = filtered_df[filtered_df["discipline"] == selected_discipline]

    return filtered_df


def show_recommendation_page():
    st.title("Olympic Sports Recommender")
    st.markdown(
        "Diese App empfiehlt passende olympische Sportarten auf Basis eines eingegebenen Körperprofils."
    )

    with st.expander("Wie funktioniert der Recommender?"):
        st.markdown(
            """
            **1. Erfolgsprofile pro Sportart**

            Für jede Sportart wird aus historischen Medaillengewinnern ein durchschnittliches Profil gebildet:
            - durchschnittliche Größe
            - durchschnittliches Gewicht
            - durchschnittliches Alter

            **2. Standardisierte Distanz**

            Dein Profil wird mit jedem dieser Sportprofile verglichen.  
            Dabei werden Größe, Gewicht und Alter standardisiert, damit die drei Merkmale fair vergleichbar sind.

            **3. Similarity Score**

            Aus der standardisierten Distanz wird ein Similarity Score berechnet:

            **Similarity Score = 1 / (1 + Distanz)**

            **Interpretation**
            - Werte liegen zwischen **0 und 1**
            - je höher der Wert, desto ähnlicher ist dein Profil dem durchschnittlichen Erfolgsprofil der Sportart
            - der Wert ist **keine Wahrscheinlichkeit**
            - der Wert ist ein **Ähnlichkeitsmaß**
            """
        )

    st.subheader("Olympic Sports Recommender")

    col1, col2 = st.columns(2)

    with col1:
        user_height = st.slider("Größe (cm)", min_value=140, max_value=220, value=185)
        user_weight = st.slider("Gewicht (kg)", min_value=40, max_value=150, value=80)

    with col2:
        user_age = st.slider("Alter", min_value=12, max_value=50, value=25)
        user_sex = st.selectbox("Geschlecht", ["M", "F"])

    raw_df = load_recommendation_profiles()
    raw_df = raw_df[raw_df["sex"] == user_sex].copy()

    if raw_df.empty:
        st.warning("Für das gewählte Profil konnten keine passenden Daten gefunden werden.")
        return

    df = prepare_recommendation_scores(raw_df, user_height, user_weight, user_age)
    top_10 = df.head(10).copy()
    top_3 = top_10.head(3)

    kpi1, kpi2, kpi3 = st.columns(3)

    with kpi1:
        if len(top_3) > 0:
            st.metric(
                "Top 1",
                top_3.iloc[0]["sport_name"],
                f"Score {top_3.iloc[0]['similarity_score']:.3f}",
            )
    with kpi2:
        if len(top_3) > 1:
            st.metric(
                "Top 2",
                top_3.iloc[1]["sport_name"],
                f"Score {top_3.iloc[1]['similarity_score']:.3f}",
            )
    with kpi3:
        if len(top_3) > 2:
            st.metric(
                "Top 3",
                top_3.iloc[2]["sport_name"],
                f"Score {top_3.iloc[2]['similarity_score']:.3f}",
            )

    left_col, right_col = st.columns([1.35, 0.95])

    with left_col:
        st.subheader("Top 10 passende Sportarten")
        st.pyplot(plot_recommender_chart(top_10), use_container_width=False)

    with right_col:
        st.subheader("Interpretation")

        best_sport = top_10.iloc[0]["sport_name"]
        best_score = float(top_10.iloc[0]["similarity_score"])
        second_score = float(top_10.iloc[1]["similarity_score"]) if len(top_10) > 1 else None
        best_level = render_score_badge(best_score)

        st.markdown(
            f"**Beste Empfehlung:** {best_sport} mit einem Similarity Score von **{best_score:.3f}**."
        )
        st.progress(min(max(best_score, 0.0), 1.0), text=f"Top-Empfehlung: {best_level}")

        if second_score is not None:
            diff = best_score - second_score
            st.markdown(f"Der Abstand zur zweitbesten Empfehlung beträgt **{diff:.3f}**.")

        st.markdown(
            """
            **Lesebeispiel**
            - höhere Werte = bessere Passung
            - ähnliche Werte = mehrere Sportarten passen ähnlich gut
            - größere Abstände = deutlichere Priorisierung
            """
        )

    st.subheader("Empfehlungsdetails")
    display_df = top_10[
        [
            "sport_name",
            "sex",
            "avg_height",
            "avg_weight",
            "avg_age",
            "similarity_score",
            "match_level",
            "std_distance",
        ]
    ].rename(
        columns={
            "sport_name": "Sportart",
            "sex": "Geschlecht",
            "avg_height": "Ø Größe (cm)",
            "avg_weight": "Ø Gewicht (kg)",
            "avg_age": "Ø Alter",
            "similarity_score": "Similarity Score",
            "match_level": "Match Level",
            "std_distance": "Standardisierte Distanz",
        }
    )
    st.dataframe(display_df, use_container_width=True)


def show_medal_winners_page():
    st.title("Alle Medaillengewinner Olympia 1904 - 2016")
    st.markdown(
        "Hier kannst du Medaillengewinner nach Land, Jahr, Sportart und Disziplin filtern."
    )

    st.info(
        "Die KPI-Zahlen zählen einzigartige Medaillenentscheidungen pro Disziplin. "
        "Teammedaillen werden daher nur einmal gezählt."
    )

    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

    with filter_col1:
        countries = load_filter_countries()
        selected_country = st.selectbox("Land", countries)

    with filter_col2:
        years = load_filter_years(selected_country)
        selected_year = st.selectbox("Jahr", years)

    with filter_col3:
        sports = load_filter_sports(selected_country, selected_year)
        selected_sport = st.selectbox("Sportart", sports)

    with filter_col4:
        disciplines = load_filter_disciplines(selected_country, selected_year, selected_sport)
        selected_discipline = st.selectbox("Disziplin", disciplines)

    summary_df = load_filtered_medal_summary(
        selected_country,
        selected_year,
        selected_sport,
        selected_discipline,
    )

    top_countries_df = load_top_countries(
        selected_country,
        selected_year,
        selected_sport,
        selected_discipline,
    )

    gold = int(summary_df.loc[0, "gold_medals"])
    silver = int(summary_df.loc[0, "silver_medals"])
    bronze = int(summary_df.loc[0, "bronze_medals"])
    total = int(summary_df.loc[0, "total_medals"])

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Gold", gold)
    kpi2.metric("Silber", silver)
    kpi3.metric("Bronze", bronze)
    kpi4.metric("Gesamt", total)

    left_col, right_col = st.columns([1.0, 0.95])

    with left_col:
        st.subheader("Medaillenverteilung")
        st.pyplot(plot_medal_summary_chart(gold, silver, bronze), use_container_width=False)

    with right_col:
        st.subheader("Top 10 Länder")
        if top_countries_df.empty:
            st.warning("Keine Länderdaten für diese Filterkombination gefunden.")
        else:
            display_top_countries = top_countries_df.rename(
                columns={
                    "country": "Land",
                    "gold_medals": "Gold",
                    "silver_medals": "Silber",
                    "bronze_medals": "Bronze",
                    "total_medals": "Gesamt",
                }
            )
            st.dataframe(display_top_countries, use_container_width=True, hide_index=True)

    display_mode = st.radio(
        "Darstellung der Gewinnerliste",
        ["Athletenebene", "Medaillenentscheidung / Team-Ebene"],
        horizontal=True,
    )

    if display_mode == "Athletenebene":
        winners_df = load_filtered_winners(
            selected_country,
            selected_year,
            selected_sport,
            selected_discipline,
        )

        winners_df = apply_table_filters(winners_df)

        st.subheader("Gewinnerliste auf Athletenebene")
        st.write(f"Gefundene Einträge: **{len(winners_df)}**")

        if winners_df.empty:
            st.warning("Für diese Filterkombination wurden keine Gewinner gefunden.")
        else:
            st.dataframe(winners_df, use_container_width=True)
            csv = winners_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Athletenliste als CSV herunterladen",
                data=csv,
                file_name="olympia_gewinner_athleten.csv",
                mime="text/csv",
            )

    else:
        winner_events_df = load_filtered_winner_events(
            selected_country,
            selected_year,
            selected_sport,
            selected_discipline,
        )

        winner_events_df = apply_table_filters(winner_events_df)

        st.subheader("Gewinnerliste auf Medaillenentscheidungs-Ebene")
        st.write(f"Gefundene Einträge: **{len(winner_events_df)}**")

        if winner_events_df.empty:
            st.warning("Für diese Filterkombination wurden keine Einträge gefunden.")
        else:
            st.dataframe(winner_events_df, use_container_width=True)
            csv = winner_events_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Medaillenentscheidungen als CSV herunterladen",
                data=csv,
                file_name="olympia_medaillenentscheidungen.csv",
                mime="text/csv",
            )


view = st.radio(
    "Ansicht",
    ["Olympic Sports Recommender", "Alle Medaillengewinner Olympia 1904 - 2016"],
    horizontal=True,
    label_visibility="collapsed",
)

if view == "Olympic Sports Recommender":
    show_recommendation_page()
else:
    show_medal_winners_page()