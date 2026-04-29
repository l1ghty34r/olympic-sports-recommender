import pandas as pd


def get_recommendation_profiles(engine):
    query = """
    SELECT
        s.sport_name,
        a.sex,
        ROUND(AVG(a.height)::numeric, 2) AS avg_height,
        ROUND(AVG(a.weight)::numeric, 2) AS avg_weight,
        ROUND(AVG(r.age)::numeric, 2) AS avg_age,
        COUNT(*) AS medal_winners
    FROM result r
    JOIN athlete a ON r.athlete_id = a.athlete_id
    JOIN event e ON r.event_id = e.event_id
    JOIN sport s ON e.sport_id = s.sport_id
    WHERE r.medal IS NOT NULL
      AND a.height IS NOT NULL
      AND a.weight IS NOT NULL
      AND r.age IS NOT NULL
    GROUP BY s.sport_name, a.sex
    HAVING COUNT(*) >= 20
    ORDER BY medal_winners DESC;
    """
    df = pd.read_sql(query, engine)

    df["avg_height"] = (df["avg_height"] / 10).round(2)
    df["avg_weight"] = (df["avg_weight"] / 10).round(2)

    return df


def _build_filter_conditions(
    country_name="Alle",
    year="Alle",
    sport_name="Alle",
    discipline_name="Alle",
):
    conditions = ["r.medal IS NOT NULL"]
    params = {}

    if country_name != "Alle":
        conditions.append("c.country = %(country_name)s")
        params["country_name"] = country_name

    if year != "Alle":
        conditions.append("r.year = %(year)s")
        params["year"] = int(year)

    if sport_name != "Alle":
        conditions.append("s.sport_name = %(sport_name)s")
        params["sport_name"] = sport_name

    if discipline_name != "Alle":
        conditions.append("e.event_name = %(discipline_name)s")
        params["discipline_name"] = discipline_name

    where_clause = " AND ".join(conditions)
    return where_clause, params


def get_filter_countries(engine):
    query = """
    SELECT DISTINCT c.country
    FROM result r
    JOIN country c ON r.noc = c.noc
    WHERE r.medal IS NOT NULL
    ORDER BY c.country;
    """
    df = pd.read_sql(query, engine)
    return ["Alle"] + df["country"].tolist()


def get_filter_years(engine, country_name="Alle"):
    where_clause = ["r.medal IS NOT NULL"]
    params = {}

    if country_name != "Alle":
        where_clause.append("c.country = %(country_name)s")
        params["country_name"] = country_name

    query = f"""
    SELECT DISTINCT r.year
    FROM result r
    JOIN country c ON r.noc = c.noc
    WHERE {' AND '.join(where_clause)}
    ORDER BY r.year;
    """
    df = pd.read_sql(query, engine, params=params)
    years = df["year"].astype(str).tolist()
    return ["Alle"] + years


def get_filter_sports(engine, country_name="Alle", year="Alle"):
    where_clause = ["r.medal IS NOT NULL"]
    params = {}

    if country_name != "Alle":
        where_clause.append("c.country = %(country_name)s")
        params["country_name"] = country_name

    if year != "Alle":
        where_clause.append("r.year = %(year)s")
        params["year"] = int(year)

    query = f"""
    SELECT DISTINCT s.sport_name
    FROM result r
    JOIN country c ON r.noc = c.noc
    JOIN event e ON r.event_id = e.event_id
    JOIN sport s ON e.sport_id = s.sport_id
    WHERE {' AND '.join(where_clause)}
    ORDER BY s.sport_name;
    """
    df = pd.read_sql(query, engine, params=params)
    return ["Alle"] + df["sport_name"].tolist()


def get_filter_disciplines(engine, country_name="Alle", year="Alle", sport_name="Alle"):
    where_clause = ["r.medal IS NOT NULL"]
    params = {}

    if country_name != "Alle":
        where_clause.append("c.country = %(country_name)s")
        params["country_name"] = country_name

    if year != "Alle":
        where_clause.append("r.year = %(year)s")
        params["year"] = int(year)

    if sport_name != "Alle":
        where_clause.append("s.sport_name = %(sport_name)s")
        params["sport_name"] = sport_name

    query = f"""
    SELECT DISTINCT e.event_name AS discipline_name
    FROM result r
    JOIN country c ON r.noc = c.noc
    JOIN event e ON r.event_id = e.event_id
    JOIN sport s ON e.sport_id = s.sport_id
    WHERE {' AND '.join(where_clause)}
    ORDER BY discipline_name;
    """
    df = pd.read_sql(query, engine, params=params)
    return ["Alle"] + df["discipline_name"].tolist()


