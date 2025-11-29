import matplotlib.pyplot as plt
import numpy as np

# Data for the table
data = [
    ["XGBoost", "0.95", "0.05", "0.92"],
    ["Random Forest", "0.92", "0.08", "0.90"],
    ["Linear Regression", "0.85", "0.15", "0.82"]
]

columns = ("Model", "R-squared", "Mean Absolute Error", "Mean Squared Error")

# Create a figure and axis
fig, ax = plt.subplots(figsize=(10, 2))
ax.axis('tight')
ax.axis('off')

# Create the table
the_table = ax.table(cellText=data, colLabels=columns, loc='center', cellLoc='center')

# Style the table
the_table.auto_set_font_size(False)
the_table.set_fontsize(12)
the_table.scale(1.2, 1.2)

# Add a title
plt.title("Model Performance Metrics", fontsize=16)

# Save the figure
plt.savefig("model_performance_metrics.png", bbox_inches='tight', pad_inches=0.1)