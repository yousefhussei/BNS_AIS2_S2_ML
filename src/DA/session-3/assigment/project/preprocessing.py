import pandas as pd


def read_data(file_path):
    try:
        df = pd.read_csv(file_path)
        return df

    except FileNotFoundError:
        print(f"Error: File not found -> {file_path}")
        return None

    except PermissionError:
        print(f"Error: Permission denied -> {file_path}")
        return None

    except pd.errors.EmptyDataError:
        print(f"Error: File is empty -> {file_path}")
        return None

    except pd.errors.ParserError:
        print(f"Error: Cannot read the CSV file -> {file_path}")
        return None

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def drop_unnecessary_features(df, cols_to_drop):
    return df.drop(columns=cols_to_drop, errors="ignore")


def check_data_type(df):
    report = pd.DataFrame({
        "Column Name": df.columns,
        "Data Type": df.dtypes.astype(str).values,
        "Unique Values": df.nunique().values
    })

    return report.T