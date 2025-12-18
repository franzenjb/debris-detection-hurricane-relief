# Debris Detection for Hurricane Relief

Automated detection of debris piles in satellite imagery using AI (SamGeo) to help Red Cross target relief efforts in Pinellas County, FL after Hurricanes Milton and Helene.

## Overview

This application uses **SamGeo** (Segment Anything Model for Geospatial Data) with text prompts to automatically identify debris piles in satellite imagery. The detected locations are exported as GeoJSON/Shapefile for use in GIS systems and relief coordination.

## Quick Start

### Option 1: Google Colab (Recommended - Free GPU)

1. Open Google Colab: https://colab.research.google.com
2. Upload `debris_detection_notebook.ipynb`
3. Go to Runtime → Change runtime type → Select "GPU"
4. Run all cells

### Option 2: Local Installation

```bash
# Create environment
conda create -n debris_detect python=3.11 -y
conda activate debris_detect

# Install PyTorch with CUDA (for GPU)
conda install pytorch torchvision pytorch-cuda=12.1 -c pytorch -c nvidia -y

# Install SamGeo with text prompt support
pip install "segment-geospatial[text]" leafmap geopandas folium

# Run the detector
python debris_detector.py
```

## Files

| File | Description |
|------|-------------|
| `debris_detector.py` | Main Python script for debris detection |
| `debris_detection_notebook.ipynb` | Interactive Jupyter notebook |
| `noaa_imagery_downloader.py` | Tool to download NOAA post-hurricane imagery |
| `requirements.txt` | Python dependencies |
| `setup_and_run.sh` | Setup script for local installation |

## How It Works

1. **Download satellite imagery** for Pinellas County areas
2. **Initialize LangSAM** (Language + Segment Anything Model)
3. **Detect debris** using text prompts like "debris pile", "storm debris"
4. **Export results** as GeoJSON, Shapefile, or CSV for GIS/mapping

## Key Features

- **Text-based detection**: Describe what to find ("debris pile") instead of manual annotation
- **Multiple output formats**: GeoJSON, Shapefile, CSV
- **Interactive maps**: Visualize results with Leafmap/Folium
- **Batch processing**: Process multiple areas automatically

## NOAA Imagery Sources

For best results, use actual post-hurricane imagery from NOAA:

### Web Viewers
- **Hurricane Milton**: https://storms.ngs.noaa.gov/storms/milton/index.html
- **Hurricane Helene**: https://storms.ngs.noaa.gov/storms/helene/index.html

### AWS S3 (Bulk Download)
```bash
# List available imagery (no credentials needed)
aws s3 ls s3://maxar-opendata/events/HurricaneMilton-Oct24/ --no-sign-request

# Download specific tile
aws s3 cp s3://maxar-opendata/events/HurricaneMilton-Oct24/TILE_ID.tif ./imagery/ --no-sign-request
```

## Pinellas County Coverage

The application includes predefined bounding boxes for key areas:

| Area | Coordinates (W, S, E, N) |
|------|-------------------------|
| Clearwater Beach | -82.835, 27.965, -82.815, 27.985 |
| St. Pete Beach | -82.745, 27.715, -82.725, 27.735 |
| Treasure Island | -82.780, 27.760, -82.760, 27.780 |
| Indian Rocks Beach | -82.860, 27.880, -82.840, 27.900 |
| Dunedin | -82.795, 28.010, -82.775, 28.030 |
| Gulfport | -82.715, 27.740, -82.695, 27.760 |

## Detection Parameters

Adjust these for better results:

```python
BOX_THRESHOLD = 0.24   # Lower = more detections (may include false positives)
TEXT_THRESHOLD = 0.24  # Lower = more text matches
ZOOM = 18              # Higher = more detail (slower download)
```

## Effective Text Prompts

For debris detection, try:
- `debris pile`
- `storm debris`
- `construction debris`
- `rubble`
- `waste pile`
- `damaged materials`
- `yard debris`

## Output Format

The GeoJSON output includes:
- Polygon geometries for each detected debris pile
- Centroid coordinates (lat/lon)
- Detection confidence scores
- Area in square meters

Example output structure:
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": { "type": "Polygon", "coordinates": [...] },
      "properties": {
        "id": 1,
        "centroid_lat": 27.975,
        "centroid_lon": -82.825,
        "area_sqm": 45.2
      }
    }
  ]
}
```

## System Requirements

- **Python**: 3.10+
- **GPU**: Recommended (8GB+ VRAM) - NVIDIA CUDA or Apple MPS
- **RAM**: 16GB+ recommended
- **Storage**: 5GB+ for imagery and models

## License

- **SamGeo**: MIT License
- **Maxar Open Data**: CC BY-NC 4.0 (Non-commercial use)
- **NOAA Imagery**: Public domain

## Resources

- [SamGeo Documentation](https://samgeo.gishub.org/)
- [NOAA Storm Imagery](https://storms.ngs.noaa.gov/)
- [Segment Anything Model](https://segment-anything.com/)
- [Red Cross Disaster Services](https://www.redcross.org/about-us/our-work/disaster-relief.html)

## Support

For issues with:
- **SamGeo**: https://github.com/opengeos/segment-geospatial/issues
- **This application**: Open an issue in this repository
