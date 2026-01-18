"""
Main execution script for the ML pipeline.
"""
import pandas as pd
import pickle
import os
from data_cleaning import clean_data
from feature_engineering import create_features
from train_model import train_model, evaluate_model
from predict import make_predictions

def main():
    """
    Execute the complete ML pipeline.
    """
    # Load data
    train_df = pd.read_csv('../data/sample_train.csv')
    test_df = pd.read_csv('../data/sample_test.csv')
    
    # Clean data
    train_df = clean_data(train_df)
    test_df = clean_data(test_df)
    
    # Feature engineering
    train_df = create_features(train_df)
    test_df = create_features(test_df)
    
    # Prepare features and target
    X_train = train_df.drop(['id', 'target'], axis=1)
    y_train = train_df['target']
    X_test = test_df.drop(['id'], axis=1)
    test_ids = test_df['id']
    
    # Train model
    model = train_model(X_train, y_train)
    
    # Evaluate on training set
    metrics = evaluate_model(model, X_train, y_train)
    
    # Make predictions
    predictions = make_predictions(model, X_test)
    
    # Create submission
    submission = pd.DataFrame({
        'id': test_ids,
        'prediction': predictions
    })
    
    # Save outputs
    os.makedirs('../outputs', exist_ok=True)
    submission.to_csv('../outputs/submission.csv', index=False)
    
    with open('../outputs/metrics.txt', 'w') as f:
        for metric, value in metrics.items():
            f.write(f"{metric}: {value:.4f}\n")
    
    with open('../outputs/model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    print("Pipeline completed successfully!")
    print(f"Metrics: {metrics}")

if __name__ == '__main__':
    main()
