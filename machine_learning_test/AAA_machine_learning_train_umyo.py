import numpy as np
import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error

def evaluate_model(y_true, y_pred):
    mse = mean_squared_error(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    
    print(f'Mean Squared Error: {mse}')
    print(f'Mean Absolute Error: {mae}')
    
datafile = 'september13-2023-Session-14A.csv'
data = pd.read_csv(f'Data-Captures/{datafile}')

print(f'Training Model from {datafile}')

input_features = ['u0_time','u0_qgs0','u0_qgs1','u0_qgs2','u0_qgs3','u0_x','u0_y','u0_z',
                 'u1_time','u1_qgs0','u1_qgs1','u1_qgs2','u1_qgs3','u1_x','u1_y','u1_z',
                 'u2_time','u2_qgs0','u2_qgs1','u2_qgs2','u2_qgs3','u2_x','u2_y','u2_z',
                 'u3_time','u3_qgs0','u3_qgs1','u3_qgs2','u3_qgs3','u3_x','u3_y','u3_z']
X = data[input_features]
input_labels = ['lask_time','LASK1','LASK2','LASK3','LASK4']
y = data[input_labels]

# Split the data into training and testing sets, and scale the input features
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler = StandardScaler()


base_model = RandomForestRegressor(n_estimators=100, random_state=42)

model = MultiOutputRegressor(base_model)

model.fit(X_train, y_train)

# Print the evaluation metric(s) to the screen
with open(f'{datafile.split(".")[0]}.pkl', 'wb') as f:
    pickle.dump(model, f)


# Predict on the test set
y_pred = model.predict(X_test)

# Evaluate the model
evaluate_model(y_test, y_pred)


# Create a new DataFrame with the actual and predicted labels
result_df = y_test.copy().reset_index(drop=True)
result_df.columns = ['LASK_time','Actual LASK1', 'Actual LASK2', 'Actual LASK3', 'Actual LASK4']
result_df['Predicted LASK TIme'] = y_pred[:, 0]
result_df['Predicted LASK1'] = y_pred[:, 1]
result_df['Predicted LASK2'] = y_pred[:, 2]
result_df['Predicted LASK3'] = y_pred[:, 3]
result_df['Predicted LASK4'] = y_pred[:, 4]

# Save the DataFrame as a CSV file

result_df.to_csv('predictions_vs_actuals 5.csv', index=False)

