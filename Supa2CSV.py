import pandas as pd
import dotenv
import os
from supabase import create_client, Client
dotenv.load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Pull Data from the 'price_facts' table and putting it into a pandas dataframe

data = supabase.table("price_facts").select("*").execute()
df = pd.DataFrame(data.data)
df.to_csv("commodity_prices.csv", index=False)
print("Data exported to commodity_prices.csv")