# 🏐 Volleyball Team Analysis System

A comprehensive, data-driven web application built with **Python Django** for coaches and team managers to optimize team performance through granular match statistics and visual analytics.

## ✨ Core Features

*   **🏆 Match & Performance Tracking**: Log detailed match statistics including attack success, serve accuracy, and block efficiency.
*   **📊 Advanced Error Breakdown**: Granular tracking of **Attack Errors** and **Reception Errors** to identify technical gaps.
*   **🩺 Injury Tracker**: Integrated medical dashboard to manage player health and recovery status.
*   **📉 Dynamic Visual Analytics**: High-performance radar and bar charts powered by **Chart.js** for team-wide analysis and side-by-side player comparisons.
*   **📅 Automated Training Planner**: A logic-driven engine that generates personalized weekly drills based on individual player's statistical weaknesses.
*   **💎 Premium Aesthetic**: Modern **dark-themed glassmorphism** UI designed for high readability and a professional "command center" feel.

## 🚀 Quick Start

### 1. Installation
```bash
git clone <repository-url>
cd Volleyball-Analysis-System
pip install -r requirements.txt
```

### 2. Setup Database
```bash
python manage.py migrate
```

### 3. Seed Demo Data
Populate the system with 7 players, 5 matches, and training records:
```bash
python -X utf8 seed_data.py
python seed_training.py
```

### 4. Run Server
```bash
python manage.py runserver 8080
```
Access the application at: [http://127.0.0.1:8080/](http://127.0.0.1:8080/)
*   **Username**: `admin`
*   **Password**: `admin123`

## 📊 Scoring Methodology

The system uses a **weighted heuristic model** to calculate an objective performance score (0-100) for every match:
*   **40%**: Attack Success Rate
*   **30%**: Serve Accuracy
*   **30%**: Block Efficiency

## 🛠️ Technology Stack
*   **Backend**: Python, Django
*   **Frontend**: Vanilla HTML5/CSS3, Bootstrap 5
*   **Charts**: Chart.js
*   **Database**: SQLite (Default) / PostgreSQL Compatible

---
*Helping coaches turn data into victories.*
