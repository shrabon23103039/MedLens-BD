import sqlite3
import os
from datetime import datetime

OUTBREAK_DB_PATH = os.path.join("data", "outbreak.db")

DIVISION_COORDS = {
    "Dhaka": [23.8103, 90.4125],
    "Chittagong": [22.3569, 91.7832],
    "Rajshahi": [24.3745, 88.6042],
    "Khulna": [22.8456, 89.5403],
    "Sylhet": [24.8949, 91.8687],
    "Barisal": [22.7010, 90.3535],
    "Rangpur": [25.7439, 89.2752],
    "Mymensingh": [24.7471, 90.4203],
}


def init_outbreak_db():
    conn = sqlite3.connect(OUTBREAK_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS disease_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            condition TEXT NOT NULL,
            division TEXT NOT NULL,
            week TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Outbreak database initialized")


def current_week():
    return datetime.now().strftime("%Y-W%W")


def log_disease(condition, division):
    if division not in DIVISION_COORDS:
        return
    conn = sqlite3.connect(OUTBREAK_DB_PATH)
    conn.execute(
        "INSERT INTO disease_log (condition, division, week) VALUES (?, ?, ?)",
        (condition, division, current_week())
    )
    conn.commit()
    conn.close()


def get_division_counts(disease, week=None):
    if not week:
        week = current_week()
    conn = sqlite3.connect(OUTBREAK_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT division, COUNT(*) as count
        FROM disease_log
        WHERE LOWER(condition) LIKE LOWER(?)
        AND week = ?
        GROUP BY division
    """, (f"%{disease}%", week))
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}


def render_map(disease_filter="Dengue"):
    import folium
    m = folium.Map(location=[23.6850, 90.3563], zoom_start=7)
    data = get_division_counts(disease_filter)

    for division, coords in DIVISION_COORDS.items():
        count = data.get(division, 0)
        color = "red" if count > 5 else "orange" if count > 0 else "green"
        folium.CircleMarker(
            location=coords,
            radius=max(count * 2, 8),
            color=color,
            fill=True,
            fill_opacity=0.7,
            popup=f"{division}: {count} cases this week"
        ).add_to(m)

    return m


if __name__ == "__main__":
    init_outbreak_db()

    # Seed test data
    log_disease("Dengue", "Dhaka")
    log_disease("Dengue", "Dhaka")
    log_disease("Dengue", "Chittagong")
    log_disease("Typhoid", "Sylhet")
    log_disease("Typhoid", "Rajshahi")

    counts = get_division_counts("Dengue")
    print(f"✅ Dengue counts this week: {counts}")

    counts2 = get_division_counts("Typhoid")
    print(f"✅ Typhoid counts this week: {counts2}")