"""
Debris Pile Detection for Hurricane Relief - Pinellas County
Uses SamGeo (Segment Anything Model for Geospatial Data) to identify debris piles
from post-hurricane satellite imagery to help Red Cross target relief efforts.

Hurricane Milton (Oct 2024) and Helene imagery from NOAA/Maxar
"""

import os
from pathlib import Path

# Check for GPU availability
try:
    import torch
    GPU_AVAILABLE = torch.cuda.is_available()
    if GPU_AVAILABLE:
        print(f"GPU detected: {torch.cuda.get_device_name(0)}")
    else:
        print("No GPU detected - will use CPU (slower processing)")
except ImportError:
    GPU_AVAILABLE = False
    print("PyTorch not installed yet")


class DebrisDetector:
    """
    Detect debris piles in satellite imagery using SamGeo with text prompts.
    Designed for post-hurricane damage assessment in Pinellas County, FL.
    """

    def __init__(self, output_dir="./output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.sam = None
        self.lang_sam = None

    def initialize_model(self, use_text_prompts=True):
        """
        Initialize the SAM model for segmentation.

        Args:
            use_text_prompts: If True, use LangSAM for text-based detection
        """
        if use_text_prompts:
            from samgeo.text_sam import LangSAM
            self.lang_sam = LangSAM()
            print("LangSAM initialized for text-prompt based detection")
        else:
            from samgeo import SamGeo
            self.sam = SamGeo(
                model_type="vit_h",  # Highest accuracy model
                automatic=True,
                device="cuda" if GPU_AVAILABLE else "cpu"
            )
            print("SamGeo initialized for automatic segmentation")

    def detect_debris_with_text(self, image_path, output_path=None,
                                 text_prompts=None, box_threshold=0.24,
                                 text_threshold=0.24):
        """
        Detect debris piles using text prompts.

        Args:
            image_path: Path to satellite image (GeoTIFF)
            output_path: Path for output shapefile/GeoJSON
            text_prompts: List of text descriptions to search for
            box_threshold: Confidence threshold for bounding boxes
            text_threshold: Confidence threshold for text matching

        Returns:
            Path to output vector file with detected debris locations
        """
        if self.lang_sam is None:
            self.initialize_model(use_text_prompts=True)

        # Default prompts optimized for debris detection
        if text_prompts is None:
            text_prompts = [
                "debris pile",
                "construction debris",
                "storm debris",
                "waste pile",
                "rubble pile",
                "trash pile",
                "damaged materials",
                "hurricane debris"
            ]

        if output_path is None:
            output_path = self.output_dir / "debris_detected.geojson"

        print(f"Detecting debris in: {image_path}")
        print(f"Using text prompts: {text_prompts}")

        # Run detection for each prompt and combine results
        all_masks = []
        for prompt in text_prompts:
            print(f"  Searching for: '{prompt}'...")
            try:
                self.lang_sam.predict(
                    image=str(image_path),
                    text_prompt=prompt,
                    box_threshold=box_threshold,
                    text_threshold=text_threshold,
                )
                # Save intermediate results
                prompt_output = self.output_dir / f"debris_{prompt.replace(' ', '_')}.tif"
                self.lang_sam.save_masks(
                    output=str(prompt_output),
                    dtype="uint8"
                )
                all_masks.append(prompt_output)
            except Exception as e:
                print(f"  Warning: No matches for '{prompt}': {e}")

        # Convert to vector format for GIS use
        if all_masks:
            self.lang_sam.raster_to_vector(
                str(all_masks[-1]),  # Use last successful mask
                str(output_path)
            )
            print(f"Results saved to: {output_path}")

        return output_path

    def detect_debris_automatic(self, image_path, output_path=None):
        """
        Automatic segmentation - detects all objects, then filter for debris.
        Useful when text prompts aren't specific enough.

        Args:
            image_path: Path to satellite image (GeoTIFF)
            output_path: Path for output vector file

        Returns:
            Path to output vector file
        """
        if self.sam is None:
            self.initialize_model(use_text_prompts=False)

        if output_path is None:
            output_path = self.output_dir / "all_segments.geojson"

        mask_path = self.output_dir / "masks.tif"

        print(f"Running automatic segmentation on: {image_path}")

        # Generate all masks
        self.sam.generate(
            source=str(image_path),
            output=str(mask_path),
            batch=True,
            foreground=True,
            erosion_kernel=(3, 3),
            mask_multiplier=255
        )

        # Convert to vector
        self.sam.raster_to_vector(
            str(mask_path),
            str(output_path)
        )

        print(f"Segmentation complete. Results: {output_path}")
        return output_path

    def download_noaa_imagery(self, bbox, output_path=None, source="milton"):
        """
        Download NOAA post-hurricane imagery for a bounding box.

        Args:
            bbox: Bounding box [west, south, east, north] in WGS84
            output_path: Where to save the imagery
            source: "milton" or "helene"

        Returns:
            Path to downloaded imagery
        """
        from samgeo import tms_to_geotiff

        if output_path is None:
            output_path = self.output_dir / f"noaa_{source}_imagery.tif"

        # NOAA imagery tile services
        # Note: These are example URLs - actual NOAA tiles may require
        # accessing through their official portals
        tms_sources = {
            "milton": "https://tiles.arcgis.com/tiles/C8EMgrsFcRFL6LrL/arcgis/rest/services/Milton_Imagery/MapServer/tile/{z}/{y}/{x}",
            "helene": "https://tiles.arcgis.com/tiles/C8EMgrsFcRFL6LrL/arcgis/rest/services/Helene_Imagery/MapServer/tile/{z}/{y}/{x}",
            # Fallback to standard satellite imagery
            "esri": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
        }

        tms_url = tms_sources.get(source, tms_sources["esri"])

        print(f"Downloading {source} imagery for bbox: {bbox}")

        try:
            tms_to_geotiff(
                output=str(output_path),
                bbox=bbox,
                zoom=18,  # High resolution for debris detection
                source=tms_url,
                quiet=False
            )
            print(f"Imagery saved to: {output_path}")
            return output_path
        except Exception as e:
            print(f"Error downloading imagery: {e}")
            print("Try using ESRI World Imagery as fallback...")
            tms_to_geotiff(
                output=str(output_path),
                bbox=bbox,
                zoom=18,
                source=tms_sources["esri"],
                quiet=False
            )
            return output_path

    def create_interactive_map(self, geojson_path, center=None):
        """
        Create an interactive map showing detected debris piles.

        Args:
            geojson_path: Path to debris detection results
            center: Map center [lat, lon], defaults to Pinellas County

        Returns:
            Folium map object
        """
        import folium
        import geopandas as gpd

        # Default to Pinellas County, FL
        if center is None:
            center = [27.9, -82.7]  # Pinellas County approximate center

        # Create base map
        m = folium.Map(
            location=center,
            zoom_start=14,
            tiles="OpenStreetMap"
        )

        # Add satellite imagery layer
        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri",
            name="Satellite",
            overlay=False
        ).add_to(m)

        # Load and add debris detection results
        if Path(geojson_path).exists():
            gdf = gpd.read_file(geojson_path)

            # Style for debris polygons
            style_function = lambda x: {
                'fillColor': '#ff0000',
                'color': '#ff0000',
                'weight': 2,
                'fillOpacity': 0.5
            }

            folium.GeoJson(
                gdf,
                name="Detected Debris Piles",
                style_function=style_function,
                tooltip=folium.GeoJsonTooltip(
                    fields=['id'] if 'id' in gdf.columns else [],
                    aliases=['Debris ID:']
                )
            ).add_to(m)

            print(f"Added {len(gdf)} debris polygons to map")

        # Add layer control
        folium.LayerControl().add_to(m)

        # Save map
        map_path = self.output_dir / "debris_map.html"
        m.save(str(map_path))
        print(f"Interactive map saved to: {map_path}")

        return m


