import pandas as pd

def main():
    filename = input("Please enter the HDF5 file name: ")
    try:
        df = pd.read_hdf(filename)
        print("File loaded successfully! It contains the following columns:")
        print(list(df.columns))

        csv_filename = filename.replace('.h5', '.csv')
        df.to_csv(csv_filename, index=False)
        print(f"Data has been exported to CSV file: {csv_filename}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

