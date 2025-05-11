## Project Introduction

The objective of this project is to automate the extraction and structuring of vape product data from two e-commerce websites. The focus is on 
transforming unstructured product descriptions into a structured schema suitable for data analysis, product comparison, or downstream  applications.

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

The extracted product features are stored in the structured_output.json file present in the repository.
