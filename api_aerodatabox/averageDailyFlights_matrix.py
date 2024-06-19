import os
import json
import pandas as pd

# Directory containing the JSON files
directory = '01-January'

# Initialize an empty DataFrame for the matrix
matrix = pd.DataFrame()

# Dictionary to hold updates before applying them in batch
updates = {}

# Function to update the matrix
def update_matrix(origin, destination, avg_daily_flights):
    if origin not in updates:
        updates[origin] = {}
    updates[origin][destination] = float(avg_daily_flights)

# Loop through all JSON files in the directory
for filename in os.listdir(directory):
    if filename.endswith('.json'):
        origin = filename.split('.')[0]
        filepath = os.path.join(directory, filename)
        
        with open(filepath, 'r') as file:
            try:
                data = json.load(file)
                for route in data.get('routes', []):
                    destination_info = route.get('destination', {})
                    destination = destination_info.get('icao')
                    avg_daily_flights = route.get('averageDailyFlights')
                    if destination and avg_daily_flights is not None:
                        update_matrix(origin, destination, avg_daily_flights)
            except json.JSONDecodeError:
                print(f"Error decoding JSON from file {filename}")
        
        # Apply updates to the matrix
        if updates:
            update_df = pd.DataFrame(updates).T.fillna(0)
            matrix = pd.concat([matrix, update_df], axis=1).fillna(0)
            matrix = matrix.T.groupby(level=0).sum().T
            updates.clear()
        
        # Save the matrix to a CSV file
        matrix.to_csv('01-averageDailyFlights.csv')
        print(f'Processed {filename}')

print('All files processed successfully.')
