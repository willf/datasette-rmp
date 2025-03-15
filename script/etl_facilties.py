#!/usr/bin/env python3
# filepath: /Users/willf/projects/datasette-rmp/script/check_lat_lon.py
import csv
import sys
import signal

# Define bounding boxes for US and its territories
us_regions = {
    "Continental US": {"lat": (24.5, 49.5), "lon": (-125.0, -66.5)},
    "Alaska": {"lat": (51.2, 71.5), "lon": (-180.0, -130.0)},
    "Hawaii": {"lat": (18.5, 22.5), "lon": (-160.5, -154.5)},
    "Puerto Rico": {"lat": (17.5, 18.6), "lon": (-67.5, -65.0)},
    "Guam": {"lat": (13.2, 13.7), "lon": (144.6, 145.0)},
    "US Virgin Islands": {"lat": (17.6, 18.5), "lon": (-65.2, -64.5)},
    "American Samoa": {"lat": (-14.5, -14.1), "lon": (-171.0, -168.0)},
    "Northern Mariana Islands": {"lat": (14.0, 20.6), "lon": (144.5, 146.5)},
}


def guess_correct_coordinates(entry, us_regions):
    """
    Attempts to guess the correct coordinates for a suspicious entry.

    Parameters:
    entry: Dictionary containing the suspicious entry information
    us_regions: Dictionary of US region bounding boxes

    Returns:
    Dictionary with possible corrections
    """
    row = entry["entry"]
    corrections = []

    try:
        # Get the original coordinates
        try:
            lat = float(row["Latitude"])
            lon = float(row["Longitude"])
        except (ValueError, TypeError):
            return {"original": (row["Latitude"], row["Longitude"]), "suggestions": []}

        # Check for swapped coordinates
        swapped = (lon, lat)
        if is_within_us(swapped[0], swapped[1], us_regions):
            corrections.append(
                {
                    "type": "Swapped coordinates",
                    "coords": swapped,
                    "confidence": "Medium",
                }
            )

        # Check for sign errors
        sign_corrections = [(-lat, lon), (lat, -lon), (-lat, -lon)]

        for correction in sign_corrections:
            if is_within_us(correction[0], correction[1], us_regions):
                corrections.append(
                    {
                        "type": "Sign error",
                        "coords": correction,
                        "confidence": "High"
                        if abs(correction[0]) > 0 and abs(correction[1]) > 0
                        else "Medium",
                    }
                )

        # Check for decimal place errors (×10 or ÷10)
        decimal_corrections = [
            (lat / 10, lon),
            (lat, lon / 10),
            (lat / 10, lon / 10),
            (lat * 10, lon),
            (lat, lon * 10),
            (lat * 10, lon * 10),
        ]

        for correction in decimal_corrections:
            if is_within_us(correction[0], correction[1], us_regions):
                corrections.append(
                    {
                        "type": "Decimal place error",
                        "coords": correction,
                        "confidence": "Medium",
                    }
                )

        # Use state information for a generic guess
        state = row["State"]
        state_centers = {
            "AL": (32.8, -86.8),
            "AK": (64.2, -149.5),
            "AZ": (34.3, -111.7),
            "AR": (34.8, -92.2),
            "CA": (36.8, -119.4),
            "CO": (39.1, -105.4),
            "CT": (41.6, -72.7),
            "DE": (39.0, -75.5),
            "FL": (27.8, -81.5),
            "GA": (32.9, -83.4),
            "HI": (20.3, -156.4),
            "ID": (44.2, -114.5),
            "IL": (40.0, -89.0),
            "IN": (39.9, -86.3),
            "IA": (42.0, -93.5),
            "KS": (38.5, -98.0),
            "KY": (37.5, -85.3),
            "LA": (31.0, -92.0),
            "ME": (45.4, -69.0),
            "MD": (39.0, -76.7),
            "MA": (42.2, -71.5),
            "MI": (44.3, -85.4),
            "MN": (46.3, -94.3),
            "MS": (32.7, -89.7),
            "MO": (38.4, -92.3),
            "MT": (47.0, -109.6),
            "NE": (41.5, -99.8),
            "NV": (39.3, -116.6),
            "NH": (43.7, -71.6),
            "NJ": (40.1, -74.7),
            "NM": (34.4, -106.1),
            "NY": (42.9, -75.5),
            "NC": (35.6, -79.4),
            "ND": (47.5, -100.5),
            "OH": (40.4, -82.7),
            "OK": (35.6, -97.4),
            "OR": (43.9, -120.6),
            "PA": (40.9, -77.8),
            "RI": (41.7, -71.6),
            "SC": (33.9, -80.9),
            "SD": (44.4, -100.2),
            "TN": (35.9, -86.4),
            "TX": (31.5, -99.3),
            "UT": (39.3, -111.7),
            "VT": (44.0, -72.7),
            "VA": (37.8, -78.8),
            "WA": (47.4, -120.5),
            "WV": (38.6, -80.6),
            "WI": (44.3, -89.5),
            "WY": (42.8, -107.3),
            "DC": (38.9, -77.0),
            "PR": (18.2, -66.4),
            "GU": (13.5, 144.8),
            "VI": (18.3, -64.8),
            "AS": (-14.3, -170.0),
            "MP": (15.2, 145.8),
        }

        if state in state_centers:
            corrections.append(
                {
                    "type": "State center approximation",
                    "coords": state_centers[state],
                    "confidence": "Low",
                }
            )

        # Sort by confidence
        confidence_levels = {"High": 3, "Medium": 2, "Low": 1}
        corrections.sort(
            key=lambda x: confidence_levels.get(x["confidence"], 0), reverse=True
        )

        return {"original": (lat, lon), "suggestions": corrections}

    except Exception as e:
        return {
            "original": (
                row.get("Latitude", "unknown"),
                row.get("Longitude", "unknown"),
            ),
            "error": str(e),
            "suggestions": [],
        }


