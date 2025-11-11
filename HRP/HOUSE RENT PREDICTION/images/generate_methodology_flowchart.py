import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle
import numpy as np

# Create figure and axis
fig, ax = plt.subplots(1, 1, figsize=(14, 10))
ax.set_xlim(0, 10)
ax.set_ylim(0, 12)
ax.axis('off')

# Define colors
colors = {
    'start_end': '#2E8B57',  # Sea Green
    'process': '#4682B4',    # Steel Blue
    'decision': '#FF6347',  # Tomato
    'data': '#DAA520'       # Goldenrod
}

# Function to create rounded rectangle
def create_rounded_rect(ax, xy, width, height, color, text, text_color='white'):
    box = FancyBboxPatch(xy, width, height,
                        boxstyle="round,pad=0.1",
                        facecolor=color, edgecolor='black', linewidth=2)
    ax.add_patch(box)
    ax.text(xy[0] + width/2, xy[1] + height/2, text,
            ha='center', va='center', fontsize=10, fontweight='bold',
            color=text_color, wrap=True)
    return box

# Function to create diamond shape for decisions
def create_diamond(ax, xy, width, height, color, text):
    # Create diamond using polygon
    center_x, center_y = xy[0] + width/2, xy[1] + height/2
    points = np.array([
        [center_x, center_y + height/2],  # Top
        [center_x + width/2, center_y],    # Right
        [center_x, center_y - height/2], # Bottom
        [center_x - width/2, center_y]   # Left
    ])
    diamond = plt.Polygon(points, closed=True, facecolor=color,
                         edgecolor='black', linewidth=2)
    ax.add_patch(diamond)
    ax.text(center_x, center_y, text, ha='center', va='center',
            fontsize=10, fontweight='bold', color='white', wrap=True)
    return diamond

# Function to create circle
def create_circle(ax, xy, radius, color, text):
    circle = Circle(xy, radius, facecolor=color, edgecolor='black', linewidth=2)
    ax.add_patch(circle)
    ax.text(xy[0], xy[1], text, ha='center', va='center',
            fontsize=10, fontweight='bold', color='white')
    return circle

# Function to draw arrow
def draw_arrow(ax, start, end, color='black'):
    ax.annotate('', xy=end, xytext=start,
                arrowprops=dict(arrowstyle='->', color=color, lw=2))

# Start
start = create_circle(ax, (5, 11), 0.5, colors['start_end'], 'START')

# Step 1: Data Collection
step1 = create_rounded_rect(ax, (3.5, 9.5), 3, 1, colors['process'], 'Data Collection\n(Gather rental data from\nvarious sources)')
draw_arrow(ax, (5, 10.5), (5, 10))

# Step 2: Data Preprocessing
step2 = create_rounded_rect(ax, (3.5, 8), 3, 1, colors['process'], 'Data Preprocessing\n(Clean, normalize,\nand transform data)')
draw_arrow(ax, (5, 9.5), (5, 9))

# Step 3: Feature Engineering
step3 = create_rounded_rect(ax, (3.5, 6.5), 3, 1, colors['process'], 'Feature Engineering\n(Select and create\nrelevant features)')
draw_arrow(ax, (5, 8), (5, 7.5))

# Decision: Sufficient Features?
decision1 = create_diamond(ax, (3.5, 5), 3, 1, colors['decision'], 'Sufficient\nFeatures?')
draw_arrow(ax, (5, 6.5), (5, 6))

# No - Go back to feature engineering
ax.text(2, 5.5, 'No', fontsize=10, fontweight='bold', color='red')
draw_arrow(ax, (3.5, 5.5), (2.5, 5.5))
draw_arrow(ax, (2.5, 5.5), (2.5, 8.5))
draw_arrow(ax, (2.5, 8.5), (3.5, 8.5))

# Yes - Proceed to model selection
ax.text(6.5, 5.5, 'Yes', fontsize=10, fontweight='bold', color='green')
draw_arrow(ax, (6.5, 5.5), (7, 5.5))

# Step 4: Model Selection
step4 = create_rounded_rect(ax, (5.5, 4), 3, 1, colors['process'], 'Model Selection\n(Choose appropriate\nML algorithms)')
draw_arrow(ax, (7, 4.5), (6.5, 4.5))

# Step 5: Model Training
step5 = create_rounded_rect(ax, (5.5, 2.5), 3, 1, colors['process'], 'Model Training\n(Train models with\ntraining data)')
draw_arrow(ax, (6.5, 4), (6.5, 3.5))

# Step 6: Model Evaluation
step6 = create_rounded_rect(ax, (5.5, 1), 3, 1, colors['process'], 'Model Evaluation\n(Test and validate\nmodel performance)')
draw_arrow(ax, (6.5, 2.5), (6.5, 2))

# Decision: Acceptable Performance?
decision2 = create_diamond(ax, (3.5, -0.5), 3, 1, colors['decision'], 'Acceptable\nPerformance?')
draw_arrow(ax, (6.5, 1), (6.5, 0))

# No - Go back to model selection
ax.text(5, -0.5, 'No', fontsize=10, fontweight='bold', color='red')
draw_arrow(ax, (5, -0.5), (4, -0.5))
draw_arrow(ax, (4, -0.5), (4, 4.5))
draw_arrow(ax, (4, 4.5), (5.5, 4.5))

# Yes - Deploy model
ax.text(7.5, -0.5, 'Yes', fontsize=10, fontweight='bold', color='green')
draw_arrow(ax, (7.5, -0.5), (8, -0.5))

# Step 7: Model Deployment
step7 = create_rounded_rect(ax, (7, -2), 3, 1, colors['data'], 'Model Deployment\n(Deploy trained model\nto production)')
draw_arrow(ax, (8, -0.5), (8.5, -1))

# End
end = create_circle(ax, (8.5, -3.5), 0.5, colors['start_end'], 'END')
draw_arrow(ax, (8.5, -2), (8.5, -3))

# Add title
plt.title('House Rent Prediction - Methodology Flowchart', fontsize=16, fontweight='bold', pad=20)

# Add legend
legend_elements = [
    mpatches.Patch(color=colors['start_end'], label='Start/End'),
    mpatches.Patch(color=colors['process'], label='Process'),
    mpatches.Patch(color=colors['decision'], label='Decision'),
    mpatches.Patch(color=colors['data'], label='Data/Output')
]
ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.02, 0.98))

plt.tight_layout()
plt.savefig('methodology_flowchart.png', dpi=300, bbox_inches='tight')
plt.show()

print("Methodology flowchart saved as 'methodology_flowchart.png'")