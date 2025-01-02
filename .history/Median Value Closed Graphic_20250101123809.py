import pandas as pd
import json

# Function to clean and preprocess the dataset
def preprocess_data(data):
    # Remove dollar signs, commas, and convert to numeric values
    clean_data = data.copy()
    clean_data.iloc[:, 1:] = clean_data.iloc[:, 1:].replace(
        '[\$,]', '', regex=True).replace('', None).astype(float)
    return clean_data

# Function to calculate MoM and YoY changes
def calculate_changes(data, recent_month, previous_month, last_year_month):
    changes = pd.DataFrame()
    changes['Location'] = data.iloc[:, 0]
    changes['Recent'] = data[recent_month]
    changes['MoM Change (%)'] = (
        (data[recent_month] - data[previous_month]) / data[previous_month]) * 100
    changes['YoY Change (%)'] = (
        (data[recent_month] - data[last_year_month]) / data[last_year_month]) * 100
    return changes

# Load the data
city_data_path = '/Users/austinwhitt/Desktop/Chart Maker/Data/3_year_city_median_closed.csv'
county_data_path = '/Users/austinwhitt/Desktop/Chart Maker/Data/3_year_county_median_closed.csv'


city_data = pd.read_csv(city_data_path)
county_data = pd.read_csv(county_data_path)

# Preprocess the datasets
city_data_clean = preprocess_data(city_data)
county_data_clean = preprocess_data(county_data)

# Define the relevant months
recent_month = "Dec - 2024"
previous_month = "Nov - 2024"
last_year_month = "Dec - 2023"

# Calculate changes for city and county data
city_changes = calculate_changes(city_data_clean, recent_month, previous_month, last_year_month)
county_changes = calculate_changes(county_data_clean, recent_month, previous_month, last_year_month)

# Combine city and county changes for visualization
combined_changes = pd.concat([city_changes, county_changes], ignore_index=True)

# Drop rows with NaN values (if any)
combined_changes.dropna(inplace=True)

# Prepare data for JSON output
scatter_data = [
    {
        "x": row['MoM Change (%)'],
        "y": row['YoY Change (%)'],
        "label": row['Location']
    }
    for _, row in combined_changes.iterrows()
]

# Save the data to a JSON file
output_path = 'scatter_data.json'
with open(output_path, 'w') as json_file:
    json.dump(scatter_data, json_file, indent=4)

print(f"Data successfully saved to {output_path}.")
