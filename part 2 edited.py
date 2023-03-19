import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import itertools
from fuzzywuzzy import fuzz

# Ask the user for variables to search for
search_vars = []
while True:
    var = input("Enter a variable to search for (or type 'done' when finished): ").lower() # convert input to lowercase
    if var == 'done':
        break
    search_vars.append(var)

# Connect to the SQLite database
conn = sqlite3.connect('excel collated.db')

# Search for tables that contain the variables
tables_with_vars = []
cursor = conn.cursor()
for table_name in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
    table_name = table_name[0]
    table = pd.read_sql_query(f"SELECT * FROM [{table_name}]", conn)
    cols = table.columns
    cols_with_var = [col for col in cols if any(fuzz.partial_ratio(search_var.lower(), col.lower()) >= 75 for search_var in search_vars)]
    if len(cols_with_var) > 0:
        print(f"\nTable name: {table_name}")
        print(f"Columns available: {', '.join(cols_with_var)}")
        tables_with_vars.append((table_name, cols_with_var))

# Ask the user to select a table and variable
if len(tables_with_vars) == 0:
    print("No tables found that contain the specified variables.")
else:
    selected_table_name, selected_var = None, None
    while not selected_table_name or not selected_var:
        selected_table_index = input("Enter the number of the table you want to use: ")
        if selected_table_index.isnumeric() and 0 <= int(selected_table_index) - 1 < len(tables_with_vars):
            selected_table_index = int(selected_table_index) - 1
            selected_table_name, available_cols = tables_with_vars[selected_table_index]
            selected_var = input(f"Enter a variable from {', '.join(available_cols)}: ").lower().strip()
            if selected_var not in available_cols:
                selected_table_name, selected_var = None, None
                print(f"{selected_var} not found in the selected table. Please try again.")
        else:
            print(f"Invalid table number. Please try again.")

    # Get the selected table and variables
    selected_table = pd.read_sql_query(f"SELECT * FROM [{selected_table_name}]", conn)
    selected_vars = [var for var in search_vars if var.lower() in [col.lower() for col in selected_table.columns]]

    # Perform the cross-tabulation and plot the results
    if len(selected_vars) == 0:
        print("None of the specified variables were found in the selected table.")
    else:
        if any(selected_table[var].dtype == 'datetime64[ns]' for var in selected_vars):
            date_var = [var for var in selected_vars if selected_table[var].dtype == 'datetime64[ns]']
            if len(date_var) == 1:
                date_var = date_var[0].lower() # convert to lowercase
                pivot_table = pd.pivot_table(selected_table, values=selected_vars, index=date_var, aggfunc=np.sum)
                pivot_table.plot(kind='bar')
                plt.show()
                print(pivot_table)
            else:
                print("More than one date variable found. Please select one date variable to plot the results.")
        else:
            print("One of the selected variables must be a date variable to plot the results.")
