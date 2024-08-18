import json
import requests
import os
import glob
import re


JSON_DATA = r"F:\PROGRAMMING\Python Tutorial\WEBSCRAPE\Surf Forecast\assets\hourly_forecast"
OUTPUT_PATH = r"F:\PROGRAMMING\Python Tutorial\WEBSCRAPE\Surf Forecast\images\hourly_forecast"



class JsonToImage:
    def __init__(self, json_folder):
        self.json_folder = json_folder

    def extract_info_from_filename(self, filename):
        # Extract "Philippines", "West Luzon", "Turtle Head" from filename
        match = re.search(r"result_(.*?)_(.*?)_(.*?).json", filename)
        if match:
            return match.groups()
        return None, None, None

    def read_json(self, filepath):
        # Reading JSON data from a file
        with open(filepath, 'r') as json_file:
            data = json.load(json_file)
        return data
        

    def process_json_files(self):
        # Process all JSON files in the folder

        for filename in os.listdir(self.json_folder):
            if filename.endswith('.json'):
                
                # Extract country, region, and break from the filename
                country, region, break_name = self.extract_info_from_filename(filename)
                #print(f"Processing: Country={country}, Region={region}, Break={break_name}")

                if filename == f"result_{country}_{region}_{break_name}.json":
                    print(f"[{filename}]")
                    filepath = os.path.join(self.json_folder, filename)

                    # Read the JSON data
                    data = self.read_json(filepath)
                    
                    # Save the data to a CSV file
                    path = f"{OUTPUT_PATH}/{country}_{region}_{break_name}"
                    self.image_downloader(data,path)
                    print("\n")



    def image_downloader(self, data, path):
        # Create a folder to save images
        os.makedirs(path, exist_ok=True)

        items = data.get("items")
        
        
        for item in items:
            if item.get("head") == "Swell\nHeight Map\nSee all maps":
                
                # Download and save images
                for index, url in enumerate(item['rows']):
                    response = requests.get(url)
                    if response.status_code == 200:

                        filename = url.split('/')[-1]
                        with open(f'{path}/{filename}', 'wb') as img_file:
                            img_file.write(response.content)
                        print("----" * 10)
                        print("\t-->",filename)
                
        



if __name__ == "__main__":
    __class_json2image = JsonToImage(JSON_DATA)
    __class_json2image.process_json_files()