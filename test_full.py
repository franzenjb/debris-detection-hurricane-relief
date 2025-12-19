"""
Full debris detection test with real satellite imagery download
"""

import os
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

from pathlib import Path

OUTPUT_DIR = Path("./test_output")
OUTPUT_DIR.mkdir(exist_ok=True)

print("=" * 60)
print("DEBRIS DETECTION - FULL TEST")
print("Pinellas County - Clearwater Beach Area")
print("=" * 60)

# Step 1: Download real satellite imagery using GDAL
print("\n[Step 1] Downloading satellite imagery...")
from samgeo import tms_to_geotiff

# Small area in Clearwater Beach [west, south, east, north]
bbox = [-82.828, 27.972, -82.822, 27.978]
image_path = OUTPUT_DIR / "clearwater_satellite.tif"

print(f"Area: Clearwater Beach, FL")
print(f"Bbox: {bbox}")

tms_to_geotiff(
    output=str(image_path),
    bbox=bbox,
    zoom=18,
    source="Satellite",
    quiet=False
)

print(f"\nImagery saved: {image_path}")
print(f"File size: {image_path.stat().st_size / 1024 / 1024:.2f} MB")

# Step 2: Initialize LangSAM
print("\n[Step 2] Initializing LangSAM...")
from samgeo.text_sam import LangSAM
sam = LangSAM()
print("LangSAM ready!")

# Step 3: Detect objects
print("\n[Step 3] Running detection...")

# Test with building first (common in satellite imagery)
prompt = "building"
print(f"Detecting: '{prompt}'")

sam.predict(
    image=str(image_path),
    text_prompt=prompt,
    box_threshold=0.24,
    text_threshold=0.24,
)

# Check results
if hasattr(sam, 'boxes') and sam.boxes is not None and len(sam.boxes) > 0:
    print(f"Found {len(sam.boxes)} {prompt}(s)")

    # Save prediction image
    output_img = OUTPUT_DIR / f"{prompt}_detected.png"
    sam.show_anns(
        cmap="Reds",
        add_boxes=True,
        alpha=0.5,
        title=f"Detected: {prompt}",
        output=str(output_img)
    )
    print(f"Results saved to: {output_img}")
else:
    print(f"No {prompt}s detected")

# Step 4: Try debris detection
print("\n[Step 4] Testing debris detection...")
debris_prompts = ["debris", "rubble", "pile"]

for prompt in debris_prompts:
    print(f"  Trying: '{prompt}'...")
    try:
        sam.predict(
            image=str(image_path),
            text_prompt=prompt,
            box_threshold=0.20,
            text_threshold=0.20,
        )
        if hasattr(sam, 'boxes') and sam.boxes is not None and len(sam.boxes) > 0:
            print(f"    Found {len(sam.boxes)} matches!")
        else:
            print(f"    No matches (image may not contain debris)")
    except Exception as e:
        print(f"    Error: {e}")

# Step 5: Save visualization
print("\n[Step 5] Saving visualization...")
try:
    sam.show_anns(
        cmap="Reds",
        add_boxes=True,
        alpha=0.5,
        title="Detection Results",
        output=str(OUTPUT_DIR / "final_result.png")
    )
    print(f"Saved: {OUTPUT_DIR / 'final_result.png'}")
except Exception as e:
    print(f"Note: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print(f"\nFiles in {OUTPUT_DIR}:")
for f in sorted(OUTPUT_DIR.iterdir()):
    print(f"  - {f.name} ({f.stat().st_size / 1024:.1f} KB)")
