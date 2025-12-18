"""
NOAA Hurricane Milton/Helene Imagery Downloader
Downloads post-hurricane aerial imagery from NOAA's Big Data Program on AWS S3

Imagery source: s3://maxar-opendata/events/HurricaneMilton-Oct24/
License: Creative Commons Attribution Non-Commercial 4.0

For Pinellas County debris detection to support Red Cross relief efforts.
"""

import os
import subprocess
from pathlib import Path


class NOAAImageryDownloader:
    """
    Download NOAA/Maxar post-hurricane imagery from AWS S3.
    """

    # AWS S3 paths for hurricane imagery
    S3_SOURCES = {
        "milton": "s3://maxar-opendata/events/HurricaneMilton-Oct24/",
        "helene": "s3://maxar-opendata/events/Hurricane-Helene-Sept2024/"
    }

    # NOAA NGS Aerial Imagery Viewer URLs
    WEB_VIEWERS = {
        "milton": "https://storms.ngs.noaa.gov/storms/milton/index.html",
        "helene": "https://storms.ngs.noaa.gov/storms/helene/index.html"
    }

    def __init__(self, output_dir="./noaa_imagery"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def list_available_imagery(self, hurricane="milton"):
        """
        List available imagery files on S3 (requires AWS CLI).

        Args:
            hurricane: "milton" or "helene"
        """
        s3_path = self.S3_SOURCES.get(hurricane, self.S3_SOURCES["milton"])

        print(f"Listing imagery from: {s3_path}")
        print("(Requires AWS CLI to be installed and configured)")
        print()

        try:
            # List S3 bucket contents (no credentials needed for public buckets)
            result = subprocess.run(
                ["aws", "s3", "ls", s3_path, "--no-sign-request"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print("Available directories/files:")
                print(result.stdout)
            else:
                print(f"Error: {result.stderr}")
                print("\nAlternative: View imagery directly at:")
                print(f"  {self.WEB_VIEWERS.get(hurricane)}")

        except FileNotFoundError:
            print("AWS CLI not installed. Install with: brew install awscli")
            print("\nAlternative options:")
            print(f"1. View imagery online: {self.WEB_VIEWERS.get(hurricane)}")
            print("2. Use the ESRI World Imagery fallback in debris_detector.py")

    def download_tiles(self, hurricane="milton", prefix="", max_files=10):
        """
        Download imagery tiles from S3.

        Args:
            hurricane: "milton" or "helene"
            prefix: Subdirectory path within the bucket
            max_files: Maximum number of files to download
        """
        s3_path = self.S3_SOURCES.get(hurricane) + prefix

        print(f"Downloading from: {s3_path}")
        print(f"Output directory: {self.output_dir}")

        try:
            # Sync from S3 (no credentials needed for public buckets)
            cmd = [
                "aws", "s3", "sync",
                s3_path,
                str(self.output_dir / hurricane / prefix.replace("/", "_")),
                "--no-sign-request",
                "--exclude", "*",
                "--include", "*.tif",
                "--include", "*.TIF"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print("Download complete!")
                print(result.stdout)
            else:
                print(f"Error: {result.stderr}")

        except FileNotFoundError:
            print("AWS CLI not installed. Install with:")
            print("  macOS: brew install awscli")
            print("  pip: pip install awscli")

    def get_pinellas_county_tiles(self, hurricane="milton"):
        """
        Get imagery specifically covering Pinellas County, FL.
        Pinellas County coordinates: approximately 27.7-28.1°N, 82.6-82.9°W

        Note: This requires knowing the tile naming convention used by Maxar.
        The tiles are typically organized by date and geographic quadrant.
        """
        print("Pinellas County Imagery Tiles")
        print("=" * 50)
        print()
        print("Pinellas County Approximate Bounds:")
        print("  North: 28.1°N (near Tarpon Springs)")
        print("  South: 27.6°N (near St. Pete Beach)")
        print("  East:  82.6°W (near Tampa Bay)")
        print("  West:  82.9°W (Gulf of Mexico)")
        print()

        # List available tiles
        self.list_available_imagery(hurricane)

        print()
        print("Recommended approach:")
        print("1. Visit the NOAA imagery viewer to identify tile IDs for your area")
        print("2. Download specific tiles using: aws s3 cp s3://... ./output/")
        print()
        print(f"NOAA Viewer: {self.WEB_VIEWERS.get(hurricane)}")


def print_imagery_guide():
    """
    Print a guide on accessing NOAA/Maxar hurricane imagery.
    """
    guide = """
================================================================================
                    NOAA HURRICANE IMAGERY ACCESS GUIDE
================================================================================

SOURCES:

1. NOAA NGS Aerial Imagery Viewers (Web-based):
   - Hurricane Milton: https://storms.ngs.noaa.gov/storms/milton/index.html
   - Hurricane Helene: https://storms.ngs.noaa.gov/storms/helene/index.html

2. Maxar Open Data on AWS (Direct Download):
   - Hurricane Milton: s3://maxar-opendata/events/HurricaneMilton-Oct24/
   - Hurricane Helene: s3://maxar-opendata/events/Hurricane-Helene-Sept2024/

   Download with AWS CLI (no credentials needed):
   $ aws s3 ls s3://maxar-opendata/events/HurricaneMilton-Oct24/ --no-sign-request
   $ aws s3 cp s3://maxar-opendata/events/HurricaneMilton-Oct24/TILEID.tif ./output/ --no-sign-request

3. NOAA Big Data Program:
   https://www.noaa.gov/information-technology/open-data-dissemination

PINELLAS COUNTY COVERAGE:

Post-Hurricane Milton imagery was collected:
- October 11: Fort Desoto to Boca Grande (includes south Pinellas)
- October 13-14: Tampa Bay area (includes Pinellas County)

RECOMMENDED WORKFLOW:

1. Open the NOAA web viewer for your hurricane
2. Navigate to your area of interest in Pinellas County
3. Note the tile IDs or use the viewer's download feature
4. For bulk processing, use this script with the tile IDs

LICENSE:

Maxar Open Data is licensed under Creative Commons Attribution Non-Commercial 4.0
(CC BY-NC 4.0). Use for humanitarian and disaster response is encouraged.

================================================================================
"""
    print(guide)


if __name__ == "__main__":
    print_imagery_guide()

    print("\nChecking for available imagery...")
    print()

    downloader = NOAAImageryDownloader()
    downloader.get_pinellas_county_tiles("milton")
