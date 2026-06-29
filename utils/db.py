import sqlite3
import os

DB_PATH = os.path.join("data", "drugs.db")
OUTBREAK_DB_PATH = os.path.join("data", "outbreak.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS drugs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand_name TEXT NOT NULL,
            generic_name TEXT NOT NULL,
            drug_class TEXT,
            manufacturer TEXT,
            typical_dose TEXT,
            price_bdt REAL,
            cheaper_alternative TEXT,
            barcode TEXT
        );

        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drug_a TEXT NOT NULL,
            drug_b TEXT NOT NULL,
            severity TEXT,
            description_en TEXT,
            description_bn TEXT
        );
    """)

    conn.commit()
    conn.close()
    print("✅ Drug database initialized")


def seed_drugs():
    drugs = [
        ("Napa", "Paracetamol", "Analgesic", "Beximco Pharma", "500mg 1-2 tabs every 6hrs", 1.5, "Ace 500mg - ৳1/tab", None),
        ("Ace", "Paracetamol", "Analgesic", "Square Pharma", "500mg 1-2 tabs every 6hrs", 1.0, None, None),
        ("Napa Extra", "Paracetamol+Caffeine", "Analgesic", "Beximco Pharma", "1 tab every 6hrs", 2.0, "Napa 500mg - ৳1.5/tab", None),
        ("Seclo", "Omeprazole", "Antacid", "Square Pharma", "20mg once daily", 3.5, "Omidon 20mg - ৳2/tab", None),
        ("Pantop", "Pantoprazole", "Antacid", "Opsonin Pharma", "40mg once daily", 5.0, "Seclo 20mg - ৳3.5/tab", None),
        ("Moxacil", "Amoxicillin", "Antibiotic", "Square Pharma", "500mg 3x daily", 6.0, "Amoxil 500mg - ৳4/tab", None),
        ("Azithro", "Azithromycin", "Antibiotic", "Beximco Pharma", "500mg once daily 3 days", 15.0, "Zimax 500mg - ৳12/tab", None),
        ("Glucophage", "Metformin", "Antidiabetic", "Beximco Pharma", "500mg 2x daily", 8.0, "Metformin 500mg (Opsonin) - ৳2/tab", None),
        ("Amdocal", "Amlodipine", "Antihypertensive", "Square Pharma", "5mg once daily", 4.0, "Norvasc 5mg - ৳3/tab", None),
        ("Losartic", "Losartan", "Antihypertensive", "Opsonin Pharma", "50mg once daily", 6.0, "Losar 50mg - ৳4/tab", None),
        ("Ceevit", "Vitamin C", "Vitamin", "Square Pharma", "500mg once daily", 2.0, "Ascorbic Acid 500mg - ৳1/tab", None),
        ("Zincovit", "Zinc+Multivitamin", "Vitamin", "Opsonin Pharma", "1 tab daily", 5.0, "Zinc 20mg - ৳2/tab", None),
        ("Atova", "Atorvastatin", "Statin", "Square Pharma", "10mg once daily at night", 10.0, "Lipitor 10mg - ৳8/tab", None),
        ("Clopid", "Clopidogrel", "Antiplatelet", "Beximco Pharma", "75mg once daily", 8.0, "Plavix 75mg - ৳6/tab", None),
        ("Fexo", "Fexofenadine", "Antihistamine", "Square Pharma", "120mg once daily", 7.0, "Allegra 120mg - ৳5/tab", None),
        ("Montek", "Montelukast", "Antiasthmatic", "Opsonin Pharma", "10mg once daily", 12.0, "Singulair 10mg - ৳10/tab", None),
        ("Ciproflox", "Ciprofloxacin", "Antibiotic", "Square Pharma", "500mg 2x daily", 8.0, "Cipro 500mg - ৳6/tab", None),
        ("Metronid", "Metronidazole", "Antibiotic", "Beximco Pharma", "400mg 3x daily", 3.0, "Flagyl 400mg - ৳2/tab", None),
        ("Insulin Mixtard", "Insulin", "Antidiabetic", "Novo Nordisk", "As prescribed", 350.0, "Humulin 70/30 - ৳300/vial", None),
        ("Digoxin", "Digoxin", "Cardiac", "Square Pharma", "0.25mg once daily", 5.0, None, None),
        ("Lithium Carbonate", "Lithium", "Psychiatric", "Opsonin Pharma", "300mg 3x daily", 8.0, None, None),
        ("Isoniazid", "Isoniazid", "Anti-TB", "Beximco Pharma", "300mg once daily", 4.0, None, None),
        ("Ranitin", "Ranitidine", "Antacid", "Square Pharma", "150mg 2x daily", 2.5, "Seclo 20mg - ৳3.5/tab", None),
        ("Telmisartan", "Telmisartan", "Antihypertensive", "Opsonin Pharma", "40mg once daily", 7.0, "Losartic 50mg - ৳6/tab", None),
        ("Orofer", "Iron Supplement", "Supplement", "Square Pharma", "1 tab daily", 6.0, "FeSO4 200mg - ৳2/tab", None),
    ]

    interactions = [
        ("Warfarin", "Aspirin", "severe",
         "Increased risk of bleeding",
         "রক্তক্ষরণের ঝুঁকি বাড়ে"),
        ("Metformin", "Alcohol", "moderate",
         "Risk of lactic acidosis",
         "ল্যাকটিক অ্যাসিডোসিসের ঝুঁকি"),
        ("Digoxin", "Amiodarone", "severe",
         "Digoxin toxicity risk increases",
         "ডিগোক্সিন বিষক্রিয়ার ঝুঁকি বাড়ে"),
        ("Ciprofloxacin", "Antacid", "moderate",
         "Antacids reduce ciprofloxacin absorption",
         "অ্যান্টাসিড সিপ্রোফ্লক্সাসিনের শোষণ কমায়"),
        ("Lithium", "Ibuprofen", "severe",
         "NSAIDs increase lithium toxicity",
         "NSAIDs লিথিয়াম বিষক্রিয়া বাড়ায়"),
        ("Amlodipine", "Simvastatin", "moderate",
         "Increased risk of muscle damage",
         "মাংসপেশির ক্ষতির ঝুঁকি বাড়ে"),
    ]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM drugs")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO drugs (brand_name, generic_name, drug_class,
            manufacturer, typical_dose, price_bdt, cheaper_alternative, barcode)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, drugs)
        print(f"✅ {len(drugs)} drugs seeded")

    cursor.execute("SELECT COUNT(*) FROM interactions")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO interactions
            (drug_a, drug_b, severity, description_en, description_bn)
            VALUES (?, ?, ?, ?, ?)
        """, interactions)
        print(f"✅ {len(interactions)} interactions seeded")

    conn.commit()
    conn.close()