def main():
    """
    Main workflow for debris detection in Pinellas County.
    """
    print("=" * 60)
    print("DEBRIS DETECTION FOR HURRICANE RELIEF")
    print("Pinellas County, FL - Post Hurricane Milton/Helene")
    print("=" * 60)

    # Initialize detector
    detector = DebrisDetector(output_dir="./debris_output")

    # Pinellas County bounding boxes for key affected areas
    # These are approximate coordinates - adjust as needed
    PINELLAS_AREAS = {
        "clearwater_beach": [-82.835, 27.965, -82.815, 27.985],
        "st_pete_beach": [-82.745, 27.715, -82.725, 27.735],
        "treasure_island": [-82.780, 27.760, -82.760, 27.780],
        "indian_rocks": [-82.860, 27.880, -82.840, 27.900],
        "dunedin": [-82.795, 28.010, -82.775, 28.030],
        "largo": [-82.795, 27.900, -82.775, 27.920],
        "pinellas_park": [-82.715, 27.835, -82.695, 27.855],
    }

    # Example: Process a specific area
    area_name = "clearwater_beach"
    bbox = PINELLAS_AREAS[area_name]

    print(f"\nProcessing area: {area_name}")
    print(f"Bounding box: {bbox}")

    # Step 1: Download satellite imagery
    print("\n[Step 1] Downloading satellite imagery...")
    imagery_path = detector.download_noaa_imagery(
        bbox=bbox,
        source="esri"  # Use ESRI as fallback; change to "milton" when NOAA tiles available
    )

    # Step 2: Run debris detection with text prompts
    print("\n[Step 2] Detecting debris piles...")
    debris_path = detector.detect_debris_with_text(
        image_path=imagery_path,
        text_prompts=[
            "debris pile",
            "storm debris",
            "construction debris",
            "rubble",
            "waste pile"
        ]
    )

    # Step 3: Create interactive map for Red Cross
    print("\n[Step 3] Creating interactive map...")
    detector.create_interactive_map(debris_path)

    print("\n" + "=" * 60)
    print("DETECTION COMPLETE")
    print("=" * 60)
    print(f"Output directory: {detector.output_dir}")
    print("\nFiles created:")
    for f in detector.output_dir.iterdir():
        print(f"  - {f.name}")
    print("\nOpen debris_map.html in a browser to view results")


if __name__ == "__main__":
    main()
