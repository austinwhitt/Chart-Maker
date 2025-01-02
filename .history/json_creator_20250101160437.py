import os
import pandas as pd
import json

class MarketMetricsGenerator:
    def __init__(self):
        self.data_path = './Data'
        self.metrics = [
            'inventory',
            'median',
            'months_supply',
            'new_listings',
            'price_per_foot',
            'showings'
        ]
        self.output_path = './Data/json/2024/December'  # Adjust based on current month

    def preprocess_data(self, data):
        # Remove dollar signs, commas, and convert to numeric values
        clean_data = data.copy()
        clean_data.iloc[:, 1:] = clean_data.iloc[:, 1:].replace(
            '[\$,]', '', regex=True).replace('', None).astype(float)
        return clean_data

    def calculate_changes(data, recent_month, previous_month, last_year_month):
    changes = pd.DataFrame()
    changes['Location'] = data.iloc[:, 0]
    changes['Recent'] = data[recent_month]
    
    # MoM Change calculation with safety checks
    mom_change = (data[recent_month] - data[previous_month]) / data[previous_month] * 100
    changes['MoM Change (%)'] = mom_change.replace([np.inf, -np.inf], 0)  # Replace infinity with 0
    
    # YoY Change calculation with safety checks
    yoy_change = (data[recent_month] - data[last_year_month]) / data[last_year_month] * 100
    changes['YoY Change (%)'] = yoy_change.replace([np.inf, -np.inf], 0)  # Replace infinity with 0
    
    return changes

    def generate_json_for_metric(self, metric):
        try:
            # Load city and county data
            city_path = os.path.join(self.data_path, metric, 'city.csv')
            county_path = os.path.join(self.data_path, metric, 'county.csv')
            
            city_data = pd.read_csv(city_path)
            county_data = pd.read_csv(county_path)
            
            # Clean the data
            city_data_clean = self.preprocess_data(city_data)
            county_data_clean = self.preprocess_data(county_data)
            
            # Get the most recent months (assuming same columns in both files)
            columns = [col for col in city_data_clean.columns if ' - ' in col]
            recent_month = columns[-1]  # Most recent month
            previous_month = columns[-2]  # Previous month
            last_year_month = columns[-13]  # Same month last year
            
            # Calculate changes
            city_changes = self.calculate_changes(
                city_data_clean, recent_month, previous_month, last_year_month)
            county_changes = self.calculate_changes(
                county_data_clean, recent_month, previous_month, last_year_month)
            
            # Combine and prepare for JSON
            combined_changes = pd.concat([city_changes, county_changes], ignore_index=True)
            combined_changes.dropna(inplace=True)
            
            # Create JSON structure
            scatter_data = [
                {
                    "x": row['MoM Change (%)'],
                    "y": row['YoY Change (%)'],
                    "label": row['Location'],
                    "medianValue": row['Recent']
                }
                for _, row in combined_changes.iterrows()
            ]
            
            # Ensure output directory exists
            os.makedirs(self.output_path, exist_ok=True)
            
            # Save to JSON
            output_file = os.path.join(self.output_path, f'{metric}_scatter.json')
            with open(output_file, 'w') as json_file:
                json.dump(scatter_data, json_file, indent=4)
                
            print(f"Successfully generated {metric} JSON")
            
        except Exception as e:
            print(f"Error processing {metric}: {e}")

    def update_all_metrics(self):
        print("Starting to generate JSONs for all metrics...")
        for metric in self.metrics:
            print(f"Processing {metric}...")
            self.generate_json_for_metric(metric)
        print("Finished generating all JSONs!")

if __name__ == "__main__":
    generator = MarketMetricsGenerator()
    generator.update_all_metrics()