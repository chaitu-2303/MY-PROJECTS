# House Rent Prediction

![House Rent Prediction Logo](https://github.com/chaitu-2303/House-Rent-Prediction/blob/master/IMAGES/LOGO.png?raw=true)

This project focuses on building a machine learning model to predict house rental prices based on various features of a property. The goal is to provide an accurate estimate of a house's rent, which can be useful for both landlords and tenants.

Machine learning for house rental descriptions is a tool that either predicts a fair price for a property or automatically generates compelling descriptions for listings. It analyzes a property's features (size, location, amenities, etc.) to either:

* **Predict Rent:** Use a regression model to estimate a competitive and accurate rental price.
* **Generate Descriptions:** Use natural language processing (NLP) to create clear, attractive summaries of a property from a list of its features.

The goal is to save time, increase accuracy, and help both landlords and tenants make more informed decisions.

---

## 🚀 Features

* **Data Preprocessing:** Scripts to clean and prepare raw data for model training. This includes handling missing values, encoding categorical features, and scaling numerical data.
* **Exploratory Data Analysis (EDA):** Notebooks or scripts to visualize and understand the relationships between different features and the target variable (rent).
* **Model Training:** Training a regression model (e.g., Linear Regression, Decision Tree, Random Forest) to predict rental prices.
* **Model Evaluation:** Metrics to assess the performance of the trained model, such as Mean Absolute Error (MAE), Mean Squared Error (MSE), and R2 score.
* **Prediction Interface:** A simple script or API endpoint to make predictions on new, unseen data.

---

## 🛠️ Technologies Used

The project is built primarily using Python and relies on a common data science stack.

* **Language:** Python
* **Data Manipulation:** Pandas, NumPy
* **Machine Learning:** Scikit-learn
* **Data Visualization (Optional):** Matplotlib, Seaborn
* **Web Framework (for API):** Flask (if an API endpoint is included)

---

## 📋 Installation

To get started with this project, follow these steps.

1.  Clone the repository:

    ```bash
   git clone [https://github.com/chaitu-2303/My-projects/tree/master/House%20Rent%20Prediction/house_rental](https://github.com/chaitu-2303/My-projects/tree/master/House%20Rent%20Prediction/house_rental)
   cd house_rental
   ```

2.  Set up a virtual environment:

    ```bash
   # Create a virtual environment
   python -m venv venv

    # Activate the virtual environment
   On Windows:
   venv\Scripts\activate
   On macOS/Linux:
   source venv/bin/activate
   ```

3.  Install dependencies:

    ```bash
   pip install -r requirements.txt
   ```

    If you don't have a `requirements.txt` file, you can install the main libraries manually:

    ```bash
   pip install pandas numpy scikit-learn
   ```

---

## 🚀 Usage

After installation, you can train the model and make predictions from your local machine.

### Training the Model

1.  Ensure your dataset `(house_data.csv)` is placed in the `data/` directory.

2.  Run the training script:

    ```bash
   python src/train_model.py
   ```

---

### Making a Prediction

Use the prediction script to get a rent estimate for a new property.

```bash
python src/predict.py --bedrooms 3 --bathrooms 2 --sqft 1500 --location "City Center"

________________


📁 File Structure


The project has the following suggested file structure:






house_rental/
├── data/
│   └── house_data.csv        # Raw dataset for training
├── models/
│   └── house_rent_model.pkl  # Trained machine learning model
├── notebooks/
│   └── eda.ipynb             # Jupyter Notebook for exploratory data analysis
├── src/
│   ├── preprocess.py         # Script for data cleaning and preprocessing
│   ├── train_model.py        # Script to train and evaluate the model
│   └── predict.py            # Script for making predictions
├── README.md                 # This file
├── requirements.txt          # Project dependencies
└── .gitignore                # Git ignore file

________________


Demo


Insert gif or link to demo
________________


Screenshots


________________


🧪 Running Tests




1. Unit Tests with unittest


If you’ve written Python test cases using the built-in unittest module, you can run them like this:


Bash




python -m unittest discover -s tests

* tests/ should be the directory containing your test files (e.g., test_model.py, test_preprocessing.py).
* Each test file should follow the naming convention test_*.py.


2. Using pytest


If you prefer pytest (more readable and powerful), install it first:


Bash




pip install pytest

Then run all tests:


Bash




pytest

You can also run a specific test file:


Bash




pytest tests/test_model.py



3. Example Test Case


Here’s a simple test for a rent prediction function:


Python




# tests/test_prediction.py
import unittest
from model import predict_rent  # hypothetical function

class TestRentPrediction(unittest.TestCase):
   def test_basic_prediction(self):
       features = {'bhk': 2, 'size': 1000, 'city': 'Mumbai', 'furnishing': 'Semi-Furnished'}
       rent = predict_rent(features)
       self.assertTrue(rent > 5000)

if __name__ == '__main__':
   unittest.main()

________________


📋 Documentation


1. Documentation
2. House Rent Prediction Infographic
________________


📜 License


MIT License
This project is licensed under the MIT License.
* Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
1. The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
2. The Software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement.
3. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the Software or the use or other dealings in the Software.
4. Any modifications or derivative works must include a clear attribution to the original authors and a description of the changes made.
5. Redistribution of the Software must retain this license and all associated disclaimers.
The Software may not be used for any unlawful or unethical purposes.
________________


👥 Users


* Tenants: Individuals looking for affordable housing options based on location, size, and amenities.
* Landlords & Property Owners: To set competitive rental prices that attract tenants while maximizing returns.
* Real Estate Platforms: Websites like MagicBricks or 99acres use predictive models to recommend listings and estimate fair rental values.
* Urban Planners & Researchers: To analyze rental trends and housing affordability across regions.
* Investors: To assess rental yield and make informed decisions about property purchases.
________________


🔑 Environment Variables


To run this project, you may need to add the following environment variables to a .env file:


Code snippet




API_KEY=[YOUR_API_KEY]
DATA_PATH=[PATH_TO_YOUR_DATA]

________________


⚙️ API Reference


Your Flask-based API likely exposes endpoints for rent prediction. Here's a suggested reference structure based on typical usage:


Base URL




HTTP




http://<your-domain-or-localhost>/api



Endpoints


Method
	Endpoint
	Description
	Payload Format
	POST
	/predict
	Returns predicted rent based on input
	JSON
	

Sample Request




HTTP




POST /predict
Content-Type: application/json

{
 "BHK": 2,
 "Size": 1200,
 "City": "Mumbai",
 "Furnishing Status": "Furnished",
 "Tenant Preferred": "Family",
 "Bathroom": 2
}



Sample Response




HTTP




{
 "predicted_rent": 32000
}

Let me know if you want Swagger or Postman documentation for this.
________________


🚀 Deployment


To deploy this Flask app, here are a few streamlined options.
1. Local Deployment
Bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py

2. Heroku Deployment
   * Add a Procfile:
web: gunicorn app:app

   * Ensure requirements.txt and runtime.txt are present.
   * Use Git to push to Heroku.
      3. Docker Deployment
      * Add a Dockerfile:
Dockerfile
FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]

      * Then build and run:
Bash
docker build -t house-rent .
docker run -p 5000:5000 house-rent

________________


⚡ Optimizations


Here are some ideas to improve performance and maintainability:


Model Optimization


         * Use GridSearchCV or RandomizedSearchCV for hyperparameter tuning.
         * Consider using XGBoost or LightGBM for better accuracy and speed.


Data Pipeline


         * Cache preprocessed data to avoid redundant transformations.
         * Use joblib for faster model serialization/deserialization.


API Efficiency


         * Add input validation using pydantic or marshmallow.
         * Enable CORS only for trusted domains.


Logging & Monitoring


         * Integrate logging module for better debugging.
         * Add a basic health check endpoint (/health) for uptime monitoring.
________________


👥 Authors


         * PAMARTHI CHAITANYA (2203031240984)
         * GOLLA GOKUL SAI RAM (2203031240421)
         * DUGGIRALA KRISHNA CHOWDARY (2203031240358)
         * REDDY HARSHA SAI VENKATA PRUDHVI (2203031241123)
________________


🙏 Acknowledgements


I’d like to express my gratitude to the following resources and individuals who supported and inspired this project:
         * Kaggle – For providing the House Rent Dataset used to train and evaluate the model.
         * Scikit-learn & Pandas – For their powerful and flexible tools that made data preprocessing and model building seamless.
         * Flask – For enabling a lightweight and efficient API framework to deploy the model.
         * Matplotlib & Seaborn – For helping visualize data insights and trends.
         * GitHub Community – For continuous inspiration and open-source collaboration.
         * My mentors, peers, and fellow developers – For their valuable feedback and encouragement throughout the development process.
Special thanks to everyone who believes in the power of data-driven decision-making and supports open learning.
________________


🤝 Contributing


Contributions are what make the open-source community an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.
         1. Fork the Project.
         2. Create your Feature Branch (git checkout -b feature/AmazingFeature).
         3. Commit your Changes (git commit -m 'Add some AmazingFeature').
         4. Push to the Branch (git push origin feature/AmazingFeature).
         5. Open a Pull Request.
________________


🎨 Color Reference


If you're planning to enhance the UI or dashboard, here’s a clean palette suggestion:
Element
	Color Name
	Color Code
	Usage
	Primary Accent
	Havelock Blue
	🟦#4A90E2
	Buttons, highlights
	Secondary
	Turquoise
	🟩#50E3C2
	Hover states, secondary info
	Background
	Cultured (Light)
	⚪#F5F7FA
	Page background
	Text (Dark)
	Jet (Dark Gray)
	⬛#333333
	Main text
	Text (Light)
	Gray
	⚫#888888
	Subtext, labels
	Error/Alert
	Crimson Red
	🟥#D0021B
	Validation messages