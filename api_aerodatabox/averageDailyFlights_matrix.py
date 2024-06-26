import os
import json
import pandas as pd
from scipy.sparse import csr_matrix, save_npz
from collections import defaultdict

# Base directory containing all the monthly folders
base_directory = '.'

# List of month folders
month_folders = [f'{i:02d}-{month}' for i, month in enumerate(
    ["January", "February", "March", "April", "May", "June",
     "July", "August", "September", "October", "November", "December"], 1)]

# Function to update the matrix
def update_matrix(data, origin, destination, avg_daily_flights):
    data[origin][destination] += float(avg_daily_flights)

# Loop through each monthly folder
for month_folder in month_folders:
    directory = os.path.join(base_directory, month_folder)
    
    # Initialize an empty dictionary for the matrix data
    data = defaultdict(lambda: defaultdict(float))
    
    if os.path.exists(directory) and os.path.isdir(directory):
        # Loop through all JSON files in the directory
        file_list = [f for f in os.listdir(directory) if f.endswith('.json')]
        
        for i, filename in enumerate(file_list):
            origin = filename.split('.')[0]
            filepath = os.path.join(directory, filename)
            
            with open(filepath, 'r') as file:
                try:
                    data_json = json.load(file)
                    for route in data_json.get('routes', []):
                        destination_info = route.get('destination', {})
                        destination = destination_info.get('icao')
                        avg_daily_flights = route.get('averageDailyFlights')
                        if destination and avg_daily_flights is not None:
                            update_matrix(data, origin, destination, avg_daily_flights)
                except json.JSONDecodeError:
                    print(f"Error decoding JSON from file {filename}")
            
            # Save the matrix periodically
            if (i + 1) % 100 == 0 or (i + 1) == len(file_list):
                print(f'Processed {i + 1}/{len(file_list)} files in {month_folder}...')
        
        # Create DataFrame from the data dictionary
        matrix_df = pd.DataFrame.from_dict(data, orient='index').fillna(0).astype(pd.SparseDtype("float", 0))
        
        # Convert DataFrame to sparse matrix and save
        sparse_matrix = csr_matrix(matrix_df.sparse.to_coo())
        save_npz(f'{month_folder}.npz', sparse_matrix)
        
        print(f'Saved matrix for {month_folder}.')

print('All files processed successfully.')
