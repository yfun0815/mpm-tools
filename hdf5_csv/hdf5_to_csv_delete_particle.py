import pandas as pd
import sys

def main():
    if len(sys.argv) < 3:
        print("Usage: python hdf5_to_csv_delete_particle.py <h5_file> <id1> [<id2> <id3> ...]")
        return

    h5_filename = sys.argv[1]
    particle_ids_to_delete = set(map(int, sys.argv[2:]))

    try:
        with pd.HDFStore(h5_filename) as store:
            keys = store.keys()
            if len(keys) != 1:
                print(f"Error: Expected exactly one key in HDF5 file, found: {keys}")
                return
            key = keys[0]
        
        df = pd.read_hdf(h5_filename, key=key)

        if 'id' not in df.columns:
            print("Error: No 'id' column found in the data.")
            return

        original_count = len(df)
        df = df[~df['id'].isin(particle_ids_to_delete)].reset_index(drop=True)
        new_count = len(df)

        df['id'] = range(len(df))

        print(f"Deleted particles: {sorted(particle_ids_to_delete)}")
        print(f"Remaining particles: {new_count} (originally {original_count})")

        csv_filename = h5_filename.replace('.h5', f'.csv')
        df.to_csv(csv_filename, index=False)
        print(f"Exported to CSV: {csv_filename}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

