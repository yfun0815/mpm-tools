import pandas as pd
import re

def main():
    filename = input("Please enter the HDF5 file name: ")
    try:
        # Read the HDF5 file into a DataFrame
        df = pd.read_hdf(filename)
        print("File loaded successfully! It contains the following columns:")
        print(list(df.columns))  # Print column names in the file
        
        # Rename columns 'coord_x', 'coord_y', 'coord_z' to 'x', 'y', 'z' and 'material_id' to 'type'
        df = df.rename(columns={'coord_x': 'x', 'coord_y': 'y', 'coord_z': 'z', 'material_id': 'type'})
        
        # Extract the timestep from the filename (assumes filename like 'twophase_particles09900.h5')
        match = re.search(r'(\d+)(?=.h5$)', filename)  # Correct regex to match digits before '.h5'
        if match:
            timestep = match.group(1)  # Get the matched number (e.g., '09900')
        else:
            raise ValueError("Timestep could not be extracted from the filename")
        
        # Get the number of atoms (particles)
        num_atoms = len(df)

        # Calculate the box bounds dynamically based on the min and max of x, y, z
        box_bounds_x = df['x'].min(), df['x'].max()
        box_bounds_y = df['y'].min(), df['y'].max()
        box_bounds_z = df['z'].min(), df['z'].max()

        # Prepare the LIGGGHTS file name
        liggghts_filename = filename.replace('.h5', '.liggghts')

        # Write the LIGGGHTS file
        with open(liggghts_filename, 'w') as f:
            # Write TIMESTEP
            f.write(f"ITEM: TIMESTEP\n{timestep}\n")
            
            # Write NUMBER OF ATOMS
            f.write(f"ITEM: NUMBER OF ATOMS\n{num_atoms}\n")
            
            # Write BOX BOUNDS
            f.write("ITEM: BOX BOUNDS pp pp pp\n")
            f.write(f"{box_bounds_x[0]} {box_bounds_x[1]}\n")
            f.write(f"{box_bounds_y[0]} {box_bounds_y[1]}\n")
            f.write(f"{box_bounds_z[0]} {box_bounds_z[1]}\n")
            
            # Write ATOMS line (this line will reflect the columns in the DataFrame)
            f.write("ITEM: ATOMS ")
            f.write(" ".join(list(df.columns)) + "\n")
            
            # Write the particle data
            for index, row in df.iterrows():
                f.write(" ".join(map(str, row.values)) + "\n")

        print(f"Data has been exported to LIGGGHTS file: {liggghts_filename}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
