import pandas as pd
import re
import sys

def process_file(filename):
    try:
        # Read the HDF5 file into a DataFrame
        df = pd.read_hdf(filename)
        print(f"File '{filename}' loaded successfully! It contains the following columns:")
        print(list(df.columns))
        
        # Rename columns
        df = df.rename(columns={'coord_x': 'x', 'coord_y': 'y', 'coord_z': 'z', 'material_id': 'type'})
        
        # Extract timestep from filename
        match = re.search(r'(\d+)(?=\.h5$)', filename)
        if match:
            timestep = match.group(1)
        else:
            raise ValueError("Timestep could not be extracted from the filename")
        
        num_atoms = len(df)

        # Box bounds
        box_bounds_x = df['x'].min(), df['x'].max()
        box_bounds_y = df['y'].min(), df['y'].max()
        box_bounds_z = df['z'].min(), df['z'].max()

        # Output filename
        liggghts_filename = filename.replace('.h5', '.liggghts')

        # Write the LIGGGHTS file
        with open(liggghts_filename, 'w') as f:
            f.write(f"ITEM: TIMESTEP\n{timestep}\n")
            f.write(f"ITEM: NUMBER OF ATOMS\n{num_atoms}\n")
            f.write("ITEM: BOX BOUNDS pp pp pp\n")
            f.write(f"{box_bounds_x[0]} {box_bounds_x[1]}\n")
            f.write(f"{box_bounds_y[0]} {box_bounds_y[1]}\n")
            f.write(f"{box_bounds_z[0]} {box_bounds_z[1]}\n")
            f.write("ITEM: ATOMS " + " ".join(df.columns) + "\n")
            for _, row in df.iterrows():
                f.write(" ".join(map(str, row.values)) + "\n")

        print(f"Exported '{liggghts_filename}' successfully.")

    except Exception as e:
        print(f"Error processing file '{filename}': {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python h5_to_liggghts.py particles*.h5")
        sys.exit(1)

    filenames = sys.argv[1:]

    for filename in filenames:
        process_file(filename)

if __name__ == "__main__":
    main()
