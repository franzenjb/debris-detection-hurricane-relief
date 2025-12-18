"""
Test debris detection with sample satellite image
"""

import os
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

from pathlib import Path

# Create output directory
OUTPUT_DIR = Path("./test_output")
OUTPUT_DIR.mkdir(exist_ok=True)

image_path = OUTPUT_DIR / "sample_satellite.tif"

print("=" * 60)
print("DEBRIS DETECTION TEST")
print("Using sample satellite imagery")
print("=" * 60)

# Check if sample image exists
if not image_path.exists():
    print(f"ERROR: Sample image not found at {image_path}")
    print("Run: curl -L -o test_output/sample_satellite.tif 'https://github.com/opengeos/data/raw/main/images/satellite.tif'")
    exit(1)

print(f"\nUsing image: {image_path}")
print(f"File size: {image_path.stat().st_size / 1024:.1f} KB")

# Step 1: Initialize LangSAM
print("\n[Step 1] Initializing LangSAM model...")
print("(First run downloads ~2.5GB of model weights - this takes a few minutes)")

from samgeo.text_sam import LangSAM

sam = LangSAM()
print("LangSAM ready!")

# Step 2: Run detection with text prompts
print("\n[Step 2] Running object detection...")

# Test with common objects first to verify it works
test_prompts = ["building", "tree", "road"]

for prompt in test_prompts:
    print(f"\n  Detecting: '{prompt}'...")
    try:
        sam.predict(
            image=str(image_path),
            text_prompt=prompt,
            box_threshold=0.24,
            text_threshold=0.24,
        )

        # Check if any boxes were found
        if hasattr(sam, 'boxes') and sam.boxes is not None and len(sam.boxes) > 0:
            print(f"  Found {len(sam.boxes)} matches for '{prompt}'")
        else:
            print(f"  No matches for '{prompt}'")

    except Exception as e:
        print(f"  Error detecting '{prompt}': {e}")

# Step 3: Run debris detection specifically
print("\n[Step 3] Testing debris-specific prompts...")
debris_prompts = ["debris pile", "rubble", "damaged structure", "construction materials"]

for prompt in debris_prompts:
    print(f"\n  Detecting: '{prompt}'...")
    try:
        sam.predict(
            image=str(image_path),
            text_prompt=prompt,
            box_threshold=0.20,  # Lower threshold for debris
            text_threshold=0.20,
        )

        if hasattr(sam, 'boxes') and sam.boxes is not None and len(sam.boxes) > 0:
            print(f"  Found {len(sam.boxes)} potential matches")

            # Save this result
            mask_path = OUTPUT_DIR / f"{prompt.replace(' ', '_')}_mask.tif"
            sam.save_masks(output=str(mask_path), dtype="uint8")
            print(f"  Saved mask: {mask_path.name}")
        else:
            print(f"  No matches (this sample may not contain debris)")

    except Exception as e:
        print(f"  Note: {e}")

# Step 4: Save visualization with last successful detection
print("\n[Step 4] Saving visualization...")
try:
    output_fig = str(OUTPUT_DIR / "detection_result.png")
    sam.show_anns(
        cmap="Reds",
        add_boxes=True,
        alpha=0.5,
        title="Detection Results",
        output=output_fig
    )
    print(f"Visualization saved: {output_fig}")
except Exception as e:
    print(f"Visualization note: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print(f"\nOutput files in: {OUTPUT_DIR.absolute()}")
for f in OUTPUT_DIR.iterdir():
    size_kb = f.stat().st_size / 1024
    print(f"  - {f.name} ({size_kb:.1f} KB)")

print("\n" + "-" * 60)
print("NEXT STEPS:")
print("-" * 60)
print("1. Install GDAL to download actual satellite imagery:")
print("   brew install gdal")
print("   pip install GDAL")
print("")
print("2. Or use Google Colab with the notebook:")
print("   debris_detection_notebook.ipynb")
print("")
print("3. For NOAA post-hurricane imagery:")
print("   https://storms.ngs.noaa.gov/storms/milton/index.html")
