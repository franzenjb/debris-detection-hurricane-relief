"""
Debris Detection Web Application
AI-powered satellite imagery analysis for disaster relief coordination
American Red Cross - Hurricane Relief Operations
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
from PIL import Image
import os
import time
from pathlib import Path
import tempfile

# Set page config
st.set_page_config(
    page_title="Debris Detection | Red Cross Relief",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Professional CSS - Red Cross Brand
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    .stApp {
        background-color: #f5f7fa;
    }

    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Typography */
    h1, h2, h3, h4, h5, h6, p, span, div, label {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }

    /* Header Branding */
    .rc-header {
        background: linear-gradient(135deg, #c62828 0%, #b71c1c 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        box-shadow: 0 8px 24px rgba(198, 40, 40, 0.15);
        margin-bottom: 2rem;
        border: 1px solid rgba(255,255,255,0.1);
    }

    .rc-header h1 {
        color: white !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        margin: 0 0 0.5rem 0 !important;
        letter-spacing: -0.5px;
    }

    .rc-header p {
        color: rgba(255,255,255,0.95) !important;
        font-size: 1rem !important;
        margin: 0 !important;
        font-weight: 400;
    }

    .rc-badge {
        display: inline-block;
        background: rgba(255,255,255,0.2);
        border: 1px solid rgba(255,255,255,0.3);
        padding: 0.4rem 1rem;
        border-radius: 20px;
        color: white !important;
        font-size: 0.85rem;
        font-weight: 500;
        margin-top: 0.75rem;
        backdrop-filter: blur(10px);
    }

    /* Card System */
    .rc-card {
        background: white;
        border-radius: 12px;
        padding: 1.75rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #e5e7eb;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }

    .rc-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        border-color: #d1d5db;
    }

    .rc-card-header {
        display: flex;
        align-items: center;
        margin-bottom: 1.25rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #f3f4f6;
    }

    .rc-card-icon {
        font-size: 1.75rem;
        margin-right: 0.75rem;
        filter: grayscale(20%);
    }

    .rc-card-title {
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        color: #1f2937 !important;
        margin: 0 !important;
    }

    .rc-card-subtitle {
        font-size: 0.875rem;
        color: #6b7280;
        margin-top: 0.25rem;
    }

    /* Alert Boxes */
    .rc-alert {
        padding: 1.25rem;
        border-radius: 10px;
        margin: 1.25rem 0;
        border-left: 4px solid;
        display: flex;
        align-items: start;
        gap: 1rem;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    .rc-alert-icon {
        font-size: 1.5rem;
        flex-shrink: 0;
        margin-top: 0.1rem;
    }

    .rc-alert-warning {
        background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%);
        border-color: #f57c00;
        color: #1a1a1a !important;
    }

    .rc-alert-warning strong {
        color: #e65100 !important;
    }

    .rc-alert-warning a {
        color: #1565c0 !important;
        font-weight: 500;
        text-decoration: none;
        border-bottom: 1px solid #1565c0;
    }

    .rc-alert-info {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-color: #1976d2;
        color: #1a1a1a !important;
    }

    .rc-alert-success {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        border-color: #388e3c;
        color: #1a1a1a !important;
    }

    /* Metrics */
    .rc-metric {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        border: 2px solid #f3f4f6;
        transition: all 0.3s ease;
    }

    .rc-metric:hover {
        border-color: #c62828;
        box-shadow: 0 4px 12px rgba(198, 40, 40, 0.1);
    }

    .rc-metric-value {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: #c62828 !important;
        line-height: 1;
        margin: 0 !important;
    }

    .rc-metric-label {
        font-size: 0.875rem;
        color: #6b7280;
        margin-top: 0.5rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.3s ease !important;
        border: none !important;
        font-size: 0.95rem !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #c62828 0%, #b71c1c 100%) !important;
        box-shadow: 0 4px 12px rgba(198, 40, 40, 0.3) !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #b71c1c 0%, #a71a1a 100%) !important;
        box-shadow: 0 6px 20px rgba(198, 40, 40, 0.4) !important;
        transform: translateY(-2px);
    }

    /* Progress Bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #c62828 0%, #f44336 100%);
        border-radius: 10px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f9fafb 100%);
        border-right: 1px solid #e5e7eb;
    }

    [data-testid="stSidebar"] h3 {
        color: #1f2937 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        margin-top: 1.5rem !important;
    }

    /* File Uploader */
    [data-testid="stFileUploader"] {
        background: white;
        border: 2px dashed #d1d5db;
        border-radius: 12px;
        padding: 2rem;
        transition: all 0.3s ease;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: #c62828;
        background: #fafafa;
    }

    /* Image Display */
    .rc-image-container {
        border-radius: 12px;
        overflow: hidden;
        border: 2px solid #e5e7eb;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }

    /* Footer */
    .rc-footer {
        text-align: center;
        padding: 2rem;
        color: #6b7280;
        font-size: 0.875rem;
        margin-top: 3rem;
        border-top: 1px solid #e5e7eb;
    }

    .rc-footer a {
        color: #c62828;
        text-decoration: none;
        font-weight: 500;
    }

    .rc-footer a:hover {
        text-decoration: underline;
    }

    /* Step Indicator */
    .rc-step {
        background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
        color: white !important;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    .rc-step-number {
        background: #c62828;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1rem;
    }

    .rc-step-title {
        font-size: 1.1rem;
        font-weight: 600;
        margin: 0 !important;
    }

    /* Status Messages */
    .rc-status {
        background: white;
        padding: 1.25rem;
        border-radius: 10px;
        border-left: 4px solid #c62828;
        margin: 1rem 0;
        font-weight: 500;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'detection_complete' not in st.session_state:
    st.session_state.detection_complete = False
if 'results' not in st.session_state:
    st.session_state.results = None
if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None

# Header - Modern Red Cross Branding
st.markdown("""
<div class="rc-header">
    <h1>🛰️ Hurricane Debris Detection System</h1>
    <p>AI-powered satellite imagery analysis for disaster relief coordination</p>
    <span class="rc-badge">🔴 American Red Cross | Pinellas County, FL</span>
