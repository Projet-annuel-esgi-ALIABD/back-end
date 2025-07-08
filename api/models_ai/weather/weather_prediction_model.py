import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os
import time
import xgboost as xgb


class WeatherPredictionModel:
    """
    A class to process weather data and build prediction models
    """

    def __init__(
        self,
        data_path=None,
        input_features=None,
        target_feature="TX",
        days_to_predict=1,
    ):
        """
        Initialize the model

        Args:
            data_path (str): Path to the CSV data file
            input_features (list): List of features to use for prediction
            target_feature (str): Weather variable to predict (e.g., 'TX' for max temperature)
            days_to_predict (int): Number of days ahead to predict
        """
        self.data_path = data_path
        self.target_feature = target_feature
        self.input_features = input_features or ["RR", "TN", "TM", "TX", "TAMPLI"]
        self.days_to_predict = days_to_predict
        self.model = None
        self.scaler = None
        self.features = None
        self.weather_data = None

    def load_data(self):
        """
        Load and preprocess weather data, filtering to only include input_features

        Returns:
            pd.DataFrame: The loaded and preprocessed data
        """
        print(f"Loading data from {self.data_path}")
        try:
            # Load the data
            df = pd.read_csv(self.data_path, sep=";")

            # Convert date column to datetime
            if "DATE" in df.columns:
                df["DATE"] = pd.to_datetime(df["DATE"])
                # Set date as index
                df.set_index("DATE", inplace=True)

            # Keep only relevant columns (input_features + target_feature)
            relevant_columns = self.input_features.copy()
            if self.target_feature not in relevant_columns:
                relevant_columns.append(self.target_feature)

            # Filter columns that exist in the dataframe
            available_columns = [col for col in relevant_columns if col in df.columns]
            print(f"Available columns in the dataset: {available_columns}")
            # Select only the relevant columns
            df = df[available_columns]

            print(f"Original shape: {df.shape}")
            print(f"Using only {len(available_columns)} columns: {available_columns}")
            print(f"Missing values before cleaning:\n{df.isnull().sum()}")

            # For numeric columns, fill NaN with the median
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                df[col] = df[col].fillna(df[col].median())

            # Remove rows still containing NaN values in critical columns
            if self.target_feature in df.columns:
                df = df.dropna(subset=[self.target_feature])

            print(f"Shape after cleaning: {df.shape}")
            print(f"Missing values after cleaning:\n{df.isnull().sum()}")

            self.weather_data = df
            return df

        except Exception as e:
            print(f"Error loading data: {e}")
            return None

    def load_data_from_dataframe(self, df):
        """
        Load data from a pandas DataFrame instead of CSV file

        Args:
            df (pd.DataFrame): Weather data DataFrame

        Returns:
            pd.DataFrame: The loaded and preprocessed data
        """
        print("Loading data from DataFrame")
        try:
            # Convert date column to datetime if it exists
            if "DATE" in df.columns:
                df["DATE"] = pd.to_datetime(df["DATE"])
                # Set date as index
                df.set_index("DATE", inplace=True)

            # Keep only relevant columns (input_features + target_feature)
            relevant_columns = self.input_features.copy()
            if self.target_feature not in relevant_columns:
                relevant_columns.append(self.target_feature)

            # Filter columns that exist in the dataframe
            available_columns = [col for col in relevant_columns if col in df.columns]
            print(f"Available columns in the dataset: {available_columns}")
            # Select only the relevant columns
            df = df[available_columns]

            print(f"Original shape: {df.shape}")
            print(f"Using only {len(available_columns)} columns: {available_columns}")

            # Convert comma-separated decimal values to periods if they are strings
            for col in df.select_dtypes(include=["object"]).columns:
                if col != "DATE":  # Skip date column
                    df[col] = df[col].astype(str).str.replace(",", ".").astype(float)

            # For numeric columns, fill NaN with the median
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                df[col] = df[col].fillna(df[col].median())

            # Remove rows still containing NaN values in critical columns
            if self.target_feature in df.columns:
                df = df.dropna(subset=[self.target_feature])

            print(f"Shape after cleaning: {df.shape}")
            print(f"Missing values after cleaning:\n{df.isnull().sum()}")

            self.weather_data = df
            return df

        except Exception as e:
            print(f"Error loading data from DataFrame: {e}")
            return None

    def preprocess_data(self):
        """
        Preprocess data for modeling: feature engineering and data splitting

        Returns:
            tuple: X_train, X_test, y_train, y_test
        """
        if self.weather_data is None:
            if self.data_path:
                self.load_data()
            else:
                raise ValueError("No data available. Please load data first.")

        df = self.weather_data.copy()

        # Convert comma-separated decimal values to periods
        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].str.replace(",", ".").astype(float)

        # Create lag features (previous days' values)
        for i in range(1, 8):  # Past 7 days as features
            for col in [
                "TX",
                "TN",
                "RR",
                "FFM",
            ]:  # Max temp, min temp, precipitation, wind
                if col in df.columns:
                    df[f"{col}_lag_{i}"] = df[col].shift(i)

        # Create rolling window features (averages over different periods)
        for window in [3, 7, 14]:
            for col in ["TX", "TN", "RR", "FFM"]:
                if col in df.columns:
                    df[f"{col}_rolling_{window}"] = (
                        df[col].rolling(window=window).mean()
                    )

        # Add day of year as a feature (seasonal patterns)
        df["dayofyear"] = df.index.dayofyear
        df["month"] = df.index.month

        # Create target variable (future temperature)
        df[f"{self.target_feature}_target"] = df[self.target_feature].shift(
            -self.days_to_predict
        )

        # Drop rows with NaN due to shifts
        df = df.dropna()

        # Prepare features and target
        y = df[f"{self.target_feature}_target"]

        # Exclude the target column and any date columns
        exclude_cols = [f"{self.target_feature}_target"]
        X = df.drop(columns=exclude_cols)

        print(f"Features used for training: {X.columns.tolist()}")
        print(f"Target variable: {self.target_feature}_target")
        print(f"Shape of features: {X.shape}")
        print(f"Shape of target: {y.shape}")

        # Store features for later use in prediction
        self.features = X.columns.tolist()

        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=False
        )

        # Scale the features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        return (
            X_train_scaled,
            X_test_scaled,
            y_train,
            y_test,
            X_train.index,
            X_test.index,
        )

    def build_model(self):
        """
        Build and train the prediction model

        Returns:
            xgb.XGBRegressor: The trained model
        """
        # Preprocess data
        X_train_scaled, X_test_scaled, y_train, y_test, train_idx, test_idx = (
            self.preprocess_data()
        )

        # Initialize and train the model
        print("Training XGBoost model...")
        start_time = time.time()

        xgb_model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.01,
            reg_lambda=1,
            random_state=42,
            n_jobs=-1,
        )

        # Train the model
        xgb_model.fit(
            X_train_scaled,
            y_train,
            eval_set=[(X_test_scaled, y_test)],
            sample_weight=None,
            verbose=False,
        )

        training_time = time.time() - start_time
        print(f"Model training completed in {training_time:.2f} seconds")

        self.model = xgb_model

        # Make predictions
        y_pred_train = xgb_model.predict(X_train_scaled)
        y_pred_test = xgb_model.predict(X_test_scaled)

        # Evaluate the model
        train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
        test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
        train_mae = mean_absolute_error(y_train, y_pred_train)
        test_mae = mean_absolute_error(y_test, y_pred_test)
        train_r2 = r2_score(y_train, y_pred_train)
        test_r2 = r2_score(y_test, y_pred_test)

        print(f"Train RMSE: {train_rmse:.2f}")
        print(f"Test RMSE: {test_rmse:.2f}")
        print(f"Train MAE: {train_mae:.2f}")
        print(f"Test MAE: {test_mae:.2f}")
        print(f"Train R²: {train_r2:.4f}")
        print(f"Test R²: {test_r2:.4f}")

        # Save evaluation metrics
        metrics = {
            "train_rmse": train_rmse,
            "test_rmse": test_rmse,
            "train_mae": train_mae,
            "test_mae": test_mae,
            "train_r2": train_r2,
            "test_r2": test_r2,
            "training_time": training_time,
        }

        return xgb_model, metrics

    def save_model(self, path="models"):
        """
        Save the trained model and scaler

        Args:
            path (str): Directory to save the model

        Returns:
            bool: True if successful, False otherwise
        """
        if self.model is None:
            print("No model to save. Please train a model first.")
            return False

        try:
            # Create directory if it doesn't exist
            if not os.path.exists(path):
                os.makedirs(path)

            # Save the model
            model_file = os.path.join(
                path, f"model_{self.target_feature}_{self.days_to_predict}day.joblib"
            )
            joblib.dump(self.model, model_file)

            # Save the scaler
            scaler_file = os.path.join(
                path, f"scaler_{self.target_feature}_{self.days_to_predict}day.joblib"
            )
            joblib.dump(self.scaler, scaler_file)

            # Save features list
            features_file = os.path.join(
                path, f"features_{self.target_feature}_{self.days_to_predict}day.txt"
            )
            with open(features_file, "w") as f:
                f.write("\n".join(self.features))

            print(f"Model and associated files saved to {path}")
            return True

        except Exception as e:
            print(f"Error saving model: {e}")
            return False

    def load_model(self, path="models"):
        """
        Load a previously saved model and scaler

        Args:
            path (str): Directory where the model is saved

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Load the model
            model_file = os.path.join(
                path, f"model_{self.target_feature}_{self.days_to_predict}day.joblib"
            )
            self.model = joblib.load(model_file)

            # Load the scaler
            scaler_file = os.path.join(
                path, f"scaler_{self.target_feature}_{self.days_to_predict}day.joblib"
            )
            self.scaler = joblib.load(scaler_file)

            # Load features list
            features_file = os.path.join(
                path, f"features_{self.target_feature}_{self.days_to_predict}day.txt"
            )
            with open(features_file, "r") as f:
                self.features = f.read().splitlines()

            print(f"Model and associated files loaded from {path}")
            return True

        except Exception as e:
            print(f"Error loading model: {e}")
            return False

    def make_prediction(self, latest_data):
        """
        Make a prediction using the trained model

        Args:
            latest_data (pd.DataFrame): Latest weather data with required features

        Returns:
            float: Predicted value
        """
        if self.model is None:
            print("No model available. Please train or load a model first.")
            return None

        # Prepare the data similar to training
        df = latest_data.copy()

        # Convert comma-separated decimal values to periods
        for col in df.select_dtypes(include=["object"]).columns:
            if col != "DATE":
                df[col] = df[col].astype(str).str.replace(",", ".").astype(float)

        # Create lag features (previous days' values)
        for i in range(1, 8):  # Past 7 days as features
            for col in [
                "TX",
                "TN",
                "RR",
                "FFM",
            ]:  # Max temp, min temp, precipitation, wind
                if col in df.columns:
                    df[f"{col}_lag_{i}"] = df[col].shift(i)

        # Create rolling window features (averages over different periods)
        for window in [3, 7, 14]:
            for col in ["TX", "TN", "RR", "FFM"]:
                if col in df.columns:
                    df[f"{col}_rolling_{window}"] = (
                        df[col].rolling(window=window).mean()
                    )

        # Add day of year as a feature (seasonal patterns)
        df["dayofyear"] = df.index.dayofyear
        df["month"] = df.index.month

        # Drop rows with NaN due to shifts and rolling windows
        df = df.dropna()

        if df.empty:
            print("No valid data available for prediction after preprocessing")
            return None

        # Take the last row for prediction
        latest_row = df.iloc[-1:][self.features]

        if not all(feature in latest_row.columns for feature in self.features):
            missing = [f for f in self.features if f not in latest_row.columns]
            print(f"Error: Missing features: {missing}")
            return None

        # Scale features
        X_scaled = self.scaler.transform(latest_row)

        # Make prediction
        prediction = self.model.predict(X_scaled)

        return prediction[0]
