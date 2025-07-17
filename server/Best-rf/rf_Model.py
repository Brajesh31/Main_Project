import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
import pickle

# Load the dataset
df = pd.read_csv('Final Data.csv')

# Handle missing values (if any)
df = df.dropna()

# Ensure consistent units for wind speed (convert miles/h to m/s if needed)
if 'Wind Speed (miles/h)' in df.columns:
    df['Wind Speed (m/s)'] = df['Wind Speed (miles/h)'] * 0.44704

# Define input (X) and output (y) variables
X = df[['Wind Speed (m/s)', 'Temperature', 'Humidity', 'Pressure']]
y = df['LV ActivePower (kW)']

# Normalize or standardize features for better performance
scaler = StandardScaler()
X = scaler.fit_transform(X)

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=100)

# Initialize the Random Forest Regressor
rf = RandomForestRegressor(random_state=100)

# Define the hyperparameter grid
param_dist = {
    'n_estimators': [50, 100, 200],
    'max_depth': [10, 20, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

# Initialize RandomizedSearchCV
random_search = RandomizedSearchCV(
    estimator=rf,
    param_distributions=param_dist,
    n_iter=20,  # Number of parameter combinations to test
    cv=3,  # Cross-validation folds
    n_jobs=-1,  # Use all available processors
    scoring='neg_mean_squared_error',
    random_state=100,
    verbose=3  # Verbose output to monitor progress
)

# Fit the model
random_search.fit(X_train, y_train)

# Best model and parameters
best_rf = random_search.best_estimator_
print(f"Best Parameters: {random_search.best_params_}")

# Train the model with the best parameters
best_rf.fit(X_train, y_train)

# Predictions on the test set
y_pred = best_rf.predict(X_test)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"\nModel Evaluation:")
print(f"Root Mean Squared Error (RMSE): {rmse:.2f}")
print(f"Mean Absolute Error (MAE): {mae:.2f}")
print(f"R² Score: {r2:.2f}")

# Feature importance
feature_importance = pd.DataFrame({
    'Feature': ['Wind Speed (m/s)', 'Temperature', 'Humidity', 'Pressure'],
    'Importance': best_rf.feature_importances_
}).sort_values(by='Importance', ascending=False)
print("\nFeature Importance:")
print(feature_importance)

# Visualize feature importance
plt.figure(figsize=(8, 6))
plt.bar(feature_importance['Feature'], feature_importance['Importance'], color='skyblue')
plt.title('Feature Importance')
plt.xlabel('Features')
plt.ylabel('Importance')
plt.show()

# Save the trained model and scaler for later use
pickle.dump(best_rf, open("best_rf_model.pkl", "wb"))
pickle.dump(scaler, open("scaler.pkl", "wb"))

print("\nModel and scaler saved successfully!")
