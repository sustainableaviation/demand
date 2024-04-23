import os
import requests

airport = "LSZH"

url = "https://aerodatabox.p.rapidapi.com/airports/icao/{airport}/stats/routes/daily"

headers = {
    "X-RapidAPI-Key": "59a275298cmsh24590c15cf01d92p12e3a3jsn0f5baacc5959",
    "X-RapidAPI-Host": "aerodatabox.p.rapidapi.com"
}

response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Get the current directory
    current_directory = os.path.dirname(os.path.realpath(__file__))
    
    # Define the file path
    file_path = os.path.join(current_directory, "{airport}.json")
    
    # Write the JSON response to a file
    with open(file_path, "w") as file:
        file.write(response.text)
        
    print("JSON data saved to:", file_path)
else:
    print("Failed to retrieve data from the API:", response.status_code)