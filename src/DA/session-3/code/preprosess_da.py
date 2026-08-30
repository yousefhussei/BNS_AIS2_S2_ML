import pandas as pd
def drpo_columns(df, columns):
    return df.drop(columns = columns)

def get_data_summary(df: pd.DataFrame)->pd.DataFrame:
    pd.DataFrame({"Dtype ": df.dtype, "n_unique" :df.n_unique}).T