
import os 
import re
import time 
import csv 
import datetime
import pandas
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()

def setup_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no UI)
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu") 
    chrome_options.add_argument("--no-sandbox")  # Disable sandboxing (useful for some environments like Docker)
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
 
    return webdriver.Chrome(options=chrome_options)


def collect_data(stock_name , index ,driver):
    # TODO: 
    # Apply ------
    # Regular Trading Hours:
    # 9:30 a.m. to 4:00 p.m. Eastern Time . 
    # Extended Hours Trading:
    # Pre-market: Typically starts at 4:00 a.m. ET and can go until 9:30 a.m. ET. 
    # After-hours: Typically starts at 4:00 p.m. ET and can go until 8:00 p.m. ET. 
        
    base_url = os.getenv('BASE_URL')
    driver.get(f"{base_url}{stock_name}:{index}")
    
    combined_xpath = (
    "/html/body/c-wiz[2]/div/div[4]/div/main/div[2]/div[1]/c-wiz/div/div[1]/div/div[1]/div/div[1]/div/span/div/div | "
    "/html/body/c-wiz[2]/div/div[4]/div/main/div[2]/div[1]/c-wiz/div/div[1]/div/div[3]"
    )
   
    elements = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.XPATH, combined_xpath))
    )                                         
   
    elements = [elem.text for elem in elements]
    elements.extend(re.split('·', elements[1]))
    del elements[1]
    formatted_text = ["TSLA"]
    formatted_text.extend(([part.strip() for part in elements]))
    del formatted_text[-1]
   
    return formatted_text
            
def store_data(data, path):
    with open(path, mode='a', newline='', encoding='utf-8') as file:
        file.write(", ".join(data) + "\n") 


def main():
    
    driver = setup_browser()
    
    stock_name = "TSLA"
    index = "NASDAQ"
    
    now = datetime.date.today()
    # Monday_18__August_2025__12_00_AM
    start_datetime = now.strftime(f"%A_%d__%B_%Y__%I_%M_%p")
    start_filename = f'{start_datetime}.csv'
   
    # Create file and add headers
    headers = ['Share Name', 'Value', 'Datetime', 'Currency', 'Index'] 
    if not os.path.exists(f"{start_datetime}.csv"): 
        with open(start_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
    
    try: 
        while True:
            collected_data = collect_data(stock_name, index, driver)
            store_data(collected_data, start_filename)
            print(f"Data collected and stored: {collected_data}")
           
            time.sleep(60)
    except KeyboardInterrupt:
        print("Stopping tesla share value collection")
    finally:
        
        driver.quit()
        
        now = datetime.date.today()
        # Monday_18__August_2025__12_00_AM
        end_datetime = now.strftime(f"%A_%d__%B_%Y__%I_%M_%p")
        end_filename = f"{start_datetime}_to_{end_datetime}.csv"
        if os.path.exists(f"{start_datetime}.csv"):
            # update save file name to include end date
            os.rename(start_filename, end_filename)
            print(f"File renamed from {start_filename} to {end_filename}")
        else:
            print(f"The file {start_filename} does not exist.")
        
    
if __name__ == "__main__":
    main()