</div>
""", unsafe_allow_html=True)

# Important notice - Clean alert design
st.markdown("""
<div class="rc-alert rc-alert-warning">
    <div class="rc-alert-icon">⚠️</div>
    <div>
        <strong>Post-Hurricane Imagery Required</strong><br>
        For accurate debris detection, you need satellite imagery captured <strong>after</strong> the hurricane event.
        Regular mapping services show pre-hurricane conditions with no debris visible.<br><br>
        <strong>Recommended Data Sources:</strong><br>
        • <a href="https://storms.ngs.noaa.gov/storms/milton/index.html" target="_blank">NOAA Hurricane Milton Imagery</a><br>
        • <a href="https://storms.ngs.noaa.gov/storms/helene/index.html" target="_blank">NOAA Hurricane Helene Imagery</a>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar - Clean Professional Design
with st.sidebar:
    st.markdown("### 🎯 Detection Settings")

    detection_sensitivity = st.slider(
        "Detection Sensitivity",
        min_value=0.10,
        max_value=0.40,
        value=0.20,
        step=0.02,
        help="Lower values = more detections (may include false positives)"
    )

    st.markdown("---")
    st.markdown("### 📋 Detection Categories")

    detect_debris = st.checkbox("🗑️ Debris Piles", value=True)
    detect_rubble = st.checkbox("🧱 Rubble & Construction Waste", value=True)
    detect_tarps = st.checkbox("🔵 Blue Tarps (Roof Damage)", value=True)
    detect_vehicles = st.checkbox("🚗 Displaced Vehicles", value=False)

    st.markdown("---")
    st.markdown("### ℹ️ How It Works")
    st.markdown("""
    **1.** Upload post-hurricane aerial imagery
    **2.** AI analyzes imagery for debris patterns
    **3.** Review detected locations on map
    **4.** Export results for field deployment
    """)

    st.markdown("---")
    st.markdown("### 🔗 Data Sources")
    st.markdown("""
    **NOAA Storm Imagery:**
    [Hurricane Milton](https://storms.ngs.noaa.gov/storms/milton/index.html)
    [Hurricane Helene](https://storms.ngs.noaa.gov/storms/helene/index.html)

    **Commercial Providers:**
    [Maxar Open Data (AWS)](https://registry.opendata.aws/maxar-open-data/)
    """)

