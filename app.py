"""
Debris Detection - Hurricane Relief
Simple, clean interface for AI debris detection
"""

import streamlit as st
from PIL import Image
import os
import time
from pathlib import Path

st.set_page_config(
    page_title="Debris Detection",
    page_icon="🛰️",
    layout="wide"
)

# Simple, high-contrast CSS
st.markdown("""
<style>
    /* Force dark text everywhere */
    * { color: #1a1a1a !important; }

    /* Red header */
    .header {
        background: #c62828;
        color: white !important;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    .header h1, .header p { color: white !important; margin: 0; }
    .header h1 { font-size: 28px; margin-bottom: 8px; }

    /* Warning box */
    .warning {
        background: #fff3cd;
        border: 2px solid #ffc107;
        border-radius: 8px;
        padding: 16px;
        margin: 16px 0;
    }
    .warning strong { color: #856404 !important; }
    .warning a { color: #0066cc !important; }

    /* Section headers */
    .section {
        background: #333;
        color: white !important;
        padding: 12px 16px;
        border-radius: 6px;
        margin: 16px 0 12px 0;
        font-weight: bold;
        font-size: 16px;
    }
    .section * { color: white !important; }

    /* Info box */
    .info {
        background: #e7f3ff;
        border: 2px solid #0066cc;
        border-radius: 8px;
        padding: 16px;
        margin: 12px 0;
    }

    /* Success box */
    .success {
        background: #d4edda;
        border: 2px solid #28a745;
        border-radius: 8px;
        padding: 16px;
        margin: 12px 0;
    }

    /* Big metric */
    .metric {
        background: white;
        border: 2px solid #ddd;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
    }
    .metric-value {
        font-size: 48px !important;
        font-weight: bold !important;
        color: #c62828 !important;
    }
    .metric-label {
        font-size: 14px;
        color: #666 !important;
        text-transform: uppercase;
    }

    /* Fix Streamlit elements */
    .stButton > button {
        background: #c62828 !important;
        color: white !important;
        border: none !important;
        padding: 12px 24px !important;
        font-size: 16px !important;
        font-weight: bold !important;
    }
    .stButton > button:hover {
        background: #a52020 !important;
    }
    .stButton > button:disabled {
        background: #ccc !important;
        color: #666 !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] { background: #f8f9fa; }
    [data-testid="stSidebar"] * { color: #1a1a1a !important; }
</style>
""", unsafe_allow_html=True)

# Initialize state
if 'detection_complete' not in st.session_state:
    st.session_state.detection_complete = False
if 'results' not in st.session_state:
    st.session_state.results = None
if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None

# Header
st.markdown("""
<div class="header">
    <h1>🛰️ Hurricane Debris Detection</h1>
    <p>AI-powered analysis for Red Cross relief coordination | Pinellas County, FL</p>
</div>
""", unsafe_allow_html=True)

