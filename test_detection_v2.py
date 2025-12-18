"""
Test debris detection - alternative approach using leafmap
"""

import os
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

from pathlib import Path

# Create output directory
OUTPUT_DIR = Path("./test_output")
OUTPUT_DIR.mkdir(exist_ok=True)

print("=" * 60)
print("DEBRIS DETECTION TEST (v2)")
print("Pinellas County - Clearwater Beach Area")
print("=" * 60)

# Step 1: Download satellite imagery using leafmap
print("\n[Step 1] Downloading satellite imagery...")

import leafmap

# Small test area in Clearwater Beach
# [west, south, east, north]
bbox = [-82.830, 27.970, -82.820, 27.980]  # ~1km x 1km area

image_path = OUTPUT_DIR / "test_satellite.tif"

print(f"Bounding box: {bbox}")
print(f"Output: {image_path}")

try:
    leafmap.map_tiles_to_geotiff(
        output=str(image_path),
        bbox=bbox,
        zoom=18,
        source="Satellite",
        quiet=False
    )
    print(f"\nImagery downloaded: {image_path}")
    print(f"File size: {image_path.stat().st_size / 1024 / 1024:.2f} MB")
except Exception as e:
    print(f"Error with leafmap download: {e}")
    print("\nTrying alternative: downloading a sample image from web...")

    # Download a sample image for testing
    import urllib.request
    sample_url = "https://raw.githubusercontent.com/opengeos/segment-geospatial/main/examples/data/satellite.tif"
    urllib.request.urlretrieve(sample_url, str(image_path))
    print(f"Downloaded sample image: {image_path}")

# Check if file exists
if not image_path.exists():
    print("ERROR: Could not download imagery. Please install GDAL:")
    print("  brew install gdal")
    print("  pip install GDAL")
    exit(1)

# Step 2: Initialize LangSAM
print("\n[Step 2] Initializing LangSAM model...")
print("(This downloads ~2.5GB of model weights on first run)")

from samgeo.text_sam import LangSAM

sam = LangSAM()
print("LangSAM ready!")

# Step 3: Run detection
print("\n[Step 3] Running debris detection...")
text_prompt = "building"  # Start with "building" as a test - easier to detect
print(f"Text prompt: '{text_prompt}'")

sam.predict(
    image=str(image_path),
    text_prompt=text_prompt,
    box_threshold=0.24,
    text_threshold=0.24,
)

# Save results
mask_path = OUTPUT_DIR / "detection_mask.tif"
sam.save_masks(output=str(mask_path), dtype="uint8")
print(f"Mask saved: {mask_path}")

# Convert to vector
vector_path = OUTPUT_DIR / "detected_objects.geojson"
try:
    sam.raster_to_vector(str(mask_path), str(vector_path))

    import geopandas as gpd
    gdf = gpd.read_file(vector_path)
    print(f"\nDetected {len(gdf)} objects matching '{text_prompt}'")
    print(f"Results saved: {vector_path}")
except Exception as e:
    print(f"Vector conversion note: {e}")

# Step 4: Show visual results
print("\n[Step 4] Generating visualization...")
try:
    output_fig = str(OUTPUT_DIR / "detection_result.png")
    sam.show_anns(
        cmap="Reds",
        add_boxes=True,
        alpha=0.5,
        title=f"Detection Results: {text_prompt}",
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
