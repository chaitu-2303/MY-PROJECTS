import pandas as pd
import matplotlib.pyplot as plt
import csv
import io

# Manually clean the CSV data using the csv module
output = io.StringIO()
writer = csv.writer(output)

with open('../House_Rent_Dataset.csv', 'r', newline='', encoding='utf-8') as f:
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

# Select numerical columns for distribution plots
numerical_features = df.select_dtypes(include=['int64', 'float64']).columns

# Create histograms for each numerical feature
for feature in numerical_features:
    plt.figure(figsize=(10, 6))
    df[feature].hist(bins=30)
    plt.title(f'Distribution of {feature}')
    plt.xlabel(feature)
    plt.ylabel('Frequency')
    plt.grid(False)
    plt.savefig(f'{feature}_distribution.png')
    plt.close()

print("Feature distribution graphs saved.")