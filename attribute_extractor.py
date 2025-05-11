from dotenv import load_dotenv #Load the environemntal variables
load_dotenv()
from langchain_core.output_parsers import PydanticOutputParser #to get structured output
from langchain.output_parsers import OutputFixingParser #to get structured output if the pydantic model fails
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field #To define the custom validation strategy
from typing import Optional ,List
from langchain_groq import ChatGroq  #Load the groq hosted model
from tqdm import tqdm  # to show the progress bar while feature extraction
import json,os
import pandas as pd
from tenacity import retry, wait_exponential, stop_after_attempt #To invoke the llm at a gap of certain second 
import warnings
warnings.filterwarnings('ignore')

# Step-1 load the llm model
llm = ChatGroq(model_name = "llama-3.3-70b-Versatile",max_tokens= 1200) # Load the Groq Model

# Step-2 Define the Schema for the fields
# inherit the base pydantic model, and define schema and handel when the field is not availabe for product
class VapeProducts(BaseModel):
    brand: str = Field(description="Brand name of the product", default='n/a')   
    model_type: str = Field(description="The model of the product", default='n/a')
    flavor: List[str] = Field(description="Available flavors for the product", default=[])
    puff_count: Optional[int] = Field(description="Number of puffs", default=None)
    nicotine_strength: str = Field(description="Nicotine Strength in mg or %", default='n/a')
    battery_capacity: Optional[int] = Field(description='Battery capacity in mAh', default=None)
    coil_type: str = Field(description="Type of coil", default='n/a')

# Step-3 Initialize the Pydantic model and Outputfixingparser
# Base parser and auto-fix wrapper
base_parser = PydanticOutputParser(pydantic_object=VapeProducts)
parser = OutputFixingParser.from_llm(parser=base_parser, llm=llm)

# Step-4 Creating a promot template to guide the llm to generate based on the provided description and not to hallucinate
prompt = PromptTemplate(
    template="""Extract the following fields from the vape product description:
- brand
- model/type
- flavor
- puff_count
- nicotine_strength
- battery_capacity
- coil_type

If a value is not present, respond with "n/a" (as a string) or null for numeric fields.

Respond ONLY with a valid JSON object and NO extra text or formatting:
{format_instructions}

Product Description:
 {description}\n""",
    input_variables=["description"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

# Step-5 Creating a Chain by combining : promopt , llm model and the pydantic output parser
chain = prompt | llm | parser

# Step-6 Load the CSV files that contains the product detail of 2 seperate websites (Obtained after web scrapping)
df_vaperanger= pd.read_csv('vaperanger.csv')
df_vapewholesaleusa = pd.read_csv("vapewholesaleusa.csv")

# Step-7 Preprocessing the CSV files, since the the structure of web pages were different 
# to ensure both have 'inner_feature_description' by filling missing column with empty string
for df in [df_vaperanger, df_vapewholesaleusa]:
    if 'inner_feature_description' not in df.columns:
        df['inner_feature_description'] = ''
    df['title'] = df['title'].fillna('')
    df['inner_product_description'] = df['inner_product_description'].fillna('')
    df['inner_feature_description'] = df['inner_feature_description'].fillna('')
    df['product_link'] = df['product_link'].fillna('n/a')
    df["full_description"] = (
        df["title"].astype(str) + ". " +
        df["inner_product_description"].astype(str) + " " +
        df["inner_feature_description"].astype(str)
    )

# Step-8 combining the 2 dataframes/csv after the number of columns have been equal after preprocessing step 
combined_df = pd.concat([df_vaperanger, df_vapewholesaleusa], ignore_index=True)

# Step-9 Check and load the content of the 'structured_output.json' already exist , if not then create it
output_file = "structured_output.json" #To store the features extracted

# Load existing results if available
if os.path.exists(output_file):
    with open(output_file, "r") as f:
        results = json.load(f)  #load from .json file
    start_index = len(results)
    print(f"Already extracted up to index {start_index} , so continuing feature extraction from index {start_index+1}")
else:
    results = []
    start_index = 0

# Step-9 Invoking the llm to extract the feature
@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(2)) #invoke llm at interval of 2 second
def get_llm_output(description):
    return chain.invoke({"description": description}) #Invoking llm with feature description

# If the .json file has already store some records then Process only remaining rows of the CSV file (handles cases when some failures happen due to reaching the free tier limit for calling the groq model)
for i, row in tqdm(list(combined_df.iterrows())[start_index:], total=len(combined_df)-start_index, desc="Extracting structured data"):
    desc = row["full_description"]   #Extract feature description to pass to llm
    link = row.get("product_link", "n/a") #Extract product link , to later add to the .json/dictonary object
    try:
        output = get_llm_output(desc)
        structured_data = output.dict() #Convert the llm output (i.e pydnatic) to dictonary
    except Exception as e:  #Hnadle case when any failure happens due to reaching the llm token limit
        print(f"--Due to this exception the fields extracted are empty: {e}")
        structured_data = {
            "brand": "n/a",
            "model_type": "n/a",
            "flavor": [],
            "puff_count": None,
            "nicotine_strength": "n/a",
            "battery_capacity": None,
            "coil_type": "n/a"
        }

    structured_data["product_link"] = link #Add product link
    results.append(structured_data)

    # storing results to file after each round
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)