# Main content - Card-based layout
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    # Step 1 Card
    st.markdown("""
    <div class="rc-step">
        <div class="rc-step-number">1</div>
        <div class="rc-step-title">Upload Imagery</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="rc-card">
        <div class="rc-card-header">
            <div class="rc-card-icon">📸</div>
            <div>
                <div class="rc-card-title">Post-Hurricane Aerial Imagery</div>
                <div class="rc-card-subtitle">Upload satellite or aerial photos showing hurricane damage</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Select image file",
        type=['png', 'jpg', 'jpeg', 'tif', 'tiff'],
        help="Supported formats: PNG, JPG, JPEG, TIF, TIFF",
        label_visibility="collapsed"
    )

    if uploaded_file is not None:
        # Save uploaded file
        output_dir = Path("./output")
        output_dir.mkdir(exist_ok=True)

        # Save to temp file
        file_extension = uploaded_file.name.split('.')[-1]
        temp_path = output_dir / f"uploaded_image.{file_extension}"

        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.session_state.uploaded_image = str(temp_path)

        # Display uploaded image
        image = Image.open(uploaded_file)
        st.markdown('<div class="rc-image-container">', unsafe_allow_html=True)
        st.image(image, caption=f"{uploaded_file.name}", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.success(f"Image ready: {image.size[0]}x{image.size[1]} pixels")

    else:
        st.markdown("""
        <div class="rc-alert rc-alert-info">
            <div class="rc-alert-icon">💡</div>
            <div>
                <strong>How to obtain imagery:</strong><br>
                1. Visit NOAA Storm Imagery portal<br>
                2. Navigate to Pinellas County, FL<br>
                3. Download or screenshot the area<br>
                4. Upload here for AI analysis
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Demo option
        st.markdown("---")
        if st.button("🎮 Load Demo Area", use_container_width=True):
            st.session_state.demo_mode = True
            st.info("Demo mode will download current satellite imagery (may not contain visible debris)")

    st.markdown("</div>", unsafe_allow_html=True)  # Close rc-card

with col_right:
    # Step 2 Card
    st.markdown("""
    <div class="rc-step">
        <div class="rc-step-number">2</div>
        <div class="rc-step-title">Run Detection</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="rc-card">
        <div class="rc-card-header">
            <div class="rc-card-icon">🔍</div>
            <div>
                <div class="rc-card-title">AI Debris Analysis</div>
                <div class="rc-card-subtitle">Automated detection of debris piles and damage indicators</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.uploaded_image is None and not st.session_state.get('demo_mode', False):
        st.markdown("""
        <div class="rc-alert rc-alert-info">
            <div class="rc-alert-icon">⬅️</div>
            <div>
                <strong>Waiting for imagery</strong><br>
                Upload a post-hurricane image in Step 1 to begin AI analysis.
                The detection process typically takes 1-2 minutes.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Run detection button
    run_disabled = st.session_state.uploaded_image is None and not st.session_state.get('demo_mode', False)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 START DEBRIS DETECTION", type="primary", use_container_width=True, disabled=run_disabled):

        progress_container = st.container()

        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Demo mode - download imagery
            if st.session_state.get('demo_mode', False) and st.session_state.uploaded_image is None:
                status_text.markdown('<div class="rc-status">📡 Downloading demo satellite imagery...</div>', unsafe_allow_html=True)
                progress_bar.progress(10)

                try:
                    from samgeo import tms_to_geotiff
                    output_dir = Path("./output")
                    output_dir.mkdir(exist_ok=True)

                    demo_path = output_dir / "demo_satellite.tif"
                    bbox = [-82.828, 27.972, -82.822, 27.978]  # Clearwater Beach

                    tms_to_geotiff(
                        output=str(demo_path),
                        bbox=bbox,
                        zoom=18,
                        source="Satellite",
                        overwrite=True,
                        quiet=True
                    )
                    st.session_state.uploaded_image = str(demo_path)
                    progress_bar.progress(25)
                except Exception as e:
                    st.error(f"Error downloading demo imagery: {e}")
                    st.stop()

            # Step 1: Load AI Model
            status_text.markdown('<div class="rc-status">🤖 Loading AI model (first-time initialization may take a moment)...</div>', unsafe_allow_html=True)
            progress_bar.progress(30)

            try:
                os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
                from samgeo.text_sam import LangSAM
                sam = LangSAM()
                progress_bar.progress(50)
                status_text.markdown('<div class="rc-status">✅ AI model loaded successfully</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error loading AI model: {e}")
                st.stop()

            # Step 2: Run detections
            status_text.markdown('<div class="rc-status">🔍 Analyzing imagery for debris patterns...</div>', unsafe_allow_html=True)

            results = {}
            result_images = {}

            prompts_to_run = []
            if detect_debris:
                prompts_to_run.append(("pile of debris", "Debris Piles"))
                prompts_to_run.append(("trash pile", "Trash Piles"))
            if detect_rubble:
                prompts_to_run.append(("rubble", "Rubble"))
                prompts_to_run.append(("construction debris", "Construction Debris"))
            if detect_tarps:
                prompts_to_run.append(("blue tarp", "Blue Tarps"))
            if detect_vehicles:
                prompts_to_run.append(("damaged vehicle", "Damaged Vehicles"))

            total_prompts = len(prompts_to_run)

            for i, (prompt, display_name) in enumerate(prompts_to_run):
                status_text.markdown(f'<div class="rc-status">🔍 Detecting: {display_name}...</div>', unsafe_allow_html=True)

                try:
                    sam.predict(
                        image=st.session_state.uploaded_image,
                        text_prompt=prompt,
                        box_threshold=detection_sensitivity,
                        text_threshold=detection_sensitivity,
                    )

                    count = len(sam.boxes) if hasattr(sam, 'boxes') and sam.boxes is not None else 0
                    results[display_name] = count

                    # Save result image for this detection
                    if count > 0:
                        result_path = Path("./output") / f"detected_{prompt.replace(' ', '_')}.png"
                        try:
                            sam.show_anns(
                                cmap="Reds",
                                add_boxes=True,
                                alpha=0.5,
                                title=f"Detected: {display_name} ({count} found)",
                                output=str(result_path)
                            )
                            result_images[display_name] = str(result_path)
                        except:
                            pass

                except Exception as e:
                    results[display_name] = 0

                progress_value = 50 + int((i + 1) / total_prompts * 45)
                progress_bar.progress(progress_value)

            # Save final combined result
            try:
                final_result_path = Path("./output") / "final_detection.png"
                sam.show_anns(
                    cmap="Reds",
                    add_boxes=True,
                    alpha=0.5,
                    title="All Detections",
                    output=str(final_result_path)
                )
                st.session_state.final_result = str(final_result_path)
            except:
                pass

            progress_bar.progress(100)
            status_text.markdown('<div class="rc-status">✅ Detection complete! Results ready for review.</div>', unsafe_allow_html=True)

            st.session_state.results = results
            st.session_state.result_images = result_images
            st.session_state.detection_complete = True

            time.sleep(0.5)
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)  # Close rc-card

# Results section
if st.session_state.detection_complete and st.session_state.results:
    st.markdown("---")

    # Step 3 Header
    st.markdown("""
    <div class="rc-step">
        <div class="rc-step-number">3</div>
        <div class="rc-step-title">Review Results</div>
    </div>
    """, unsafe_allow_html=True)

    # Summary metrics - Clean card design
    total_detections = sum(st.session_state.results.values())

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="rc-metric">
            <div class="rc-metric-value">{total_detections}</div>
            <div class="rc-metric-label">Total Detections</div>
        </div>
        """, unsafe_allow_html=True)

    results_list = list(st.session_state.results.items())
    for i, (name, count) in enumerate(results_list[:3]):
        with [col2, col3, col4][i]:
            st.markdown(f"""
            <div class="rc-metric">
                <div class="rc-metric-value">{count}</div>
                <div class="rc-metric-label">{name}</div>
            </div>
            """, unsafe_allow_html=True)

    # Visual results - Card layout
    st.markdown("<br>", unsafe_allow_html=True)
    col_img1, col_img2 = st.columns(2, gap="large")

    with col_img1:
        st.markdown("""
        <div class="rc-card">
            <div class="rc-card-header">
                <div class="rc-card-icon">📷</div>
                <div>
                    <div class="rc-card-title">Original Imagery</div>
                    <div class="rc-card-subtitle">Source satellite/aerial photograph</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if st.session_state.uploaded_image and os.path.exists(st.session_state.uploaded_image):
            st.markdown('<div class="rc-image-container">', unsafe_allow_html=True)
            st.image(st.session_state.uploaded_image, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col_img2:
        st.markdown("""
        <div class="rc-card">
            <div class="rc-card-header">
                <div class="rc-card-icon">🎯</div>
                <div>
                    <div class="rc-card-title">AI Detection Results</div>
                    <div class="rc-card-subtitle">Identified debris locations</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if 'final_result' in st.session_state and os.path.exists(st.session_state.final_result):
            st.markdown('<div class="rc-image-container">', unsafe_allow_html=True)
            st.image(st.session_state.final_result, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Explanation
            if total_detections > 0:
                st.markdown(f"""
                <div class="rc-alert rc-alert-success">
                    <div class="rc-alert-icon">✅</div>
                    <div>
                        <strong>Found {total_detections} potential debris locations</strong><br>
                        Red boxes indicate detected areas. Please review results for accuracy before field deployment.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="rc-alert rc-alert-warning">
                    <div class="rc-alert-icon">⚠️</div>
                    <div>
                        <strong>No debris detected</strong><br>
                        Possible reasons:<br>
                        • Image may not contain visible debris<br>
                        • Imagery may be pre-hurricane<br>
                        • Try adjusting detection sensitivity<br>
                        • Consider higher resolution imagery
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # Individual detection results
    if st.session_state.get('result_images'):
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="rc-card">
            <div class="rc-card-header">
                <div class="rc-card-icon">🔍</div>
                <div>
                    <div class="rc-card-title">Detailed Category Results</div>
                    <div class="rc-card-subtitle">Individual detection breakdowns by type</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        img_cols = st.columns(min(len(st.session_state.result_images), 3))
        for i, (name, path) in enumerate(st.session_state.result_images.items()):
            if os.path.exists(path):
                with img_cols[i % 3]:
                    st.markdown('<div class="rc-image-container">', unsafe_allow_html=True)
                    st.image(path, caption=name, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # Export options - Clean card design
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="rc-card">
        <div class="rc-card-header">
            <div class="rc-card-icon">📤</div>
            <div>
                <div class="rc-card-title">Export & Share Results</div>
                <div class="rc-card-subtitle">Download results for field teams and GIS systems</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    exp_col1, exp_col2, exp_col3 = st.columns(3)

    with exp_col1:
        # CSV download
        import pandas as pd
        df = pd.DataFrame([
            {"Category": k, "Count": v, "Priority": "High" if v > 5 else "Medium" if v > 2 else "Low"}
            for k, v in st.session_state.results.items()
        ])
        csv = df.to_csv(index=False)
        st.download_button(
            "📄 Download CSV Report",
            data=csv,
            file_name="debris_detection_results.csv",
            mime="text/csv",
            use_container_width=True
        )

    with exp_col2:
        if 'final_result' in st.session_state and os.path.exists(st.session_state.final_result):
            with open(st.session_state.final_result, "rb") as f:
                st.download_button(
                    "🖼️ Download Detection Map",
                    data=f,
                    file_name="debris_detection_map.png",
                    mime="image/png",
                    use_container_width=True
                )

    with exp_col3:
        st.button("🗺️ Export to GeoJSON", disabled=True, use_container_width=True, help="GIS export feature coming soon")

    st.markdown("</div>", unsafe_allow_html=True)

# Footer - Professional branding
st.markdown("""
<div class="rc-footer">
    <p style="margin-bottom: 0.75rem;"><strong>Hurricane Debris Detection System</strong></p>
    <p style="margin-bottom: 0.75rem;">AI-powered satellite imagery analysis for disaster relief coordination</p>
    <p style="margin-bottom: 0.75rem;">
        Built with SamGeo AI • American Red Cross • Pinellas County Hurricane Relief
    </p>
    <p style="margin: 0;">
        <a href="https://github.com/franzenjb/debris-detection-hurricane-relief" target="_blank">GitHub Repository</a> •
        <a href="https://storms.ngs.noaa.gov/storms/milton/index.html" target="_blank">NOAA Storm Imagery</a> •
        <a href="https://www.redcross.org" target="_blank">American Red Cross</a>
    </p>
</div>
""", unsafe_allow_html=True)
