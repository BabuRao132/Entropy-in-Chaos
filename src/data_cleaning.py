"""
Data cleaning module for preprocessing raw data.
"""
import pandas as pd
import numpy as np

def clean_data(df):
    """
    Clean and preprocess the data.
    
    Args:
        df: Input dataframe
        
    Returns:
        Cleaned dataframe
    """
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Handle missing values
    df = df.fillna(df.mean())
    
    return df
