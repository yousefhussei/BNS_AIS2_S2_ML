from preprocessing import (
    read_data,
    drop_unnecessary_features,
    check_data_type
)

from config.config import DATA_PATH, COLS_TO_DROP


def main():
    # Read the dataset
    df = read_data(DATA_PATH)

    # Stop if the dataset could not be loaded
    if df is None:
        print("Pipeline stopped.")
        return

    # Check data types and unique values
    print("===== DATA QUALITY REPORT =====")
    report = check_data_type(df)
    print(report)

    # Remove unnecessary features
    df = drop_unnecessary_features(df, COLS_TO_DROP)

    # Display the final data
    print("\n===== DATA AFTER PREPROCESSING =====")
    print(df.head())

    print("\nRemaining columns:")
    print(df.columns.tolist())


if __name__ == "__main__":
    main()