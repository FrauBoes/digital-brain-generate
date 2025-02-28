import pandas as pd
import numpy as np
 
def interpolate_to_16_columns(input_file, output_file):
    """
    Transform a 4-column CSV file into a 16-column CSV file by interpolating values.
 
    Parameters:
        input_file (str): Path to the input CSV file with 4 columns.
        output_file (str): Path to save the transformed CSV file with 16 columns.
    """
    print('interpolate_data start')

    # Read the 4-column data
    data = pd.read_csv(input_file, header=None)
 
    # Ensure the data has exactly 4 columns
    if data.shape[1] != 4:
        raise ValueError("Input data must have exactly 4 columns.")
 
    # Create an empty list to store the expanded rows
    expanded_data = []
 
    # Interpolate each row to generate 16 columns
    for row in data.to_numpy():
        expanded_row = np.interp(np.linspace(0, 3, 16), np.arange(4), row)
        expanded_data.append(expanded_row)
 
    # Convert the expanded data back to a DataFrame
    expanded_df = pd.DataFrame(expanded_data, columns=[f'Col{i}' for i in range(16)])
 
    # Save the transformed data to the output file
    expanded_df.to_csv(output_file, index=False)
    print(f"... data successfully transformed and saved to {output_file}")
    print('interpolate_data end')

