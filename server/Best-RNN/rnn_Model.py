import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
import pickle

# Load the dataset
df = pd.read_csv('Final Data.csv')

# Handle missing values (if any)
df = df.dropna()

# Ensure consistent units for wind speed (convert miles/h to m/s if needed)
if 'Wind Speed (miles/h)' in df.columns:
    df['Wind Speed (m/s)'] = df['Wind Speed (miles/h)'] * 0.44704

# Use the correct wind speed column
wind_speed_col = 'Wind Speed (m/s)' if 'Wind Speed (m/s)' in df.columns else 'Wind Speed (miles/h)'

# Define input (X) and output (y) variables
X = df[[wind_speed_col, 'Temperature', 'Humidity', 'Pressure']].values
y = df['LV ActivePower (kW)'].values

# Normalize the data for better performance
scaler_X = MinMaxScaler(feature_range=(0, 1))
scaler_y = MinMaxScaler(feature_range=(0, 1))
X_scaled = scaler_X.fit_transform(X)
y_scaled = scaler_y.fit_transform(y.reshape(-1, 1))

# Reshape input data into 3D format [samples, timesteps, features] for LSTM
timesteps = 10
X_lstm, y_lstm = [], []

for i in range(timesteps, len(X_scaled)):
    X_lstm.append(X_scaled[i - timesteps:i])
    y_lstm.append(y_scaled[i])

X_lstm, y_lstm = np.array(X_lstm), np.array(y_lstm)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_lstm, y_lstm, test_size=0.2, random_state=100)

# Define the RNN model using LSTM layers
model = Sequential([
    LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])),
    Dropout(0.2),
    LSTM(50, return_sequences=False),
    Dropout(0.2),
    Dense(25),
    Dense(1)
])

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error')

# Train the model
early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test), callbacks=[early_stop], verbose=1)

# Evaluate the model
loss = model.evaluate(X_test, y_test, verbose=0)
print(f"\nModel Loss: {loss:.4f}")

# Make predictions
y_pred_scaled = model.predict(X_test)
y_pred = scaler_y.inverse_transform(y_pred_scaled)

# Inverse transform the y_test to get the original scale
y_test_original = scaler_y.inverse_transform(y_test)

# Evaluate the model
rmse = np.sqrt(mean_squared_error(y_test_original, y_pred))
mae = mean_absolute_error(y_test_original, y_pred)
r2 = r2_score(y_test_original, y_pred)

print(f"\nModel Evaluation:")
print(f"Root Mean Squared Error (RMSE): {rmse:.2f}")
print(f"Mean Absolute Error (MAE): {mae:.2f}")
print(f"R² Score: {r2:.2f}")

# Visualize the predictions
plt.figure(figsize=(10, 6))
plt.plot(y_test_original, label='True Values', color='blue')
plt.plot(y_pred, label='Predictions', color='red')
plt.title('True vs Predicted Values')
plt.xlabel('Samples')
plt.ylabel('LV ActivePower (kW)')
plt.legend()
plt.show()

# Save the trained model and scalers
model.save("rnn_model.h5")
pickle.dump(scaler_X, open("scaler_X.pkl", "wb"))
pickle.dump(scaler_y, open("scaler_y.pkl", "wb"))

print("\nModel and scalers saved successfully!")
