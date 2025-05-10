from selenium import webdriver  # used to control the browser.
from selenium.webdriver.common.by import By  #Provides methods to locate elements on a webpage (e.g., by ID, name, class name, etc.).
from selenium.webdriver.common.keys import Keys  #Contains keyboard keys (e.g., ENTER, ESCAPE, etc.) to simulate typing actions.
import time  #Python's built-in time module used for delays (e.g., time.sleep() to wait for a webpage to load).
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

driver = webdriver.Chrome()
driver.get('https://vapewholesaleusa.com/')
time.sleep(5)

#Step-1: Id of the search bar and search the item
search_bar = driver.find_element(By.ID,'search')   #Id of the search bar
search_bar.clear()
item = 'vapes'  #Item to search
search_bar.send_keys(item)                          ## to search about on the text field
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
    driver.execute_script("window.scrollBy(0, 200);")
    time.sleep(1.5)  # Wait for products to load

    # count if the required number of product have been loaded 
    req_area = driver.find_elements(By.XPATH, '//div[@class="product-item-info hover-animation-none"]')
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
                EC.presence_of_all_elements_located((By.XPATH, '//div[@class="product-item-info hover-animation-none"]')))

    for area in req_area:
        ##### To get the title 
        try:
            title_element = area.find_element(By.XPATH,'.//h2[@class="product name product-item-name"]')
            if title_element.text:
                title.append(title_element.text)
            else:
                title.append('n/a')
        except:
            title.append('n/a')

        ##### To get the IMAGE_URL
        try:
            image_element = area.find_element(By.XPATH, './/img[@class="product-image-photo "]')
            image_src = image_element.get_attribute('src')
            if image_src:
                image_url.append(image_src)
            else:
                image_url.append('n/a')
        except:
            image_url.append('n/a')


         ##### To get the PRODUCT_LINK / URL
        try:
            link = area.find_element(By.XPATH, './/a[@class="product-item-link"]')
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

# --- PRODUCT PAGE SCRAPING ---
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
            prod_description = driver.find_element(By.XPATH, '//div[@class="product attribute description"]')
            if prod_description.text:
                inner_product_description.append(prod_description.text)
            else:
                inner_product_description.append('n/a')
        except:
            inner_product_description.append('n/a')

    # Scrape the table thate contains key info: flavours,stock,price,Nicotine etc
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

            # getting data rows 
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
# as the number of table headers != the number of content so , preprocessing
import pandas as pd
df = pd.DataFrame({
    'title':title,
    'image_url':image_url,
    'product_link':product_link,
    'inner_product_description':inner_product_description,
    'table_data_list':table_data_list
})


# Handle case when the number of columns in table is not equal to table content
import re

def parse_table_data(table_data_entry):
    raw_headers = table_data_entry.get('headers', [])
    rows = table_data_entry.get('rows', [])

    if rows == ['n/a'] or not raw_headers:
        return ['n/a']

    # Manually filter headers to ignore blanks and 'qty'
    cleaned_headers = [h.strip().lower() for h in raw_headers if h.strip() and h.strip().lower() != 'qty']

    if not cleaned_headers or len(cleaned_headers) > 5:
        cleaned_headers = cleaned_headers[:5]

    structured = []
    for row in rows:
        parts = [p.strip() for p in row.split('|')]

        if len(parts) != len(cleaned_headers):
            continue  # Skip malformed rows

        item = dict(zip(cleaned_headers, parts))

        # Type conversions
        for key in item:
            if key == 'availability':
                match = re.search(r'\d+', item[key])
                item[key] = int(match.group()) if match else "Unavailable"
            # Unit price to float
            elif key == 'unit price':
                match = re.search(r'\d+(\.\d+)?', item[key])
                item[key] = float(match.group()) if match else None
            elif key == 'subtotal' and item[key] in {'$0.00', '0', '0.00'}:
                item[key] = None

        # Remove subtotal as it is not required
        item = {k: v for k, v in item.items() if v is not None}

        structured.append(item)

    return structured


# Apply to entire column
df['table_details'] = df['table_data_list'].apply(parse_table_data)
df.drop(columns=['table_data_list'],inplace=True)
df.to_csv(f'vapewholesaleusa.csv',index=False)
