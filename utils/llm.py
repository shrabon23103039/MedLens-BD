from google import genai
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def explain_prescription(raw_text, drug_info_list=[], interactions=[]):
    """Use Gemini to explain prescription in Bengali and English"""
    
    drug_context = ""
    if drug_info_list:
        drug_context = "Known drug information:\n"
        for drug in drug_info_list:
            if drug:
                drug_context += f"- {drug['brand_name']} ({drug['generic_name']}): {drug['typical_dose']}, ৳{drug['price_bdt']}/tab\n"

    prompt = f"""
    You are a friendly medical assistant for patients in Bangladesh with low health literacy.
    
    Prescription text:
    {raw_text}
    
    {drug_context}
    
    Analyze this prescription and respond ONLY with a valid JSON object in this exact format:
    {{
        "condition": {{
            "name_en": "condition name in English",
            "name_bn": "condition name in Bengali",
            "explanation_en": "simple 2-3 sentence explanation in English",
            "explanation_bn": "simple 2-3 sentence explanation in Bengali at 8th grade level"
        }},
        "medicines": [
            {{
                "brand": "brand name",
                "generic": "generic name",
                "purpose_en": "what this medicine does in 1 sentence",
                "purpose_bn": "same in Bengali",
                "dose": "dosage instructions",
                "price_bdt": 0.0,
                "cheaper_alternative": "cheaper option or null"
            }}
        ],
        "interactions": [
            {{
                "drugs": "Drug A + Drug B",
                "severity": "mild/moderate/severe",
                "message_en": "warning in English",
                "message_bn": "warning in Bengali"
            }}
        ],
        "red_flags": [
            "symptom to watch in English",
            "symptom to watch in Bengali"
        ],
        "lifestyle_tips": [
            "tip 1 in Bengali",
            "tip 2 in Bengali",
            "tip 3 in Bengali"
        ],
        "see_doctor_if": "when to see doctor in Bengali",
        "specialist": {{
            "en": "specialist type or null",
            "bn": "specialist in Bengali or null"
        }}
    }}
    
    Rules:
    - Bengali explanations must be simple, 8th grade reading level
    - Never use medical jargon without explaining it
    - If condition is unclear, make best guess from medicines
    - Return ONLY the JSON, no extra text, no markdown backticks
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=prompt
        )

        raw = response.text.strip()
        
        # Clean markdown if present
        raw = re.sub(r'^```json\s*', '', raw)
        raw = re.sub(r'^```\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
        raw = raw.strip()

        result = json.loads(raw)

        # Inject interaction data from DB if available
        if interactions:
            result["interactions"] = interactions

        return result

    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print(f"Raw response was:\n{raw}")
        return get_fallback_response()
    except Exception as e:
        print(f"LLM error: {e}")
        return get_fallback_response()


def explain_lab_report(raw_text):
    """Explain lab report values in simple Bengali and English"""

    LAB_RANGES = {
        "hemoglobin": {"min": 12.0, "max": 17.5, "unit": "g/dL",
                       "low_bn": "রক্তশূন্যতার লক্ষণ থাকতে পারে",
                       "high_bn": "পলিসাইথেমিয়ার লক্ষণ হতে পারে"},
        "wbc": {"min": 4000, "max": 11000, "unit": "cells/μL",
                "low_bn": "রোগ প্রতিরোধ ক্ষমতা কম থাকতে পারে",
                "high_bn": "সংক্রমণের লক্ষণ হতে পারে"},
        "glucose_fasting": {"min": 70, "max": 100, "unit": "mg/dL",
                            "high_bn": "ডায়াবেটিসের ঝুঁকি আছে"},
        "cholesterol": {"min": 0, "max": 200, "unit": "mg/dL",
                        "high_bn": "হৃদরোগের ঝুঁকি বাড়তে পারে"},
        "creatinine": {"min": 0.6, "max": 1.2, "unit": "mg/dL",
                       "high_bn": "কিডনির সমস্যা থাকতে পারে"},
        "sgpt": {"min": 7, "max": 56, "unit": "U/L",
                 "high_bn": "লিভারের সমস্যা থাকতে পারে"},
    }

    prompt = f"""
    You are a medical assistant explaining lab results to a Bangladeshi patient.
    
    Lab report text:
    {raw_text}
    
    Analyze each lab value and respond ONLY with valid JSON in this format:
    {{
        "summary_en": "overall 2 sentence summary in English",
        "summary_bn": "overall 2 sentence summary in Bengali",
        "values": [
            {{
                "test_name": "test name",
                "value": "patient value with unit",
                "normal_range": "normal range",
                "status": "normal/low/high",
                "explanation_en": "what this means in simple English",
                "explanation_bn": "what this means in simple Bengali"
            }}
        ],
        "urgent": true/false,
        "see_doctor": "when to see doctor in Bengali"
    }}
    
    Return ONLY the JSON, no extra text, no markdown backticks.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=prompt
        )

        raw = response.text.strip()
        raw = re.sub(r'^```json\s*', '', raw)
        raw = re.sub(r'^```\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
        raw = raw.strip()

        return json.loads(raw)

    except Exception as e:
        print(f"Lab report error: {e}")
        return {
            "summary_en": "Could not analyze report. Please try again.",
            "summary_bn": "রিপোর্ট বিশ্লেষণ করা যায়নি। আবার চেষ্টা করুন।",
            "values": [],
            "urgent": False,
            "see_doctor": "আপনার ডাক্তারের সাথে পরামর্শ করুন।"
        }


def get_fallback_response():
    """Return safe fallback if LLM fails"""
    return {
        "condition": {
            "name_en": "Unknown",
            "name_bn": "অজানা",
            "explanation_en": "Could not analyze prescription. Please try again.",
            "explanation_bn": "প্রেসক্রিপশন বিশ্লেষণ করা যায়নি। আবার চেষ্টা করুন।"
        },
        "medicines": [],
        "interactions": [],
        "red_flags": [],
        "lifestyle_tips": [],
        "see_doctor_if": "যেকোনো সমস্যায় ডাক্তারের সাথে পরামর্শ করুন।",
        "specialist": {"en": None, "bn": None}
    }


if __name__ == "__main__":
    sample_text = """
    Patient: Mohammad Ali, Age: 45
    Diagnosis: Type 2 Diabetes + Hypertension
    
    Rx:
    1. Glucophage 500mg - 0+1+1
    2. Amdocal 5mg - 1+0+0
    3. Seclo 20mg - 1+0+1
    """

    print("Testing LLM explanation engine...")
    result = explain_prescription(sample_text)

    print("\n✅ Condition:", result["condition"]["name_en"])
    print("✅ Bengali:", result["condition"]["explanation_bn"])
    print("✅ Medicines found:", len(result["medicines"]))
    print("✅ Lifestyle tips:", result["lifestyle_tips"])