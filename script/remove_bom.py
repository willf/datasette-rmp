import codecs

# File path
file_path = "/Users/willf/projects/datasette-rmp/data/Combined.csv"

# Read the file and remove BOM if it exists
with codecs.open(file_path, "r", encoding="utf-8-sig") as file:
    content = file.read()

# Write the cleaned content back to the file
with open(file_path, "w", encoding="utf-8") as file:
    file.write(content)

print(f"BOM removed from {file_path}")
