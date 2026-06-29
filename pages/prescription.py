import streamlit as st
from utils.ocr import process_prescription
from utils.llm import explain_prescription
from utils.tts import generate_audio
from utils.db import get_drug_info, check_interactions, suggest_specialist
from utils.outbreak import log_disease
import os


def show(language="English"):
    st.header("💊 Prescription Explainer")

    if language == "বাংলা":
        st.markdown("আপনার প্রেসক্রিপশন আপলোড করুন — আমরা বাংলায় ব্যাখ্যা করব।")
    else:
        st.markdown("Upload your prescription — we'll explain it in simple language.")

    uploaded_file = st.file_uploader(
        "Upload Prescription (Image or PDF)",
        type=["jpg", "jpeg", "png", "pdf"]
    )

    # Manual text input fallback
    st.markdown("**Or paste prescription text directly:**")
    manual_text = st.text_area("Paste prescription text here", height=150)

    if st.button("🔍 Analyze Prescription", type="primary"):
        raw_text = ""

        if uploaded_file:
            file_bytes = uploaded_file.read()
            file_type = "pdf" if uploaded_file.name.endswith(".pdf") else "image"

            with st.spinner("Reading prescription... / প্রেসক্রিপশন পড়া হচ্ছে..."):
                result = process_prescription(file_bytes, file_type)
                raw_text = result["raw_text"]

            with st.expander("📄 Extracted Text (Raw OCR)"):
                st.text(raw_text)

        elif manual_text.strip():
            raw_text = manual_text.strip()
        else:
            st.warning("Please upload a file or paste prescription text.")
            return

        # Get drug info from DB
        from utils.ocr import extract_drug_names
        drug_names = extract_drug_names(raw_text)
        drug_info_list = [get_drug_info(d) for d in drug_names]
        drug_info_list = [d for d in drug_info_list if d]

        # Check interactions
        interactions = check_interactions(drug_names)

        with st.spinner("Analyzing with AI... / AI বিশ্লেষণ চলছে..."):
            explanation = explain_prescription(raw_text, drug_info_list, interactions)

        # Display results
        st.markdown("---")

        # Condition
        condition = explanation.get("condition", {})
        if language == "বাংলা":
            st.subheader(f"🏥 রোগ: {condition.get('name_bn', 'অজানা')}")
            st.info(condition.get("explanation_bn", ""))
        else:
            st.subheader(f"🏥 Condition: {condition.get('name_en', 'Unknown')}")
            st.info(condition.get("explanation_en", ""))

        # Log disease anonymously
        if condition.get("name_en"):
            log_disease(condition["name_en"], "Dhaka")

        # Medicines
        medicines = explanation.get("medicines", [])
        if medicines:
            st.markdown("### 💊 Medicines / ওষুধ")
            for med in medicines:
                with st.container():
                    st.markdown(f"""
                    <div class="medicine-card">
                        <b>💊 {med.get('brand', '')} ({med.get('generic', '')})</b><br>
                        {'<b>উদ্দেশ্য:</b> ' + med.get('purpose_bn', '') if language == 'বাংলা'
                          else '<b>Purpose:</b> ' + med.get('purpose_en', '')}<br>
                        <b>Dose:</b> {med.get('dose', '')}<br>
                        {'<b>💰 সাশ্রয়ী বিকল্প:</b> ' + str(med.get('cheaper_alternative', 'N/A'))
                          if med.get('cheaper_alternative')
                          else ''}
                    </div>
                    """, unsafe_allow_html=True)

        # Interactions
        if interactions:
            st.markdown("### ⚠️ Drug Interactions / ওষুধের মিথস্ক্রিয়া")
            for interaction in interactions:
                severity = interaction.get("severity", "")
                color = "🔴" if severity == "severe" else "🟡"
                st.markdown(f"""
                <div class="warning-box">
                    {color} <b>{interaction.get('drugs', '')}</b> — {severity.upper()}<br>
                    {interaction.get('message_bn', '') if language == 'বাংলা'
                      else interaction.get('message_en', '')}
                </div>
                """, unsafe_allow_html=True)

        # Red flags
        red_flags = explanation.get("red_flags", [])
        if red_flags:
            st.markdown("### 🚨 Warning Signs / সতর্কতার লক্ষণ")
            st.markdown(f"""
            <div class="danger-box">
                {'<br>'.join(['⚠️ ' + flag for flag in red_flags])}
            </div>
            """, unsafe_allow_html=True)

        # Lifestyle tips
        tips = explanation.get("lifestyle_tips", [])
        if tips:
            st.markdown("### 🌿 Lifestyle Tips / জীবনধারা পরামর্শ")
            for tip in tips:
                st.markdown(f"✅ {tip}")

        # Specialist referral
        specialist = explanation.get("specialist", {})
        if specialist and specialist.get("en"):
            st.markdown(f"""
            <div class="success-box">
                👨‍⚕️ <b>{'বিশেষজ্ঞ পরামর্শ' if language == 'বাংলা' else 'Specialist Referral'}:</b>
                {specialist.get('bn', '') if language == 'বাংলা' else specialist.get('en', '')}
            </div>
            """, unsafe_allow_html=True)

        # Voice output
        st.markdown("### 🔊 Bengali Voice Explanation / বাংলা কণ্ঠস্বর")
        bengali_text = condition.get("explanation_bn", "")
        if bengali_text:
            with st.spinner("Generating audio..."):
                audio_path = generate_audio(bengali_text)
            if audio_path:
                with open(audio_path, "rb") as f:
                    st.audio(f.read(), format="audio/mp3")
                os.unlink(audio_path)