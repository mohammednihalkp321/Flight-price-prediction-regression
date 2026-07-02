# ✈️ Flight Price Prediction using Machine Learning

A Machine Learning regression project that predicts airline ticket prices based on flight details such as airline, travel class, journey duration, booking timing, flight distance, seat availability, and other flight-related features.

This project covers the complete Machine Learning workflow, including data cleaning, exploratory data analysis (EDA), feature engineering, preprocessing, model building, evaluation, and model comparison.

---

## 📌 Project Objective

The objective of this project is to build a regression model that can accurately predict flight ticket prices using historical flight booking data.

---

## 📂 Dataset Information

- **Dataset Size:** 300,453 records
- **Original Features:** 15
- **Target Variable:** `price`

### Numerical Features

- Duration
- Days Left
- Flight Distance
- Seat Availability
- Airline Rating
- Price

### Categorical Features

- Airline
- Source City
- Destination City
- Departure Time
- Arrival Time
- Number of Stops
- Travel Class
- Holiday Season

---

# 🛠 Project Workflow

## 1️⃣ Data Understanding

- Loaded the dataset
- Identified target variable
- Identified numerical and categorical features
- Checked dataset shape
- Examined data types
- Checked missing values
- Generated summary statistics

---

## 2️⃣ Exploratory Data Analysis (EDA)

Performed visual analysis using:

- Price Distribution
- Price Boxplot
- Duration vs Price
- Flight Distance vs Price
- Correlation Heatmap
- Price by Travel Class
- Distribution of Stops

### Key Findings

- Flight prices are positively skewed.
- Business-class tickets are much more expensive.
- Flight distance has a positive relationship with price.
- Longer journeys generally cost more.
- Seat availability has a strong negative correlation with price.
- One-stop flights are the most common.

---

## 3️⃣ Data Cleaning & Preprocessing

### Missing Value Handling

Filled missing values using:

- Median (Numerical columns)
- Mode (Categorical column)

### Duplicate Removal

- Removed duplicate records
- Reset index

### Inconsistent Value Correction

Standardized categorical values such as:

- Airline names
- Holiday season values

### Data Type Conversion

Converted required columns into appropriate data types.

### Outlier Detection

Detected outliers using the IQR (Interquartile Range) method.

### Feature Selection

Removed the `flight` column because it does not contribute to prediction.

---

## 4️⃣ Feature Engineering

Created new business-oriented features:

- Journey Type
- Demand Level
- Booking Category
- Premium Airline
- Flight Speed (km/h)

These engineered features help improve the model's understanding of pricing patterns.

---

## 5️⃣ Categorical Encoding

Applied:

- Label Encoding
- One-Hot Encoding

to convert categorical variables into numerical format.

---

## 6️⃣ Model Development

### Feature & Target Selection

- X → Input Features
- y → Price

### Train-Test Split

- Training Data → 80%
- Testing Data → 20%

### Feature Scaling

Applied **StandardScaler** to standardize numerical features.

---

# 🤖 Models Used

## 1. Linear Regression

A simple regression model that predicts ticket prices based on linear relationships between features and the target.

### Performance

| Metric | Value |
|---------|-------|
| MAE | **3707.72** |
| RMSE | **5685.17** |
| R² Score | **0.937** |

---

## 2. Polynomial Regression

Polynomial Regression (Degree = 2) was used to capture non-linear relationships between numerical features.

### Performance

| Metric | Value |
|---------|-------|
| MAE | **5168.68** |
| RMSE | **7706.79** |
| R² Score | **0.884** |

---

# 📊 Model Comparison

| Model | MAE | RMSE | R² Score |
|--------|------:|------:|------:|
| Linear Regression | **3707.72** | **5685.17** | **0.937** |
| Polynomial Regression | 5168.68 | 7706.79 | 0.884 |

### Final Model

✅ **Linear Regression**

Reason:

- Lowest MAE
- Lowest RMSE
- Highest R² Score
- Better overall prediction performance

---

# 📈 Results

The Linear Regression model achieved:

- **R² Score:** 93.7%
- Good prediction accuracy
- Low prediction error
- Better performance than Polynomial Regression

---

# 💡 Key Insights

- Flight distance positively influences ticket price.
- Longer journey duration generally increases ticket price.
- Business-class tickets are significantly more expensive.
- Lower seat availability leads to higher ticket prices.
- Last-minute bookings tend to cost more.
- Premium airlines generally charge higher prices.

---

# ⚠️ Limitations

- Dataset does not include weather information.
- Fuel prices are not considered.
- Airline competition is not included.
- Some premium-priced tickets have larger prediction errors.
- Performance depends on dataset quality.

---

# 🚀 Future Improvements

- Deploy using Streamlit.
- Collect real-time flight data.
- Try advanced models like:
  - Random Forest
  - XGBoost
  - Gradient Boosting
- Perform Hyperparameter Tuning.
- Include weather and fuel price information.

---

# 🧰 Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Scikit-learn
- Jupyter Notebook
- VS Code

---

## 📁 Project Structure

```text
Flight-price-prediction-regression/
│
├── data/
│   └── Flight_Price_Prediction.csv
│
├── models/
│   ├── linear_regression_model.pkl
│   ├── standard_scaler.pkl
│   ├── holiday_label_encoder.pkl
│   └── feature_columns.pkl
│
├── notebooks/
│   └── Flight_Price_Prediction.ipynb
│
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

# ▶️ How to Run

### Clone Repository

```bash
git clone https://github.com/mohammednihalkp321/Flight-price-prediction-regression
```

### Navigate

```bash
cd Flight-price-prediction-regression
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Notebook

Open:

```
notebooks/project_analysis.ipynb
```

Or run the Streamlit app (after completing it):

```bash
streamlit run streamlit.py
```

---

# 👨‍💻 Author

**Mohammed Nihal**

Data Analytics Intern

- Python
- SQL
- Power BI
- Machine Learning
- Data Analytics

---

