from selenium import webdriver  # used to control the browser.
from selenium.webdriver.common.by import By  #Provides methods to locate elements on a webpage (e.g., by ID, name, class name, etc.).
from selenium.webdriver.common.keys import Keys  #Contains keyboard keys (e.g., ENTER, ESCAPE, etc.) to simulate typing actions.
import time  #Python's built-in time module used for delays (e.g., time.sleep() to wait for a webpage to load).
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

driver = webdriver.Chrome()
driver.get('https://vaperanger.com/')
time.sleep(5)


#Step-1: Id of the search bar and search the item
search_bar = driver.find_element(By.ID,'quick_search_form')  
search_bar.clear()
item = 'Strawberry vapes'     #Item to search
search_bar.send_keys(item)    #to search about on the text field
search_bar.send_keys(Keys.RETURN)

#Step-2: Since the website uses lazy_load() to load the product details , so 
# Number's of product to scrape
TARGET_PRODUCTS = 100

# dynamically Scroll slowly in increment order
last_height = driver.execute_script("return document.body.scrollHeight")
scroll_attempt = 0
max_attempts = 20  # to prevent infinite loops

while True:
    # Scroll down by 500 pixel at a time
    driver.execute_script("window.scrollBy(0, 500);")
    time.sleep(1.5)  # Wait for products to load

    # count if the required number of product have been loaded 
    req_area = driver.find_elements(By.XPATH, '//div[@class="snize-item clearfix "]')
    current_count = len(req_area)
    print(f"[INFO] Loaded products: {current_count}")

    if current_count >= TARGET_PRODUCTS:
        print("[INFO] Reached target number of products.")
        break

    # Check if new height is the same (no more loading)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        scroll_attempt += 1
        if scroll_attempt >= max_attempts:
            print("[INFO] Stopped scrolling after max attempts.")
            break
    else:
        scroll_attempt = 0  # Reset attempts if height increased

    last_height = new_height


# Step-3 : Scrape the basic details such as name,image_url from the main home page
title = []
price = []
image_url = []
category = []
stock_info = []
product_link= []
inner_product_description=[]
inner_feature_description=[]
table_data_list = []


try:
    #Area of the div/container for each product
    req_area = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, '//div[@class="snize-item clearfix "]')))

    for area in req_area:
        ##### To get the title 
        try:
            title_element = area.find_element(By.XPATH,'.//span[@class="snize-title"]')
            if title_element.text:
                title.append(title_element.text)
            else:
                title.append('n/a')
        except:
            title.append('n/a')

        ##### To get the IMAGE_URL
        try:
            image_element = area.find_element(By.XPATH, './/img[contains(@class, "snize-item-image")]')
            image_src = image_element.get_attribute('src')
            if image_src:
                image_url.append(image_src)
            else:
                image_url.append('n/a')
        except:
            image_url.append('n/a')


         ##### To get the PRODUCT_LINK / URL
        try:
            link = area.find_element(By.XPATH, './ancestor::a')
            link_src = link.get_attribute('href')
            if link_src:
                product_link.append(link_src)
            else:
                product_link.append('n/a')
        except:
            product_link.append('n/a')


            
except Exception as e :
    print(f"ERROR :{e}")

# Step-4 : Now scrape for each product page using the product link
main_window = driver.current_window_handle

# Iterate through each product link 
for link in product_link:
    if link == 'n/a':
        inner_product_description.append('n/a')
        inner_feature_description.append('n/a')
        table_data_list.append(['n/a'])
        continue
    try:
        driver.execute_script("window.open(arguments[0], '_blank');", link)
        time.sleep(1)
        driver.switch_to.window(driver.window_handles[-1])

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div'))  
        )

        # Scrape the detailed description about the product
        try:
            prod_description = driver.find_element(By.XPATH, '//div[@class="productView-top-description"]')
            if prod_description.text:
                inner_product_description.append(prod_description.text)
            else:
                inner_product_description.append('n/a')
        except:
            inner_product_description.append('n/a')

        # Scrape the features of the product
        try:
            ul_lists = driver.find_elements(By.XPATH, '//div[@class="rte"]')
            combined_list_items= []
            for ul in ul_lists:
                list_items = ul.find_elements(By.TAG_NAME, 'li')
                for item in list_items:
                    if item:
                        combined_list_items.append(item.text.strip())
                    else:
                        combined_list_items.append('n/a')

            inner_feature_description.append(combined_list_items)
        except:
            inner_feature_description.append('n/a')


        # Scrape the table thate contains key info: flavours,stock,price,Nicotine etc
        # to press the "See More" button to view the ENTIRE TABle
        try:
            see_more_btn = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, '//div[contains(@class,"see-more")]'))
            )
            see_more_btn.click()
            time.sleep(1)  # Let the table load
        except:
            pass  # Button not found or not clickable

    
         # --- Scrape table data with headers ---
        try:
            table = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, '//table'))
            )

            # Try to get headers from thead or first row
            try:
                header_row = table.find_element(By.XPATH, './/thead/tr')
                headers = [th.text.strip().lower() for th in header_row.find_elements(By.TAG_NAME, 'th')]
            except:
                # Fallback to first row as headers
                try:
                    first_row = table.find_element(By.XPATH, './/tr[1]')
                    headers = [td.text.strip().lower() for td in first_row.find_elements(By.TAG_NAME, 'td')]
                except:
                    headers = []

            # Collect data rows
            rows = table.find_elements(By.XPATH, './/tbody/tr')
            row_data = []
            for row in rows:
                cells = row.find_elements(By.XPATH, './td')
                row_text = ' | '.join(cell.text.strip() for cell in cells if cell.text.strip())
                if row_text:
                    row_data.append(row_text)

            # Save structured headers + rows
            table_data_list.append({'headers': headers, 'rows': row_data if row_data else ['n/a']})

        except:
            table_data_list.append({'headers': [], 'rows': ['n/a']})

            

        driver.close()
        driver.switch_to.window(main_window)

    except Exception as e:
        print(f"Error visiting product page: {link} - {e}")
        inner_product_description.append('n/a')
        driver.switch_to.window(main_window)
    

# Step-4 Conver the Scarpped data into a data frame (for later use to save as csv file)
df = pd.DataFrame({
    'title':title,
    'image_url':image_url,
    'product_link':product_link,
    'inner_product_description':inner_product_description,
    'inner_feature_description':inner_feature_description,
    'table_data_list':table_data_list
})


import re


# Conver the unstructured table data into structured format
def parse_table_data(table_data_entry):
    headers = table_data_entry.get('headers', [])
    rows = table_data_entry.get('rows', [])

    if rows == ['n/a'] or not headers:
        return ['n/a']

    structured = []
    #Split the table details based on '|'
    for row in rows:
        parts = [p.strip() for p in row.split('|')]

        if len(parts) == len(headers):
            item = dict(zip(headers, parts))

            if 'stock' in item:
                stock_match = re.search(r'\d+', item['stock'])
                item['stock'] = int(stock_match.group()) if stock_match else "Unavailable"

            structured.append(item)

    return structured

# Apply to entire column
df['table_details'] = df['table_data_list'].apply(parse_table_data)

#Drop unstructured column
df.drop(columns='table_data_list',inplace=True)

# Save the data as csv file
df.to_csv(f"vaperanger.csv",index=False)