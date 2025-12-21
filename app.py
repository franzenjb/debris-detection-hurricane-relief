"""
Debris Detection Web Application
Visual interface for detecting debris piles in satellite imagery
For Red Cross Hurricane Relief - Pinellas County, FL
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
    page_title="Debris Detection - Hurricane Relief",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - with explicit dark text colors for visibility
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #c62828 !important;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #fff 0%, #ffebee 100%);
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #333 !important;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header strong {
        color: #c62828 !important;
    }
    .info-box {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
        color: #1a1a1a !important;
    }
    .info-box strong {
        color: #1565c0 !important;
    }
    .success-box {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
        color: #1a1a1a !important;
    }
    .success-box strong {
        color: #2e7d32 !important;
    }
    .warning-box {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
        color: #1a1a1a !important;
    }
    .warning-box strong {
        color: #e65100 !important;
    }
    .warning-box a {
        color: #1565c0 !important;
        text-decoration: underline;
    }
    .error-box {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
        color: #1a1a1a !important;
    }
    .error-box strong {
        color: #c62828 !important;
    }
    .big-number {
        font-size: 3rem;
        font-weight: bold;
        color: #d32f2f !important;
    }
    .step-header {
        background-color: #d32f2f;
        color: white !important;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        margin: 1rem 0;
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

# Header
st.markdown('<h1 class="main-header">🛰️ Hurricane Debris Detection</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI-powered detection of debris piles for Red Cross relief coordination<br><strong>Pinellas County, FL - Hurricane Milton/Helene</strong></p>', unsafe_allow_html=True)

# Important notice
st.markdown("""
<div class="warning-box">
<strong>⚠️ Important:</strong> For accurate debris detection, you need <strong>POST-HURRICANE satellite imagery</strong>.
Regular satellite maps (Google/ESRI) show pre-hurricane conditions with NO debris.<br><br>
<strong>Get post-hurricane imagery from:</strong><br>
• <a href="https://storms.ngs.noaa.gov/storms/milton/index.html" target="_blank">NOAA Hurricane Milton Imagery</a><br>
• <a href="https://storms.ngs.noaa.gov/storms/helene/index.html" target="_blank">NOAA Hurricane Helene Imagery</a>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🎯 Detection Settings")

    detection_sensitivity = st.slider(
        "Sensitivity",
        min_value=0.10,
        max_value=0.40,
        value=0.20,
        step=0.02,
        help="Lower = more detections (may have false positives)"
    )

    st.markdown("---")
    st.markdown("### 📋 What to Detect")

    detect_debris = st.checkbox("🗑️ Debris Piles", value=True)
    detect_rubble = st.checkbox("🧱 Rubble/Construction Waste", value=True)
    detect_tarps = st.checkbox("🔵 Blue Tarps (Damaged Roofs)", value=True)
    detect_vehicles = st.checkbox("🚗 Damaged/Displaced Vehicles", value=False)

    st.markdown("---")
    st.markdown("### ℹ️ How It Works")
    st.markdown("""
    1. Upload post-hurricane aerial photo
    2. AI scans for debris patterns
    3. Results show detected locations
    4. Export for Red Cross GIS
    """)

    st.markdown("---")
    st.markdown("### 🔗 Data Sources")
    st.markdown("""
    [NOAA Milton Imagery](https://storms.ngs.noaa.gov/storms/milton/index.html)

    [NOAA Helene Imagery](https://storms.ngs.noaa.gov/storms/helene/index.html)

    [Maxar Open Data (AWS)](https://registry.opendata.aws/maxar-open-data/)
    """)

# Main content - Two columns
col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown('<div class="step-header">📸 Step 1: Upload Post-Hurricane Image</div>', unsafe_allow_html=True)

    st.markdown("""
    Upload aerial/satellite imagery showing hurricane damage.
    Best results with high-resolution images showing streets with debris piles.
    """)

    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['png', 'jpg', 'jpeg', 'tif', 'tiff'],
        help="Upload post-hurricane aerial imagery"
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
        st.markdown("#### 📷 Your Uploaded Image:")
        image = Image.open(uploaded_file)
        st.image(image, caption=f"Uploaded: {uploaded_file.name}", use_container_width=True)

        st.success(f"✅ Image uploaded successfully! Size: {image.size[0]}x{image.size[1]} pixels")

    else:
        st.markdown("""
        <div class="info-box">
        <strong>📥 No image uploaded yet</strong><br><br>
        To get post-hurricane imagery:<br>
        1. Visit <a href="https://storms.ngs.noaa.gov/storms/milton/index.html">NOAA Storm Imagery</a><br>
        2. Navigate to Pinellas County area<br>
        3. Screenshot or download the imagery<br>
        4. Upload here for analysis
        </div>
        """, unsafe_allow_html=True)

        # Demo option
        st.markdown("---")
        st.markdown("#### 🎮 Or Try Demo Mode")
        if st.button("Run Demo with Sample Area", use_container_width=True):
            st.session_state.demo_mode = True
            st.info("Demo mode: Will download current satellite imagery (may not show debris)")

