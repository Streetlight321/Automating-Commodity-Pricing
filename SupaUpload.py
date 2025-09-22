def supa_upload(date, low, high, last, table_name):
    import supabase as sb
    import pandas as pd
    import dotenv
    import os
    from supabase import create_client, Client
    dotenv.load_dotenv()
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
    data = {
        'date' : date,
        'low' : low,
        'high' : high,
        'last' : last
    }
    response = supabase.table(table_name).insert(data).execute()
    print(f"Uploaded! response: {response}")
