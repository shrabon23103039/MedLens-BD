import streamlit as st
from utils.outbreak import render_map, get_division_counts, current_week
from streamlit_folium import st_folium


def show(language="English"):
    st.header("🗺️ Disease Outbreak Map")

    if language == "বাংলা":
        st.markdown("বাংলাদেশের বিভিন্ন বিভাগে রোগের প্রাদুর্ভাব মানচিত্র।")
    else:
        st.markdown("Real-time disease surveillance map across Bangladesh divisions.")

    st.info("🔒 All data is fully anonymized. No personal information is stored.")

    # Disease filter
    disease_options = [
        "Dengue", "Typhoid", "Diarrhea",
        "Pneumonia", "Malaria", "Covid-19"
    ]

    col1, col2 = st.columns([2, 1])
    with col1:
        selected_disease = st.selectbox(
            "Select Disease / রোগ নির্বাচন করুন",
            disease_options
        )
    with col2:
        st.metric(
            label="Current Week",
            value=current_week()
        )

    # Render map
    with st.spinner("Loading map..."):
        m = render_map(selected_disease)
        st_folium(m, width=700, height=500)

    # Division counts table
    counts = get_division_counts(selected_disease)
    if counts:
        st.markdown("### 📊 Cases by Division This Week")
        col1, col2 = st.columns(2)
        items = list(counts.items())
        half = len(items) // 2

        with col1:
            for division, count in items[:half]:
                st.metric(division, f"{count} cases")
        with col2:
            for division, count in items[half:]:
                st.metric(division, f"{count} cases")
    else:
        st.markdown(f"No {selected_disease} cases logged this week yet.")

    st.markdown("---")
    st.markdown("""
    <div class="info-box">
        💡 <b>How this works:</b> Every time a prescription is analyzed,
        the disease condition is anonymously logged by division.
        This creates a real-time disease early warning system for Bangladesh.
    </div>
    """, unsafe_allow_html=True)