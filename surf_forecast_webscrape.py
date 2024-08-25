# Python 3.11
# import general library
import time
import os
import glob
from datetime import datetime
import pandas as pd
import random
import threading
import json
from dotenv import load_dotenv


# importing webdriver from selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

# global variables
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Change default download directory

URL = "https://www.surf-forecast.com/"
OUTPUT_FOLDER = r"C:\Users\jeeco\Downloads\SurfForecast"

# Change this for your selected country
COUNTRY="Philippines"

# Load environment variables from the .env file
load_dotenv()

class Task:

    def __init__(self):
        self.driver = None
        self.main_items = {}
        self.sub_items = []
        self.parent_path=None
        self.userame= os.getenv("USERNAME")
        self.password= os.getenv("PASSWORD")

    def write_json(self, data={}, filename="data"):
        # Writing JSON data to a file
        with open(f'{self.parent_path}/{filename}.json', 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4)

    def read_json(self, filename="data"):
        # Reading JSON data from a file
        with open(f'{self.parent_path}/{filename}.json', 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        return data

    def get_credentials(self):
        return [self.userame, self.password]

    def defineDriver(self):
        # Chrome driver specific version will be used base on the version of google/brave browser.
        s = Service(r"chromedriver-win64\chromedriver.exe")

        cOptions = webdriver.ChromeOptions()
        cOptions.add_argument("--headless") #disable browser pop-up. run in the background.
        cOptions.add_argument("--disable-extensions")
        cOptions.add_argument("--window-size=1420, 1080")
        cOptions.add_argument("--safebrowsing-disable-download-protection")
        cOptions.add_argument("safebrowsing-disable-extension-blacklist")

        self.driver = webdriver.Chrome(service=s, options=cOptions)

    def xpath(self, strings_xpath):
        while True:
            exist = self.check_xpath_exists(strings_xpath)
            if exist: break
            else:
                self.driver.refresh()
                time.sleep(2)

        result = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, strings_xpath)))
        result.click()


    def check_xpath_exists(self, xpath):
        try:
            element = self.driver.find_element(By.XPATH, xpath)
            return True
        except (NoSuchElementException, WebDriverException):
            return False
        except Exception as e:
            #print(f"Error in check_xpath_exists: {e}")
            return False
        


    def rerun_xpath(self, xp1, xp2):
        # Find all rows in the table body
        xp = xp1
        result = ''
        wexit = False
        while True:
            try:
                result = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, xp)))
                wexit = True
            except:
                xp = xp2
                pass

            if wexit: break
        return result
    
    def login(self):
        username = self.get_credentials()[0]
        password = self.get_credentials()[1]
        chk_counter = 0
        while True:
            try:

                if chk_counter >= 3 and chk_counter<5: # check if web html is successfully loaded. If not, then refresh.
                    self.driver.refresh()
                    chk_counter = 0
                    time.sleep(10)
                
                if chk_counter >= 5: # check if web html is successfully loaded. If not, then refresh.
                    self.driver.get("https://www.surf-forecast.com/sign_in")
                    chk_counter = 0
                    time.sleep(10)
                    

                time.sleep(5)
                
                usertext = self.driver.find_element(By.ID,'email')
                usertext.clear()
                usertext.send_keys(username)

                passwdtext = self.driver.find_element(By.ID,'password')
                passwdtext.clear()
                passwdtext.send_keys(password)

                passwdtext.send_keys(Keys.RETURN)
                time.sleep(5)
                break
            except Exception as e:   
                chk_counter += 1
                pass

    def get_listed_items(self, select_id):
        items=[]
        try:
            # Wait until the select element is present
            select_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, select_id))
            )

            # Get all options in the select element
            options = select_element.find_elements(By.TAG_NAME, "option")

            # Extract text and value from each option
            options_list = [(option.get_attribute('value'), option.text) for option in options]

            # Print the options
            for value, text in options_list:
                items.append({"value": str(value), "text": str(text)})

        finally:
            return items
        
    def set_filters(self, forecast="12days"):
        self.countries = self.get_listed_items("country_id")
        
        # FILTER: COUNTRY
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        for cnty in self.countries:
            if cnty.get('text') != COUNTRY: continue
            # Wait until the select element is present
            select_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "country_id"))
            )

            # Initialize the Select class with the select element
            select = Select(select_element)

            # Set the specific value (e.g., "2148" for Samar)
            select.select_by_value(cnty.get('value'))

            # FILTER: REGION
            # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            self.regions = self.get_listed_items("region_id")
        
            for reg in self.regions:
                print("\n","-----" * 30)
                print(f"region >> {reg}")
                # Wait until the select element is present
                select_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "region_id"))
                )

                # Initialize the Select class with the select element
                select = Select(select_element)

                # Set the specific value (e.g., "2148" for Samar)
                select.select_by_value(reg.get('value'))
                time.sleep(3)
                
                
                # FILTER: BREAK
                # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                self.breaks = self.get_listed_items("location_filename_part")
                for brk in self.breaks:
                    if brk.get('text') in ['Loading...']: 
                        time.sleep(3) 
                    

                self.breaks = self.get_listed_items("location_filename_part")
                for brk in self.breaks:
                    if brk.get('text') in ['Loading...']: time.sleep(2); continue
                    if brk.get('text') in ['Choose', 'Loading...']: time.sleep(2); continue

                    

                    print(f"\tbreaker >> {brk}")
                    # Wait until the select element is present
                    while True:
                        try:
                            select_element = WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.ID, "location_filename_part"))
                            )
                            break
                        except:
                            self.driver.refresh()
                            time.sleep(3)
                            pass 

                    # Initialize the Select class with the select element
                    select = Select(select_element)

                    # Set the specific value (e.g., "2148" for Samar)
                    select.select_by_value(brk.get('value'))
                    self.filter_country = cnty.get('text')
                    self.filter_region = reg.get('text')
                    self.filter_breaker = brk.get('text')
                    time.sleep(3)

                    if forecast == "hourly":
                        self.xpath('//*[@id="contdiv"]/div[1]/div[1]/ul/li[1]/ul/li[1]/a')

                    self.harvest_table()
                    try:
                        self.harvest_subtable_1()
                    except:
                        pass
                    
                




    def harvest_table(self):
        sub_items=[]
        # Locate the table by its XPath
        table_rows = self.driver.find_elements(By.XPATH, '//*[@id="forecast-table"]/div/table/tbody/tr')

        # Iterate over each row
        for row in table_rows:
            # Find all columns within the row
            columns_head = row.find_elements(By.TAG_NAME, 'th')
            columns = row.find_elements(By.TAG_NAME, 'td')
            
            # Extract text from each column
            row_head = [ch.text for ch in columns_head]
            row_data = [column.text for column in columns]

            if row_head[0] == "m, \u00b0C":
                # Locate the <td> element with the specific class
                head = row.find_elements(By.TAG_NAME, 'td')
                for h in head:
                    try:
                        btn = h.find_element(By.TAG_NAME, 'button')
                        btn.click()
                        time.sleep(0.5)
                    except:
                        pass
                

            if row_head[0] in [
                "Swell\nHeight Map\nSee all maps",]:

                # Locate the <td> element with the specific class
                maps = row.find_elements(By.TAG_NAME, 'td')
                
                source=[]
                for m in maps:
                    # Locate the <img> element within the <td>
                    img_element = m.find_elements(By.TAG_NAME, 'img')
                    for img in img_element:
                        source.append(img.get_attribute('src'))
                
                sub_items.append(
                        {
                            'head': row_head[0],
                            'rows': source
                        }
                    )

            elif row_head[0] in [
                "Wave\nGraph\n(?)",]:

                # Locate the <td> element with the specific class
                maps = row.find_elements(By.TAG_NAME, 'td')
                
                source=[]
                for m in maps:
                    
                    source.append(
                        {
                            "data-date": m.get_attribute('data-date'),
                            "data-swell-state": m.get_attribute('data-swell-state'),
                            "data-wind": m.get_attribute('data-wind'),
                            "data-wind-state": m.get_attribute('data-wind-state')
                        }
                    )
                
                sub_items.append(
                        {
                            'head': row_head[0],
                            'rows': source
                        }
                    )
            
            else:
                sub_items.append(
                        {
                            'head': row_head[0],
                            'rows': row_data
                        }
                    )
            
            
            
                
        # Locate the table by its XPath
        table_rows = self.driver.find_elements(By.XPATH, '//*[@id="forecast-table"]/div/table/tfoot/tr')

        # Iterate over each row
        for row in table_rows:
            # Find all columns within the row
            columns_head = row.find_elements(By.TAG_NAME, 'th')
            columns = row.find_elements(By.TAG_NAME, 'td')
            
            # Extract text from each column
            row_head = [ch.text for ch in columns_head]
            row_data = [column.text for column in columns]
            
            sub_items.append(
                    {
                        'head': row_head,
                        'rows': row_data
                    }
                )
        
        new_data = {
                        'country': self.filter_country,
                        'region': self.filter_region,
                        'break': self.filter_breaker,
                        'items': sub_items
                    }
            
        self.write_json(new_data, f"result_{self.filter_country}_{self.filter_region}_{self.filter_breaker}")


    def harvest_subtable_1(self):
        sub_items={
            "header": [],
            "items": []
        }

        while True:
            try:
                # Locate the table by its XPath
                table = self.driver.find_element(By.CSS_SELECTOR, '#contdiv > div.col-reverse > div.not_in_print > div:nth-child(3) > section > div > table')

                # Locate the <thead> element
                thead = table.find_element(By.TAG_NAME, 'thead')
                # Locate the <tr> within the <thead> and get all <th> elements
                headers = thead.find_elements(By.TAG_NAME, 'th')
                header_data = [header.text for header in headers]
                sub_items.get("header").append(header_data)

                # Locate the <tbody> element
                tbody = table.find_element(By.TAG_NAME, 'tbody')
                # Locate all <tr> elements within the <tbody>
                rows = tbody.find_elements(By.TAG_NAME, 'tr')

                # Extract data from each row
                for row in rows:
                    # Locate all <td> elements within the current row
                    cols = row.find_elements(By.TAG_NAME, 'td')
                    # Extract and print the text of each <td>
                    row_data = [col.text for col in cols]
                    sub_items.get("items").append(row_data)
                    
                self.write_json(sub_items, f"result_subtable_1_{self.filter_country}_{self.filter_region}_{self.filter_breaker}")
                break
            except:
                self.driver.refresh()
                
        

        
        



    def begin(self):
        print(">> Load website..")
        self.xpath('//*[@id="mainmenu"]/menu/li[8]/a')
        time.sleep(1)
        print(">> Attempt to Login..")
        self.login()
        time.sleep(1)
        print(">> Now begin to harvest data..")
        self.xpath('//*[@id="mainmenu"]/menu/li[2]/a')
        
        self.parent_path = f"{OUTPUT_FOLDER}/12_days_forecast"
        # Check if the folder exists
        if not os.path.exists(self.parent_path):
            # Create the folder
            os.makedirs(self.parent_path)
        self.set_filters()

        # NEXT > hourly forecast

        self.parent_path = f"{OUTPUT_FOLDER}/hourly_forecast"
        # Check if the folder exists
        if not os.path.exists(self.parent_path):
            # Create the folder
            os.makedirs(self.parent_path)
        self.set_filters(forecast="hourly")
        
        

    

if __name__ == "__main__":
    __tasks = Task()


    # Navigate to the website
    __tasks.defineDriver()
    __tasks.driver.command_executor.set_timeout(10)
    __tasks.driver.get(URL)
    

    try:

        __tasks.begin()
    except KeyboardInterrupt:
        print("Script interrupted by user.")
    except Exception as e:
        print(e)
    finally:
        __tasks.driver.quit()