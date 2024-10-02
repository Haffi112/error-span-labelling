import pandas as pd
import sys

# Check if input file is provided
if len(sys.argv) < 2:
    print("Usage: python remove_first_column.py input_file.csv")
    sys.exit(1)

# Input and output file names
input_file = sys.argv[1]
output_file = "output.csv"

# Read the CSV file
df = pd.read_csv(input_file)

# Drop the first column
df.drop(df.columns[0], axis=1, inplace=True)

# Save the result to a new CSV file
df.to_csv(output_file, index=False)

print(f"First column removed and saved to {output_file}")
