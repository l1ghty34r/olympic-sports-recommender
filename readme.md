# 🏅 Olympic Sports Recommender & Data Analytics Dashboard

## 🚀 Live Demo
👉 https://olympic-sports-recommender.streamlit.app  
*(Interactive Olympic Sports Recommender & Analytics Dashboard)*

---

## 🧠 Overview

This project is an interactive data application that combines a **sports recommender system** with an **Olympic analytics dashboard**.

It allows users to:
- get personalized sport recommendations based on physical attributes  
- explore historical Olympic medal data  
- analyze performance trends across countries, sports, and years  

---

## 🧠 Features

### 🔹 Sports Recommender
- Input: height, weight, age, gender  
- Output: top matching Olympic sports  
- Similarity-based scoring system  
- Top 10 recommendations with visualization  

### 🔹 Olympic Analytics Dashboard
- Filter by country, year, sport, discipline  
- Medal distribution (Gold / Silver / Bronze)  
- KPI overview (total medals)  
- Top countries ranking  
- Interactive charts  

---

## 🏗️ Tech Stack

- Python (pandas, numpy)
- PostgreSQL (Neon)
- SQLAlchemy
- Streamlit
- Matplotlib

---

## 📊 Screenshots

### Sports Recommender
![Recommender](images/recommender.png)

### Analytics Dashboard
![Dashboard](images/dashboard.png)

---

## ⚙️ Setup

### 1. Clone repository
git clone https://github.com/l1ghty34r/olympic-sports-recommender.git  
cd olympic-sports-recommender  

### 2. Install dependencies
pip install -r requirements.txt  

### 3. Set environment variables
Create a `.env` file in the project root:

DATABASE_URL=your_neon_connection_string  

### 4. Run the app
streamlit run app.py  

---

## 📌 Key Learnings

- Built an end-to-end data application (database → backend → frontend)  
- Designed and queried relational databases using SQL  
- Implemented a rule-based recommendation system  
- Developed interactive dashboards for data exploration  

---

## 🔮 Future Improvements

- Machine learning-based recommender  
- Advanced analytics (trend analysis, forecasting)  
- UI/UX improvements
