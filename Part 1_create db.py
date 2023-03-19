import os
import pandas as pd
import sqlite3

# Set the directory path to search for Excel files
root_dir = r"D:\Excel Code"

# Create a connection to the SQLite database
conn = sqlite3.connect('excel collated.db')

# Create a function to export a dataframe to a SQLite table
def export_to_sqlite(dataframe, table_name, conn):
    # Drop rows with all empty cells
    dataframe.dropna(how='all', inplace=True)
    # Drop columns with all empty cells
    dataframe.dropna(axis=1, how='all', inplace=True)
    try:
        # Export the dataframe to the SQLite table
        dataframe.to_sql(table_name, conn, if_exists='replace', index=False)
    except sqlite3.OperationalError:
        print(f"Database locked: Table {table_name} could not be written to.")
        conn.rollback()

# Loop through all files and directories within the root directory
for root, dirs, files in os.walk(root_dir):
    for file in files:
        # Check if the file is an Excel file
        if file.endswith(".xlsx") or file.endswith(".xls"):
            # If it is an Excel file, read all sheets in the file
            file_path = os.path.join(root, file)
            try:
                excel_data = pd.read_excel(file_path, sheet_name=None)
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
                continue
            # Loop through all the sheet names and export the dataframes to SQLite tables
            for sheet_name, sheet_data in excel_data.items():
                # Check if sheet_data contains any data
                if not sheet_data.empty:
                    # Add day, month, and year columns for date columns
                    for col in sheet_data.columns:
                        if sheet_data[col].dtype == "datetime64[ns]":
                            sheet_data[col] = pd.to_datetime(sheet_data[col], errors="coerce")
                            sheet_data[col + "_day"] = sheet_data[col].dt.day
                            sheet_data[col + "_month"] = sheet_data[col].dt.month
                            sheet_data[col + "_year"] = sheet_data[col].dt.year
                    # Create a table name using the file name and sheet name
                    table_name = f"{file[:-5]}_{sheet_name}"
                    # Export the dataframe to the SQLite table
                    export_to_sqlite(sheet_data, table_name, conn)

# Close the database connection
conn.close()

print("All files completed.")
