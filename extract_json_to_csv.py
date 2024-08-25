import csv
from collections import defaultdict
import json
import os
import glob
import re

JSON_DATA = r"C:\Users\jeeco\Downloads\SurfForecast\hourly_forecast"
OUTPUT_PATH = r"C:\Users\jeeco\Downloads\SurfForecast\CSV\hourly_forecast"

# Change this for your selected country
COUNTRY="Philippines"


class Task:
    def __init__(self) -> None:
        self.parent_path = None
    


    def read_json(self, filepath):
        # Reading JSON data from a file
        with open(filepath, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        return data

    def read_all_json_files(self):
        # Get a list of all JSON files in the directory
        json_files = glob.glob(os.path.join(JSON_DATA, f'result_{COUNTRY}*.json'))

        for filepath in json_files:
            data = self.read_json(filepath)
            # Process the data here
            self.begin(data)

    

    def begin(self, data={}):
        # Check if the data dictionary is empty
        if not data:
            return
        
        # Group items by row length
        grouped_items = defaultdict(list)

        n1 = data.get("country")
        n2 = data.get("region")
        n3= data.get("break")
        self.parent_path = f"{OUTPUT_PATH}/{n1}_{n2}_{n3}"
        # Check if the folder exists
        if not os.path.exists(self.parent_path):
            # Create the folder
            os.makedirs(self.parent_path)

        for item in data['items']:
            row_length = len(item['rows'])
            grouped_items[row_length].append(item)

        # Write each group to a separate CSV file
        for length, items in grouped_items.items():
            filename = f'{self.parent_path}/items_with_{length}_rows.csv'
            with open(filename, 'w', newline='', encoding='utf-8' ) as csvfile:
                writer = csv.writer(csvfile)
                # Write headers
                writer.writerow([item['head'] for item in items])
                # Write rows
                rows = zip(*[item['rows'] for item in items])
                
                writer.writerows(rows)



class JsonToCsvConverterForSubtable:
    def __init__(self, json_folder):
        self.json_folder = json_folder

    def extract_info_from_filename(self, filename):
        # Extract "Philippines", "West Luzon", "Turtle Head" from filename
        match = re.search(r"result_subtable_1_(.*?)_(.*?)_(.*?).json", filename)
        if match:
            return match.groups()
        return None, None, None

    def read_json(self, filepath):
        # Reading JSON data from a file
        with open(filepath, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        return data

    def save_to_csv(self, data, filename, path):
        # Extract header and items from the data
        header = data["header"][0]
        items = data["items"]

        # Create a CSV file with the same name as the JSON file
        csv_filename = filename.replace('.json', '.csv')
        with open(f"{path}/{csv_filename}", 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # Write header
            writer.writerow(header)
            # Write items (rows)
            writer.writerows(items)

        

    def process_json_files(self):
        # Process all JSON files in the folder
        # Get a list of all JSON files in the directory
        json_files = glob.glob(os.path.join(JSON_DATA, f'result_{COUNTRY}*.json'))

        for filename in os.listdir(self.json_folder):
            if filename.endswith('.json'):
                
                # Extract country, region, and break from the filename
                country, region, break_name = self.extract_info_from_filename(filename)
                #print(f"Processing: Country={country}, Region={region}, Break={break_name}")

                if filename == f"result_subtable_1_{country}_{region}_{break_name}.json":
                    filepath = os.path.join(self.json_folder, filename)

                    # Read the JSON data
                    data = self.read_json(filepath)
                    
                    # Save the data to a CSV file
                    path = f"{OUTPUT_PATH}/{country}_{region}_{break_name}"
                    self.save_to_csv(data, filename, path)


if __name__ == "__main__":
    __tasks = Task()
    __tasks.read_all_json_files()

    # Subtable
    __subtable_class = JsonToCsvConverterForSubtable(JSON_DATA)
    __subtable_class.process_json_files()