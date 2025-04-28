import pandas as pd
import os

# --- USER INPUTS ---
input_txt = input("Enter the full path of the text file (e.g., /path/to/file.txt): ")
output_csv = input("Enter the full path of the output CSV file (e.g., /path/to/file.csv): ")

# Expand ~ if used
input_txt = os.path.expanduser(input_txt)
output_csv = os.path.expanduser(output_csv)

# Check if file exists
if not os.path.isfile(input_txt):
    raise FileNotFoundError(f"File not found: {input_txt}")

# --- READ FILE ---
# Read the whole file
with open(input_txt, 'r') as f:
    lines = f.readlines()

# --- FIND $Nodes block ---
try:
    start_idx = lines.index('$Nodes\n') + 2  # After $Nodes and number of nodes
    num_nodes = int(lines[start_idx - 1].strip())
    end_idx = start_idx + num_nodes
except ValueError:
    raise ValueError("No $Nodes section found in file!")

# --- PARSE DATA ---
# Only extract node data
node_lines = lines[start_idx:end_idx]
# Convert to DataFrame without adding column names
from io import StringIO
node_data = '\n'.join(node_lines)
df = pd.read_csv(StringIO(node_data), sep=r'\s+', header=None, engine='python')

# --- SAVE CSV ---
df.to_csv(output_csv, index=False, header=False)

print(f"Successfully extracted node data to {output_csv}.")
