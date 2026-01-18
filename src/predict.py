"""
Prediction module for making predictions on new data.
"""
import pickle
import pandas as pd

def load_model(model_path):
    """
    Load trained model from file.
    
    Args:
        model_path: Path to model file
        
    Returns:
        Loaded model
    """
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    return model

def make_predictions(model, X):
    """
    Make predictions using trained model.
    
    Args:
        model: Trained model
        X: Features
        
    Returns:
        Predictions
    """
    return model.predict(X)
