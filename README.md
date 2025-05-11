## Project Introduction

The objective of this project is to automate the extraction and structuring of vape product data from two e-commerce websites. The focus is on 
transforming unstructured product descriptions into a structured schema suitable for data analysis, product comparison, or downstream  applications.

---

##  Approach

### 1. Web Scraping using Selenium

  Approximately 100 vape product listings were scraped from each of two websites using Selenium. The scraping process targeted key product attributes, including:

  a. Product name

  b. Product description

  c. Key features

  d. Product link

  e. Image URL

  The extracted information are stored in CSV format for subsequent processing. (vaperanger.csv and vagewholesaleusa.csv)
  

  ### 2. Feature Extraction using a Large Language Model (LLM)
     
  To derive structured data from the scraped product descriptions, a Large Language Model was employed. The approach involved:

  a. Defining a Pydantic schema (VapeProducts) to represent structured fields such as brand, model type, flavor, puff count, nicotine strength, battery capacity, and coil type.

  b. Creating a prompt template that instructed the LLM to extract these attributes in a valid JSON format.

  c. Utilizing LangChain’s OutputFixingParser to enforce schema compliance and handle any formatting inconsistencies.

  d. Iterating through the product descriptions and applying the LLM pipeline to extract structured outputs, which were saved as a JSON file.

The extracted product features are stored in the 'structured_output.json' file present in the repository.


---
## Prerequisites

- Python 3.9 or higher
  
- [Create Groq API Key]( https://console.groq.com/keys)

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```
git clone https://github.com/prabal-k/WebScrapping_Feature_extraction
```

### 2. Open with VsCode and Create, Activate a Python Virtual Environment

### On Windows:
```
python -m venv venv

venv\Scripts\activate
```
### On Linux/macOS:
```
python3 -m venv venv

source venv/bin/activate
```
### 3. Install Required Dependencies
``
pip install -r requirements.txt
``
### 4. Configure Environment Variables

Create a .env file in the root folder with the following content:

GROQ_API_KEY = "your_groq_api_key_here"

### 5. Run the Script 

#### (Optional) A. Web Scraping and CSV Conversion

Note: The CSV files generated from the scraping process are already included in the repository. Running these scripts is optional unless updated data is required.

Scrapping the website : https://vaperanger.com/

```
python scrapper_vaperanger.py

```

Scrapping the website : https://vapewholesaleusa.com/

```
python scrapper_vapewholesaleausa.py

```

#### (Optional) b. For feature extractiong using llm

Note: The 'structured_output.json' file after extracting the features is already included in the repository. Running these scripts is optional unless updated data is required.

````
python attribute_extractor.py
````

---

## Snapshots of the extracted features ('structured_output.json')


![Image](https://github.com/user-attachments/assets/ae0a6bb4-44a6-45e0-b2b3-3bcf27d6dba0)


![Image](https://github.com/user-attachments/assets/9a535dc0-205f-4fe8-9e62-13959d7ce27d)
