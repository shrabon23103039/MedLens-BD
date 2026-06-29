import streamlit as st
from utils.barcode import check_medicine


def show(language="English"):
    st.header("🔍 Counterfeit Medicine Detector")

    if language == "বাংলা":
        st.markdown("আপনার ওষুধের বাক্স বা স্ট্রিপের ছবি তুলুন — আমরা যাচাই করব।")
    else:
        st.markdown("Upload a photo of your medicine box or strip — we'll verify if it's genuine.")

    st.info("📸 Tip: Make sure the barcode is clearly visible and well-lit.")

    uploaded_file = st.file_uploader(
        "Upload Medicine Photo",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Medicine Photo", width=300)

        if st.button("🔍 Verify Medicine", type="primary"):
            file_bytes = uploaded_file.read()

            with st.spinner("Scanning barcode..."):
                result = check_medicine(file_bytes)

            st.markdown("---")
            status = result.get("status", "")

            if status == "verified":
                st.markdown(f"""
                <div class="success-box">
                    <h3>✅ {'যাচাইকৃত ওষুধ' if language == 'বাংলা' else 'Verified Medicine'}</h3>
                    {result.get('message_bn', '') if language == 'বাংলা'
                      else result.get('message_en', '')}
                </div>
                """, unsafe_allow_html=True)
                st.balloons()

            elif status == "unverified":
                st.markdown(f"""
                <div class="danger-box">
                    <h3>⚠️ {'সতর্কতা' if language == 'বাংলা' else 'Warning'}</h3>
                    {result.get('message_bn', '') if language == 'বাংলা'
                      else result.get('message_en', '')}
                    <br><br>
                    <b>{'বারকোড' if language == 'বাংলা' else 'Barcode'}:</b>
                    {result.get('barcode', 'N/A')}
                </div>
                """, unsafe_allow_html=True)

            else:
                st.markdown(f"""
                <div class="warning-box">
                    <h3>📷 {'বারকোড পাওয়া যায়নি' if language == 'বাংলা'
                      else 'No Barcode Found'}</h3>
                    {result.get('message_bn', '') if language == 'বাংলা'
                      else result.get('message_en', '')}
                </div>
                """, unsafe_allow_html=True)