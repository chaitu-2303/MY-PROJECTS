import pandas as pd
import matplotlib.pyplot as plt
import csv
import io
import math

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

# Create a figure with subplots for each numerical feature
num_features = len(numerical_features)
cols = 2
rows = math.ceil(num_features / cols)

fig, axes = plt.subplots(nrows=rows, ncols=cols, figsize=(15, 5 * rows))
axes = axes.flatten() # Flatten the 2D array of axes to easily iterate

for i, feature in enumerate(numerical_features):
    df[feature].hist(bins=30, ax=axes[i])
    axes[i].set_title(f'Distribution of {feature}')
    axes[i].set_xlabel(feature)
    axes[i].set_ylabel('Frequency')
    axes[i].grid(False)

# Hide any unused subplots
for j in range(i + 1, len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout()
plt.savefig('combined_feature_distribution.png')
plt.close()

print("Combined feature distribution graph saved.")