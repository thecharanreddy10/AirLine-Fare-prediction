import os
import pandas as pd
import numpy as np
import pickle
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, r2_score

MODEL_FILE = 'media/new_rf_model.pkl'
PREPROCESSOR_FILE = 'media/preprocessor.pkl'
DATA_FILE = 'media/Indian_Airlines_cleaned_data.csv'

import glob

def load_data():
    # Load and concatenate all CSV datasets from media/ and dataset/ directories
    media_files = glob.glob('media/*.csv')
    dataset_files = glob.glob('dataset/*.csv')
    all_files = list(set(media_files + dataset_files))  # unique files

    dataframes = []
    for file in all_files:
        try:
            df = pd.read_csv(file)
            dataframes.append(df)
        except Exception as e:
            print(f"Error loading {file}: {e}")

    if not dataframes:
        raise ValueError("No datasets loaded. Please check dataset files.")

    # Concatenate all dataframes, aligning columns
    data = pd.concat(dataframes, ignore_index=True, sort=False)

    # Optional: drop duplicates if any
    data = data.drop_duplicates()

    return data

def preprocess_and_train():
    data = load_data()

    # Features and target
    features = ['airline', 'source_city', 'departure_time', 'stops', 'arrival_time', 'destination_city', 'class', 'duration', 'days_left']
    target = 'price'

    X = data[features]
    y = data[target]

    # Define categorical and numerical columns
    categorical_cols = ['airline', 'source_city', 'departure_time', 'arrival_time', 'destination_city', 'class']
    numerical_cols = ['stops', 'duration', 'days_left']

    # Preprocessing pipelines for both numeric and categorical data
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_cols),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_cols)
        ])

    # Define the model pipeline
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=150, max_depth=30, min_samples_leaf=5, min_samples_split=30, random_state=42))
    ])

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train model
    model.fit(X_train, y_train)

    # Predict and evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # Save model and preprocessor
    with open(MODEL_FILE, 'wb') as f:
        pickle.dump(model, f)

    return {'mae': mae, 'r2': r2}

def load_model():
    if not os.path.exists(MODEL_FILE):
        raise FileNotFoundError("Model file not found. Train the model first.")
    with open(MODEL_FILE, 'rb') as f:
        model = pickle.load(f)
    return model

import os
import pandas as pd
import numpy as np
import pickle
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, r2_score

MODEL_FILE = 'media/new_rf_model.pkl'
PREPROCESSOR_FILE = 'media/preprocessor.pkl'
DATA_FILE = 'media/Indian_Airlines_cleaned_data.csv'

import glob

# Load data once and compute median price for fallback
_data_cache = None
_median_price = None

def load_data():
    global _data_cache, _median_price
    if _data_cache is None:
        media_files = glob.glob('media/*.csv')
        dataset_files = glob.glob('dataset/*.csv')
        all_files = list(set(media_files + dataset_files))  # unique files

        dataframes = []
        for file in all_files:
            try:
                df = pd.read_csv(file)
                dataframes.append(df)
            except Exception as e:
                print(f"Error loading {file}: {e}")

        if not dataframes:
            raise ValueError("No datasets loaded. Please check dataset files.")

        data = pd.concat(dataframes, ignore_index=True, sort=False)
        data = data.drop_duplicates()
        _data_cache = data
        _median_price = data['price'].median()
    return _data_cache

def get_median_price():
    global _median_price
    if _median_price is None:
        load_data()
    return _median_price

def load_model():
    if not os.path.exists(MODEL_FILE):
        raise FileNotFoundError("Model file not found. Train the model first.")
    with open(MODEL_FILE, 'rb') as f:
        model = pickle.load(f)
    return model

def predict(input_data):
    model = load_model()

    # Convert input_data to DataFrame
    input_df = pd.DataFrame([input_data])

    # Validate input columns
    expected_features = ['airline', 'source_city', 'departure_time', 'stops', 'arrival_time', 'destination_city', 'class', 'duration', 'days_left']
    missing_features = [feat for feat in expected_features if feat not in input_df.columns]
    if missing_features:
        # Instead of raising error, return median price
        return get_median_price()

    try:
        prediction = model.predict(input_df)
        return prediction[0]
    except Exception:
        # Return median price as fallback
        return get_median_price()
