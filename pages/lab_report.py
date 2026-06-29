import streamlit as st
from utils.ocr import process_prescription
from utils.llm import explain_lab_report


def show(language="English"):
    st.header("🧪 Lab Report Explainer")

    if language == "বাংলা":
        st.markdown("আপনার ল্যাব রিপোর্ট আপলোড করুন — আমরা সহজ ভাষায় ব্যাখ্যা করব।")
    else:
        st.markdown("Upload your lab report — we'll explain every value in simple language.")

    uploaded_file = st.file_uploader(
        "Upload Lab Report (Image or PDF)",
        type=["jpg", "jpeg", "png", "pdf"]
    )

    manual_text = st.text_area("Or paste lab report text here", height=150)

    if st.button("🔍 Analyze Lab Report", type="primary"):
        raw_text = ""

        if uploaded_file:
            file_bytes = uploaded_file.read()
            file_type = "pdf" if uploaded_file.name.endswith(".pdf") else "image"
            with st.spinner("Reading report..."):
                result = process_prescription(file_bytes, file_type)
                raw_text = result["raw_text"]
            with st.expander("📄 Extracted Text"):
                st.text(raw_text)

        elif manual_text.strip():
            raw_text = manual_text.strip()
        else:
            st.warning("Please upload a file or paste report text.")
            return

        with st.spinner("Analyzing with AI..."):
            explanation = explain_lab_report(raw_text)

        st.markdown("---")

        # Summary
        if language == "বাংলা":
            st.subheader("📋 সারসংক্ষেপ")
            st.info(explanation.get("summary_bn", ""))
        else:
            st.subheader("📋 Summary")
            st.info(explanation.get("summary_en", ""))

        # Urgent warning
        if explanation.get("urgent"):
            st.error("🚨 Some values need immediate medical attention!")

        # Lab values
        values = explanation.get("values", [])
        if values:
            st.markdown("### 📊 Lab Values / পরীক্ষার ফলাফল")
            for val in values:
                status = val.get("status", "normal")
                if status == "high":
                    color = "🔴"
                    box_class = "danger-box"
                elif status == "low":
                    color = "🟡"
                    box_class = "warning-box"
                else:
                    color = "🟢"
                    box_class = "success-box"

                explanation_text = (
                    val.get("explanation_bn", "")
                    if language == "বাংলা"
                    else val.get("explanation_en", "")
                )

                st.markdown(f"""
                <div class="{box_class}">
                    {color} <b>{val.get('test_name', '')}</b>:
                    {val.get('value', '')}
                    (Normal: {val.get('normal_range', '')})<br>
                    <small>{explanation_text}</small>
                </div>
                """, unsafe_allow_html=True)

        # See doctor
        see_doctor = explanation.get("see_doctor", "")
        if see_doctor:
            st.markdown(f"""
            <div class="info-box">
                👨‍⚕️ <b>{'ডাক্তার দেখান যদি' if language == 'বাংলা'
                  else 'See a doctor if'}:</b><br>
                {see_doctor}
            </div>
            """, unsafe_allow_html=True)