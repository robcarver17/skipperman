import pandas as pd

def view_df_as_html(df: pd.DataFrame):
    ## Consider adding sort by buttons
    return df.to_html()