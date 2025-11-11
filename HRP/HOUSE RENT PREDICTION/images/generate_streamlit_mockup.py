import turtle

# Set up the screen
screen = turtle.Screen()
screen.setup(width=800, height=600)
screen.bgcolor("white")
screen.title("Streamlit UI Mockup")

# Create a turtle for drawing
pen = turtle.Turtle()
pen.speed(0)
pen.penup()

# Draw the header
pen.goto(-400, 250)
pen.pendown()
pen.color("black")
pen.begin_fill()
for _ in range(2):
    pen.forward(800)
    pen.right(90)
    pen.forward(50)
    pen.right(90)
pen.end_fill()
pen.penup()

# Write the header title
pen.goto(-380, 260)
pen.color("white")
pen.write("Streamlit House Rent Prediction", font=("Arial", 16, "bold"))

# Draw the sidebar
pen.goto(-400, 250)
pen.pendown()
pen.color("#f0f2f6")
pen.begin_fill()
for _ in range(2):
    pen.forward(200)
    pen.right(90)
    pen.forward(550)
    pen.right(90)
pen.end_fill()
pen.penup()

# Add sidebar widgets
pen.goto(-380, 200)
pen.color("black")
pen.write("Filters", font=("Arial", 14, "bold"))

pen.goto(-380, 150)
pen.write("Bedrooms:", font=("Arial", 12, "normal"))
pen.goto(-380, 120)
pen.pendown()
pen.forward(160)
pen.penup()

pen.goto(-380, 80)
pen.write("City:", font=("Arial", 12, "normal"))
pen.goto(-380, 50)
pen.pendown()
pen.forward(160)
pen.penup()

# Draw the main content area
pen.goto(-180, 200)
pen.color("black")
pen.write("Rent Prediction Output", font=("Arial", 14, "bold"))

# Draw a placeholder for a plot
pen.goto(-150, 150)
pen.pendown()
pen.color("gray")
for _ in range(2):
    pen.forward(300)
    pen.right(90)
    pen.forward(200)
    pen.right(90)
pen.penup()

pen.goto(-100, 50)
pen.write("Predicted Rent: $2,500", font=("Arial", 12, "normal"))

# Save the drawing as an image
pen.hideturtle()
screen.getcanvas().postscript(file="streamlit_mockup.eps")

# Close the turtle graphics window
turtle.done()