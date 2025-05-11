import os
from dotenv import load_dotenv
load_dotenv()
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field # To define the custom validation strategy
from typing import Optional ,List
from langchain_groq import ChatGroq
from tqdm import tqdm  # For progress bar
import json,os
import pandas as pd

llm = ChatGroq(model_name = "Llama-3.3-70b-Versatile",max_tokens= 1200) # Load the Groq Model

# inherit the base pydantic model

class VapeProducts(BaseModel):
    brand: str = Field(description="Brand name of the product", default='n/a')
    model_type: str = Field(description="The model of the product", default='n/a')
    flavor: List[str] = Field(description="Available flavors for the product", default=None)
    puff_count: int = Field(description="Number of puffs", default=None)
    nicotine_strength: str = Field(description="Nicotine Strength in mg or %", default='n/a')
    battery_capacity: Optional[int] = Field(description='Battery capacity in mAh', default=None)
    coil_type: str = Field(description="Type of coil", default='n/a')

# Create the parser
parser = PydanticOutputParser(pydantic_object=VapeProducts)

prompt = PromptTemplate(
    template="""Extract the following fields from the vape product description:
- brand
- model/type
- flavor
- puff_count
- nicotine_strength
- battery_capacity
- coil_type

If a value is not present, respond with "n/a".

Respond ONLY in this JSON format:
{format_instructions}

Product Description:
 {description}\n""",
    input_variables=["description"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

# Chain combining : promopt , llm model and the pydantic output parser
chain = prompt | llm | parser

df_vaperanger= pd.read_csv('vaperanger.csv')
df_vapewholesaleusa = pd.read_csv("vapewholesaleusa.csv")

# Ensure both have 'inner_feature_description' by filling missing column with empty string
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

# Combine both dataframes
combined_df = pd.concat([df_vaperanger, df_vapewholesaleusa], ignore_index=True)

output_file = "structured_output.json"

# Load existing results if available
if os.path.exists(output_file):
    with open(output_file, "r") as f:
        results = json.load(f)
    start_index = len(results)
    print(f"The starting index {start_index}")
else:
    results = []
    start_index = 0


# Process only remaining rows
for i, row in tqdm(list(combined_df.iterrows())[start_index:], total=len(combined_df)-start_index, desc="Extracting structured data"):
    desc = row["full_description"] 
    link = row.get("product_link", "n/a")
    try:
        output = chain.invoke({"description": desc})
        structured_data = output.dict()
    except Exception as e:
        print(f"Due to this except the fields extracted are empty: {e}")
        structured_data = {
            "brand": "n/a",
            "model_type": "n/a",
            "flavor": None,
            "puff_count": None,
            "nicotine_strength": "n/a",
            "battery_capacity": None,
            "coil_type": "n/a"
        }

    structured_data["product_link"] = link
    results.append(structured_data)

    # storing results to file after each round
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)