import pandas as pd

# Read the Excel file
df = pd.read_excel('global_grant_calculator_en.xlsx')

# Display basic information about the dataframe
print(df.info())

# Display the first few rows of the dataframe
print(df.head())

# Display column names
print("\nColumn names:")
print(df.columns.tolist())

# Display unique values in each column (if applicable)
for column in df.columns:
    if df[column].dtype == 'object' or df[column].nunique() < 10:
        print(f"\nUnique values in {column}:")
        print(df[column].unique())