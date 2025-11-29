import os
import pandas as pd
import matplotlib.pyplot as plt
import dataframe_image as dfi
import csv
import io

# Manually clean the CSV data using the csv module
output = io.StringIO()
writer = csv.writer(output)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, 'House_Rent_10k_major_cities.csv')
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dataset_summary.png')

with open(DATASET_PATH, 'r', newline='', encoding='utf-8') as f:
    # Use a custom dialect to handle the formatting
    reader = csv.reader(f, delimiter=',', quotechar='"', skipinitialspace=True)
    for row in reader:
        writer.writerow(row)

# Get the cleaned CSV data as a string
cleaned_csv_data = output.getvalue()

# Use io.StringIO to treat the string as a file
csv_file = io.StringIO(cleaned_csv_data)

# Load the dataset from the cleaned CSV data
df = pd.read_csv(csv_file)

# Generate the summary
summary = df.describe()

# Save the summary to an image within the images folder
dfi.export(summary, OUTPUT_PATH)