"""
Feature engineering module for creating new features.
"""
import pandas as pd
import numpy as np

def create_features(df):
    """
    Create new features from existing columns.
    
    Args:
        df: Input dataframe
        
    Returns:
        Dataframe with engineered features
    """
    # Example feature engineering
    df['feature_interaction'] = df['feature1'] * df['feature2']
    df['feature_sum'] = df['feature1'] + df['feature2'] + df['feature3']
    
    return df