def get_filtered_medal_summary(
    engine,
    country_name="Alle",
    year="Alle",
    sport_name="Alle",
    discipline_name="Alle",
):
    where_clause, params = _build_filter_conditions(
        country_name=country_name,
        year=year,
        sport_name=sport_name,
        discipline_name=discipline_name,
    )

    query = f"""
    WITH unique_medals AS (
        SELECT DISTINCT
            r.year,
            r.noc,
            r.event_id,
            r.medal
        FROM result r
        JOIN country c ON r.noc = c.noc
        JOIN event e ON r.event_id = e.event_id
        JOIN sport s ON e.sport_id = s.sport_id
        WHERE {where_clause}
    )
    SELECT
        COUNT(*) FILTER (WHERE medal = 'Gold') AS gold_medals,
        COUNT(*) FILTER (WHERE medal = 'Silver') AS silver_medals,
        COUNT(*) FILTER (WHERE medal = 'Bronze') AS bronze_medals,
        COUNT(*) AS total_medals
    FROM unique_medals;
    """

    df = pd.read_sql(query, engine, params=params)

    for col in ["gold_medals", "silver_medals", "bronze_medals", "total_medals"]:
        df[col] = df[col].fillna(0).astype(int)

    return df


def get_top_countries_by_filters(
    engine,
    country_name="Alle",
    year="Alle",
    sport_name="Alle",
    discipline_name="Alle",
):
    where_clause, params = _build_filter_conditions(
        country_name=country_name,
        year=year,
        sport_name=sport_name,
        discipline_name=discipline_name,
    )

    query = f"""
    WITH unique_medals AS (
        SELECT DISTINCT
            r.year,
            r.noc,
            r.event_id,
            r.medal
        FROM result r
        JOIN country c ON r.noc = c.noc
        JOIN event e ON r.event_id = e.event_id
        JOIN sport s ON e.sport_id = s.sport_id
        WHERE {where_clause}
    )
    SELECT
        c.country,
        COUNT(*) FILTER (WHERE um.medal = 'Gold') AS gold_medals,
        COUNT(*) FILTER (WHERE um.medal = 'Silver') AS silver_medals,
        COUNT(*) FILTER (WHERE um.medal = 'Bronze') AS bronze_medals,
        COUNT(*) AS total_medals
    FROM unique_medals um
    JOIN country c ON um.noc = c.noc
    GROUP BY c.country
    ORDER BY
        gold_medals DESC,
        silver_medals DESC,
        bronze_medals DESC,
        c.country ASC
    LIMIT 10;
    """

    df = pd.read_sql(query, engine, params=params)

    for col in ["gold_medals", "silver_medals", "bronze_medals", "total_medals"]:
        if col in df.columns:
            df[col] = df[col].fillna(0).astype(int)

    return df


def get_filtered_winners(
    engine,
    country_name="Alle",
    year="Alle",
    sport_name="Alle",
    discipline_name="Alle",
):
    where_clause, params = _build_filter_conditions(
        country_name=country_name,
        year=year,
        sport_name=sport_name,
        discipline_name=discipline_name,
    )

    query = f"""
    SELECT
        r.year,
        c.country,
        s.sport_name,
        e.event_name AS discipline,
        a.name AS athlete_name,
        a.sex,
        r.age,
        r.medal
    FROM result r
    JOIN country c ON r.noc = c.noc
    JOIN event e ON r.event_id = e.event_id
    JOIN sport s ON e.sport_id = s.sport_id
    JOIN athlete a ON r.athlete_id = a.athlete_id
    WHERE {where_clause}
    ORDER BY
        r.year DESC,
        c.country,
        s.sport_name,
        e.event_name,
        CASE
            WHEN r.medal = 'Gold' THEN 1
            WHEN r.medal = 'Silver' THEN 2
            WHEN r.medal = 'Bronze' THEN 3
            ELSE 4
        END,
        a.name;
    """
    return pd.read_sql(query, engine, params=params)


def get_filtered_winner_events(
    engine,
    country_name="Alle",
    year="Alle",
    sport_name="Alle",
    discipline_name="Alle",
):
    where_clause, params = _build_filter_conditions(
        country_name=country_name,
        year=year,
        sport_name=sport_name,
        discipline_name=discipline_name,
    )

    query = f"""
    WITH unique_medal_events AS (
        SELECT DISTINCT
            r.year,
            r.noc,
            r.event_id,
            r.medal
        FROM result r
        JOIN country c ON r.noc = c.noc
        JOIN event e ON r.event_id = e.event_id
        JOIN sport s ON e.sport_id = s.sport_id
        WHERE {where_clause}
    )
    SELECT
        ume.year,
        c.country,
        s.sport_name,
        e.event_name AS discipline,
        ume.medal
    FROM unique_medal_events ume
    JOIN country c ON ume.noc = c.noc
    JOIN event e ON ume.event_id = e.event_id
    JOIN sport s ON e.sport_id = s.sport_id
    ORDER BY
        ume.year DESC,
        c.country,
        s.sport_name,
        e.event_name,
        CASE
            WHEN ume.medal = 'Gold' THEN 1
            WHEN ume.medal = 'Silver' THEN 2
            WHEN ume.medal = 'Bronze' THEN 3
            ELSE 4
        END;
    """
    return pd.read_sql(query, engine, params=params)