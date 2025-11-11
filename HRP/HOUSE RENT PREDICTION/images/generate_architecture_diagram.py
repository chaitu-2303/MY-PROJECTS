import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Create figure and axis
fig, ax = plt.subplots(figsize=(12, 8))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')

# Define colors
colors = {
    'client': '#FFDDC1',      # Light Peach
    'frontend': '#D4F1F4',    # Light Blue
    'backend': '#F3E5AB',     # Light Yellow
    'database': '#E2F0CB',     # Light Green
    'ml_model': '#FFD1DC'      # Light Pink
}

# Function to create a box
def create_box(ax, xy, width, height, color, text, text_color='black', fontsize=10):
    rect = mpatches.Rectangle(xy, width, height, facecolor=color, edgecolor='black', linewidth=1.5)
    ax.add_patch(rect)
    ax.text(xy[0] + width/2, xy[1] + height/2, text, ha='center', va='center', fontsize=fontsize, fontweight='bold', color=text_color, wrap=True)

# Function to draw an arrow
def draw_arrow(ax, start, end, text="", text_offset=(0, 0.2)):
    ax.annotate('', xy=end, xytext=start, arrowprops=dict(arrowstyle='->', color='black', lw=1.5, shrinkA=5, shrinkB=5))
    if text:
        mid_point = ((start[0] + end[0]) / 2 + text_offset[0], (start[1] + end[1]) / 2 + text_offset[1])
        ax.text(mid_point[0], mid_point[1], text, ha='center', va='center', fontsize=8, fontweight='bold', bbox=dict(facecolor='white', edgecolor='none', pad=0.2))

# --- Components of the Architecture ---

# 1. Client Tier
create_box(ax, (0.5, 4.5), 2, 1, colors['client'], 'User\n(Web Browser)')

# 2. Presentation Tier (Frontend)
create_box(ax, (3.5, 7), 3, 2, colors['frontend'], 'Presentation Tier (Frontend)\n\n- HTML / CSS\n- JavaScript')
create_box(ax, (3.5, 1), 3, 2, colors['frontend'], 'Owner/Admin\n(Web Browser)')

# 3. Application Tier (Backend)
create_box(ax, (6.5, 3.5), 3, 3, colors['backend'], 'Application Tier (Backend)\n\n- Flask Web Server\n- Business Logic\n- User Authentication\n- Property Management')

# 4. Data Tier (Database)
create_box(ax, (6.5, 0.5), 3, 1.5, colors['database'], 'Data Tier\n\n- SQLite Database')

# 5. Machine Learning Model
create_box(ax, (3.5, 4), 3, 1.5, colors['ml_model'], 'Machine Learning Model\n\n- Rent Prediction Engine')

# --- Arrows and Data Flow ---

# User to Frontend
draw_arrow(ax, (2.5, 5), (3.5, 8), "HTTP Requests")
draw_arrow(ax, (3.5, 7.5), (2.5, 5.5), "HTML/JS/CSS")

# Admin to Frontend
draw_arrow(ax, (2.5, 2), (3.5, 2), "Admin Actions")
draw_arrow(ax, (3.5, 1.5), (2.5, 2.5), "Admin UI")

# Frontend to Backend
draw_arrow(ax, (6.5, 8), (7.5, 6.5), "API Calls (Login, Search, etc.)", text_offset=(-1.5, 0.2))
draw_arrow(ax, (7.5, 6), (6.5, 7), "JSON Data / Renders", text_offset=(-1.5, -0.2))

# Backend to Database
draw_arrow(ax, (8, 3.5), (8, 2), "CRUD Operations\n(SQL Queries)")

# Backend to ML Model
draw_arrow(ax, (5, 3.5), (5, 5), "Prediction Request", text_offset=(-1, 0))
draw_arrow(ax, (5, 5.5), (5, 4.5), "Predicted Rent", text_offset=(-1, 0))

# Title
fig.suptitle('Proposed System Architecture', fontsize=16, fontweight='bold')

# Save the figure
plt.savefig('proposed_system_architecture.png', dpi=300, bbox_inches='tight')

print("Proposed system architecture diagram saved as 'proposed_system_architecture.png'")