# Warning
st.markdown("""
<div class="warning">
    <strong>⚠️ You need POST-HURRICANE imagery!</strong><br><br>
    Regular Google/ESRI maps show pre-hurricane conditions with NO debris visible.<br><br>
    <strong>Get post-hurricane imagery from:</strong><br>
    • <a href="https://storms.ngs.noaa.gov/storms/milton/index.html" target="_blank">NOAA Hurricane Milton Imagery</a><br>
    • <a href="https://storms.ngs.noaa.gov/storms/helene/index.html" target="_blank">NOAA Hurricane Helene Imagery</a>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### Settings")

    sensitivity = st.slider("Detection Sensitivity", 0.10, 0.40, 0.20, 0.02)

    st.markdown("---")
    st.markdown("### What to Detect")
    detect_debris = st.checkbox("Debris Piles", value=True)
    detect_rubble = st.checkbox("Rubble", value=True)
    detect_tarps = st.checkbox("Blue Tarps", value=True)
    detect_vehicles = st.checkbox("Damaged Vehicles", value=False)

    st.markdown("---")
    st.markdown("### Data Sources")
    st.markdown("[NOAA Milton](https://storms.ngs.noaa.gov/storms/milton/index.html)")
    st.markdown("[NOAA Helene](https://storms.ngs.noaa.gov/storms/helene/index.html)")

# Main content
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section">📸 Step 1: Upload Image</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload post-hurricane aerial imagery",
        type=['png', 'jpg', 'jpeg', 'tif', 'tiff']
    )

    if uploaded_file:
        output_dir = Path("./output")
        output_dir.mkdir(exist_ok=True)

        ext = uploaded_file.name.split('.')[-1]
        temp_path = output_dir / f"uploaded.{ext}"

        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.session_state.uploaded_image = str(temp_path)

        image = Image.open(uploaded_file)
        st.image(image, caption=f"Uploaded: {uploaded_file.name}", use_container_width=True)
        st.success(f"✅ Ready! Size: {image.size[0]}x{image.size[1]}px")
    else:
        st.markdown("""
        <div class="info">
            <strong>No image uploaded</strong><br><br>
            1. Go to NOAA Storm Imagery<br>
            2. Navigate to your area<br>
            3. Screenshot or download<br>
            4. Upload here
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown('<div class="section">🔍 Step 2: Run Detection</div>', unsafe_allow_html=True)

    if st.session_state.uploaded_image is None:
        st.markdown("""
        <div class="info">
            <strong>⬅️ Upload an image first</strong><br><br>
            Once you upload post-hurricane imagery, click the button below to run AI detection.
        </div>
        """, unsafe_allow_html=True)

    run_disabled = st.session_state.uploaded_image is None

    if st.button("🚀 DETECT DEBRIS", disabled=run_disabled, use_container_width=True):
        progress = st.progress(0)
        status = st.empty()

        status.info("🤖 Loading AI model...")
        progress.progress(20)

        try:
            os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
            from samgeo.text_sam import LangSAM
            sam = LangSAM()
            progress.progress(40)
            status.info("✅ Model loaded!")
        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()

        status.info("🔍 Scanning for debris...")

        results = {}
        prompts = []
        if detect_debris:
            prompts.extend([("pile of debris", "Debris"), ("trash pile", "Trash")])
        if detect_rubble:
            prompts.extend([("rubble", "Rubble"), ("construction debris", "Construction")])
        if detect_tarps:
            prompts.append(("blue tarp", "Blue Tarps"))
        if detect_vehicles:
            prompts.append(("damaged vehicle", "Vehicles"))

        for i, (prompt, name) in enumerate(prompts):
            status.info(f"🔍 Detecting: {name}...")
            try:
                sam.predict(
                    image=st.session_state.uploaded_image,
                    text_prompt=prompt,
                    box_threshold=sensitivity,
                    text_threshold=sensitivity,
                )
                count = len(sam.boxes) if hasattr(sam, 'boxes') and sam.boxes is not None else 0
                results[name] = count
            except:
                results[name] = 0

            progress.progress(40 + int((i+1) / len(prompts) * 50))

        # Save result
        try:
            result_path = Path("./output") / "result.png"
            sam.show_anns(
                cmap="Reds",
                add_boxes=True,
                alpha=0.5,
                title="Detection Results",
                output=str(result_path)
            )
            st.session_state.final_result = str(result_path)
        except:
            pass

        progress.progress(100)
        status.success("✅ Detection complete!")

        st.session_state.results = results
        st.session_state.detection_complete = True
        time.sleep(0.5)
        st.rerun()

# Results
if st.session_state.detection_complete and st.session_state.results:
    st.markdown("---")
    st.markdown('<div class="section">📊 Step 3: Results</div>', unsafe_allow_html=True)

    total = sum(st.session_state.results.values())

    # Metrics
    cols = st.columns(4)
    with cols[0]:
        st.markdown(f"""
        <div class="metric">
            <div class="metric-value">{total}</div>
            <div class="metric-label">Total Found</div>
        </div>
        """, unsafe_allow_html=True)

    items = list(st.session_state.results.items())[:3]
    for i, (name, count) in enumerate(items):
        with cols[i+1]:
            st.markdown(f"""
            <div class="metric">
                <div class="metric-value">{count}</div>
                <div class="metric-label">{name}</div>
            </div>
            """, unsafe_allow_html=True)

    # Images
    st.markdown("<br>", unsafe_allow_html=True)
    img1, img2 = st.columns(2)

    with img1:
        st.markdown("**Original Image**")
        if st.session_state.uploaded_image and os.path.exists(st.session_state.uploaded_image):
            st.image(st.session_state.uploaded_image, use_container_width=True)

    with img2:
        st.markdown("**Detection Results**")
        if 'final_result' in st.session_state and os.path.exists(st.session_state.final_result):
            st.image(st.session_state.final_result, use_container_width=True)

    if total > 0:
        st.markdown(f"""
        <div class="success">
            <strong>✅ Found {total} potential debris locations</strong><br>
            Red boxes show detected areas. Review before field deployment.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="warning">
            <strong>⚠️ No debris detected</strong><br>
            This could mean the image is pre-hurricane or try lowering sensitivity.
        </div>
        """, unsafe_allow_html=True)

    # Export
    st.markdown("---")
    st.markdown("**Export Results**")
    exp1, exp2, exp3 = st.columns(3)

    with exp1:
        import pandas as pd
        df = pd.DataFrame([{"Category": k, "Count": v} for k, v in st.session_state.results.items()])
        st.download_button("📄 CSV Report", df.to_csv(index=False), "results.csv", "text/csv", use_container_width=True)

    with exp2:
        if 'final_result' in st.session_state and os.path.exists(st.session_state.final_result):
            with open(st.session_state.final_result, "rb") as f:
                st.download_button("🖼️ Result Image", f, "detection.png", "image/png", use_container_width=True)

    with exp3:
        st.button("🗺️ GeoJSON (Soon)", disabled=True, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<p style="text-align: center; color: #666 !important; font-size: 14px;">
Hurricane Debris Detection | Built with SamGeo AI | American Red Cross
</p>
""", unsafe_allow_html=True)