def get_drug_info(brand_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM drugs
        WHERE LOWER(brand_name) = LOWER(?)
        OR LOWER(generic_name) = LOWER(?)
    """, (brand_name, brand_name))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "brand_name": row[1],
            "generic_name": row[2],
            "drug_class": row[3],
            "manufacturer": row[4],
            "typical_dose": row[5],
            "price_bdt": row[6],
            "cheaper_alternative": row[7],
            "barcode": row[8]
        }
    return None


def check_interactions(drug_list):
    warnings = []
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for i, drug_a in enumerate(drug_list):
        for drug_b in drug_list[i+1:]:
            cursor.execute("""
                SELECT * FROM interactions
                WHERE (LOWER(drug_a) = LOWER(?) AND LOWER(drug_b) = LOWER(?))
                OR (LOWER(drug_a) = LOWER(?) AND LOWER(drug_b) = LOWER(?))
            """, (drug_a, drug_b, drug_b, drug_a))
            result = cursor.fetchone()
            if result and result[3] in ["moderate", "severe"]:
                warnings.append({
                    "drugs": f"{drug_a} + {drug_b}",
                    "severity": result[3],
                    "message_en": result[4],
                    "message_bn": result[5]
                })
    conn.close()
    return warnings


def verify_barcode(barcode):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT brand_name, generic_name, manufacturer FROM drugs WHERE barcode = ?", (barcode,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            "status": "verified",
            "message_en": f"✅ DGDA Verified — {result[0]} by {result[2]}",
            "message_bn": f"✅ এই ওষুধটি DGDA অনুমোদিত — {result[0]} ({result[2]})"
        }
    return {
        "status": "unverified",
        "message_en": "⚠️ WARNING: Not found in DGDA records. May be counterfeit.",
        "message_bn": "⚠️ সতর্কতা: এই ওষুধটি DGDA তালিকায় নেই। নকল হতে পারে।"
    }


SPECIALIST_MAP = {
    "insulin": ("এন্ডোক্রিনোলজিস্ট", "Endocrinologist"),
    "digoxin": ("কার্ডিওলজিস্ট", "Cardiologist"),
    "isoniazid": ("বক্ষব্যাধি বিশেষজ্ঞ", "Pulmonologist (TB)"),
    "lithium": ("মনোরোগ বিশেষজ্ঞ", "Psychiatrist"),
    "chemotherapy": ("অনকোলজিস্ট", "Oncologist"),
    "metformin": ("এন্ডোক্রিনোলজিস্ট", "Endocrinologist"),
    "atorvastatin": ("কার্ডিওলজিস্ট", "Cardiologist"),
}


def suggest_specialist(drug_list):
    for drug in drug_list:
        for keyword, specialists in SPECIALIST_MAP.items():
            if keyword in drug.lower():
                return {
                    "bn": f"এই ওষুধের জন্য {specialists[0]}-এর পরামর্শ নিন",
                    "en": f"Consult a {specialists[1]} for this medication"
                }
    return None


if __name__ == "__main__":
    init_db()
    seed_drugs()
    print("✅ Database ready!")

    # Test
    drug = get_drug_info("Napa")
    print(f"Drug lookup: {drug}")

    interactions = check_interactions(["Digoxin", "Amiodarone"])
    print(f"Interactions: {interactions}")