# Web Scraper for Surf-Forecast: How to run the code?

### Download supporting software
1. Visual Studio Code
2. Git

### Create Virtual Environment
1. Download and install any python version. But we suggest to install Python=3.11
2. To create virtual environment:
    > python -m venv .venv-python
3. Activate the virtual environment
    > .venv-python\Scripts\activate

### Install the libraries
1. To install the required libraries for the script, use the requirements.txt:
    > pip install -r requirements.txt

### Run the script
1. Run the script: surf_forecast_webscrape.py
    > python surf_forecast_webscrape.py

### Convert JSON data to CSV
1. Run the script: extract_json_to_csv.py
    > python extract_json_to_csv.py