def is_within_us(lat, lon, us_regions):
    """Check if coordinates are within any US region"""
    if abs(lat) > 90 or abs(lon) > 180:
        return False

    for region, bounds in us_regions.items():
        lat_min, lat_max = bounds["lat"]
        lon_min, lon_max = bounds["lon"]

        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            return True

    return False


def is_suspicious_coordinate(lat, lon):
    """Check if coordinates are suspicious (out of US bounds)"""
    if abs(lat) > 90 or abs(lon) > 180:
        return True

    for region, bounds in us_regions.items():
        lat_min, lat_max = bounds["lat"]
        lon_min, lon_max = bounds["lon"]

        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            return False

    return True


def create_markdown_link(state_abbrev, facility_id):
    """Create a markdown link for the facility ID
    Looks like: https://github.com/edgi-govdata-archiving/epa-risk-management-plans/blob/main/reports/AK/100000013521.pdf
    """
    return f"[Report](https://github.com/edgi-govdata-archiving/epa-risk-management-plans/blob/main/reports/{state_abbrev}/{facility_id}.pdf)"


def main(include_corrections=False):
    # Read the CSV header
    header_line = sys.stdin.readline().strip()
    headers = header_line.split(",")

    # Create a CSV writer for the output
    writer = csv.writer(sys.stdout)

    # Write the header with additional columns
    if include_corrections:
        writer.writerow(
            ["Report"] + headers + ["changed", "confidence", "correction_type"]
        )
    else:
        writer.writerow(["Report"] + headers)

    for line in sys.stdin:
        # Read the CSV line
        line = line.strip()
        # add report link

        reader = csv.DictReader([header_line, line])
        for row in reader:
            lat = row.get("Latitude")
            lon = row.get("Longitude")
            try:
                lat = float(lat)
                lon = float(lon)
            except (ValueError, TypeError):
                lat = None
                lon = None
            row["Report"] = create_markdown_link(row["State"], row["EPA Facility ID"])
            row["changed"] = False
            row["confidence"] = "None"
            row["correction_type"] = "None"
            if is_suspicious_coordinate(lat, lon):
                # Mark as suspicious
                corrections = guess_correct_coordinates({"entry": row}, us_regions)
                first_correction = (
                    corrections["suggestions"][0]
                    if corrections["suggestions"]
                    else None
                )
                if first_correction:
                    new_lat, new_lon = first_correction["coords"]
                    confidence = first_correction["confidence"]
                    row["changed"] = True
                    row["confidence"] = confidence
                    row["Latitude"] = new_lat
                    row["Longitude"] = new_lon
                    row["correction_type"] = first_correction["type"]
            # add Report to the row
            new_headers = ["Report"] + headers
            # Write the row with additional columns

            if include_corrections:
                writer.writerow(
                    [row[key] for key in new_headers]
                    + [row["changed"], row["confidence"], row["correction_type"]]
                )
            else:
                writer.writerow([row[key] for key in new_headers])


if __name__ == "__main__":
    # Ignore SIGPIPE and handle BrokenPipeError
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    try:
        main()
    except BrokenPipeError:
        pass
