# Olympia Streamlit App

## Voraussetzungen

Folgende Software muss installiert sein:

* Python (empfohlen: Version 3.10 oder neuer)
* PostgreSQL

---

## Python Pakete installieren

Im Projektordner im Terminal ausführen:

```
pip install -r requirements.txt
```

---

## Datenbank erstellen

```
createdb -U postgres olympics
```

---

## SQL-Dump importieren

```
psql -U postgres -d olympics -f data/olympics_dump.sql
```

---

## Streamlit App starten

```
streamlit run app.py
```

---

## App öffnen

```
http://localhost:8501
```
