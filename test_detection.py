"""
Test debris detection - downloads a small area and runs detection
"""

import os
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

from pathlib import Path

# Create output directory
OUTPUT_DIR = Path("./test_output")
OUTPUT_DIR.mkdir(exist_ok=True)

print("=" * 60)
print("DEBRIS DETECTION TEST")
print("Pinellas County - Clearwater Beach Area")
print("=" * 60)

# Step 1: Download satellite imagery
print("\n[Step 1] Downloading satellite imagery...")
from samgeo import tms_to_geotiff

# Small test area in Clearwater Beach
# [west, south, east, north]
bbox = [-82.830, 27.970, -82.820, 27.980]  # ~1km x 1km area

image_path = OUTPUT_DIR / "test_satellite.tif"

print(f"Bounding box: {bbox}")
print(f"Output: {image_path}")

tms_to_geotiff(
    output=str(image_path),
    bbox=bbox,
    zoom=18,
    source="Satellite",
    quiet=False
)

print(f"\nImagery downloaded: {image_path}")
print(f"File size: {image_path.stat().st_size / 1024 / 1024:.2f} MB")

# Step 2: Initialize LangSAM
print("\n[Step 2] Initializing LangSAM model...")
print("(This may take a moment to download model weights on first run)")

from samgeo.text_sam import LangSAM

sam = LangSAM()
print("LangSAM ready!")

# Step 3: Run detection
print("\n[Step 3] Running debris detection...")
text_prompt = "debris pile"
print(f"Text prompt: '{text_prompt}'")

sam.predict(
    image=str(image_path),
    text_prompt=text_prompt,
    box_threshold=0.24,
    text_threshold=0.24,
)

# Save results
mask_path = OUTPUT_DIR / "debris_mask.tif"
sam.save_masks(output=str(mask_path), dtype="uint8")
print(f"Mask saved: {mask_path}")

# Convert to vector
vector_path = OUTPUT_DIR / "debris_detected.geojson"
try:
    sam.raster_to_vector(str(mask_path), str(vector_path))

    import geopandas as gpd
    gdf = gpd.read_file(vector_path)
    print(f"\nDetected {len(gdf)} potential debris locations")
    print(f"Results saved: {vector_path}")
except Exception as e:
    print(f"No debris detected or error converting: {e}")

# Step 4: Show visual results
print("\n[Step 4] Generating visualization...")
try:
    sam.show_anns(
        cmap="Reds",
        add_boxes=True,
        alpha=0.5,
        title="Debris Detection Results",
        output=str(OUTPUT_DIR / "detection_result.png")
    )
    print(f"Visualization saved: {OUTPUT_DIR / 'detection_result.png'}")
except Exception as e:
    print(f"Could not save visualization: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print(f"\nOutput files in: {OUTPUT_DIR.absolute()}")
for f in OUTPUT_DIR.iterdir():
    print(f"  - {f.name} ({f.stat().st_size / 1024:.1f} KB)")
