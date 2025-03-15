import csv

# Input and output file paths
input_file = "/Users/willf/projects/datasette-rmp/data/Combined.csv"
output_file_chemicals = "/Users/willf/projects/datasette-rmp/data/Chemicals.csv"
output_file_naics = "/Users/willf/projects/datasette-rmp/data/NAICS.csv"

# Open the input CSV file
with open(input_file, mode="r", newline="", encoding="utf-8") as infile:
    reader = csv.DictReader(infile)

    # Open the output CSV file for chemicals
    with open(
        output_file_chemicals, mode="w", newline="", encoding="utf-8"
    ) as outfile_chemicals:
        writer_chemicals = csv.writer(outfile_chemicals)

        # Write the header for the output CSV file for chemicals
        writer_chemicals.writerow(["EPA Facility ID", "Chemical"])

        # Open the output CSV file for NAICS codes
        with open(
            output_file_naics, mode="w", newline="", encoding="utf-8"
        ) as outfile_naics:
            writer_naics = csv.writer(outfile_naics)

            # Write the header for the output CSV file for NAICS codes
            writer_naics.writerow(["EPA Facility ID", "NAICS Code"])

            # Iterate through each row in the input CSV file
            for i, row in enumerate(reader):
                # Print the progress
                print(f"Processing row {i + 1} {row}")
                # Split the Chemical(s) column by comma
                chemicals = row["Chemical(s)"].split(", ")

                # Write each chemical with the corresponding EPA Facility ID
                for chemical in chemicals:
                    writer_chemicals.writerow([row["EPA Facility ID"], chemical])

                # Split the NAICS Code(s) column by comma
                naics_codes = row["NAICS Code(s)"].split(", ")

                # Write each NAICS code with the corresponding EPA Facility ID
                for naics_code in naics_codes:
                    writer_naics.writerow([row["EPA Facility ID"], naics_code])

print(f"New CSV files created: {output_file_chemicals} and {output_file_naics}")