with col_right:
    st.markdown('<div class="step-header">🔍 Step 2: Run AI Detection</div>', unsafe_allow_html=True)

    if st.session_state.uploaded_image is None and not st.session_state.get('demo_mode', False):
        st.markdown("""
        <div class="info-box">
        <strong>⬅️ Upload an image first</strong><br><br>
        Once you upload a post-hurricane aerial image,
        click the button below to run AI debris detection.
        </div>
        """, unsafe_allow_html=True)

    # Run detection button
    run_disabled = st.session_state.uploaded_image is None and not st.session_state.get('demo_mode', False)

    if st.button("🚀 DETECT DEBRIS", type="primary", use_container_width=True, disabled=run_disabled):

        progress_container = st.container()

        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Demo mode - download imagery
            if st.session_state.get('demo_mode', False) and st.session_state.uploaded_image is None:
                status_text.markdown("📡 **Downloading demo satellite imagery...**")
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
            status_text.markdown("🤖 **Loading AI model (this takes a moment first time)...**")
            progress_bar.progress(30)

            try:
                os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
                from samgeo.text_sam import LangSAM
                sam = LangSAM()
                progress_bar.progress(50)
                status_text.markdown("✅ **AI model loaded!**")
            except Exception as e:
                st.error(f"Error loading AI model: {e}")
                st.stop()

            # Step 2: Run detections
            status_text.markdown("🔍 **Scanning image for debris...**")

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
                status_text.markdown(f"🔍 **Searching for: {display_name}...**")

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
            status_text.markdown("✅ **Detection complete!**")

            st.session_state.results = results
            st.session_state.result_images = result_images
            st.session_state.detection_complete = True

            time.sleep(0.5)
            st.rerun()

# Results section
if st.session_state.detection_complete and st.session_state.results:
    st.markdown("---")
    st.markdown('<div class="step-header">📊 Step 3: Detection Results</div>', unsafe_allow_html=True)

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    total_detections = sum(st.session_state.results.values())

    with col1:
        st.metric("Total Detections", total_detections)

    results_list = list(st.session_state.results.items())
    for i, (name, count) in enumerate(results_list[:3]):
        with [col2, col3, col4][i]:
            st.metric(name, count)

    # Visual results
    col_img1, col_img2 = st.columns(2)

    with col_img1:
        st.markdown("#### 📷 Original Image")
        if st.session_state.uploaded_image and os.path.exists(st.session_state.uploaded_image):
            st.image(st.session_state.uploaded_image, use_container_width=True)

    with col_img2:
        st.markdown("#### 🎯 Detection Results")
        if 'final_result' in st.session_state and os.path.exists(st.session_state.final_result):
            st.image(st.session_state.final_result, use_container_width=True)

            # Explanation
            if total_detections > 0:
                st.markdown(f"""
                <div class="success-box">
                <strong>✅ Found {total_detections} potential debris locations</strong><br>
                Red boxes show detected areas. Review for accuracy before field deployment.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="warning-box">
                <strong>⚠️ No debris detected</strong><br>
                This could mean:<br>
                • Image doesn't contain visible debris<br>
                • Image is pre-hurricane (no debris exists)<br>
                • Try lowering detection sensitivity<br>
                • Try higher resolution imagery
                </div>
                """, unsafe_allow_html=True)

    # Individual detection results
    if st.session_state.get('result_images'):
        st.markdown("#### 🔍 Individual Detection Categories")

        img_cols = st.columns(min(len(st.session_state.result_images), 3))
        for i, (name, path) in enumerate(st.session_state.result_images.items()):
            if os.path.exists(path):
                with img_cols[i % 3]:
                    st.image(path, caption=name, use_container_width=True)

    # Export options
    st.markdown("---")
    st.markdown("#### 📤 Export Results")

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
                    "🖼️ Download Result Image",
                    data=f,
                    file_name="debris_detection_map.png",
                    mime="image/png",
                    use_container_width=True
                )

    with exp_col3:
        st.button("🗺️ Export to GeoJSON (Coming Soon)", disabled=True, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p><strong>🛰️ Debris Detection for Hurricane Relief</strong></p>
    <p>Built with SamGeo AI | For American Red Cross Disaster Response</p>
    <p>
        <a href="https://github.com/franzenjb/debris-detection-hurricane-relief">GitHub</a> |
        <a href="https://storms.ngs.noaa.gov/storms/milton/index.html">NOAA Imagery</a>
    </p>
</div>
""", unsafe_allow_html=True)
