# train_models.py
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import f1_score

try:
    from xgboost import XGBClassifier
except ImportError:
    XGBClassifier = None

def extract_features(df_consumption):
    features = pd.DataFrame()
    features['mean_consumption'] = df_consumption.mean(axis=1)
    features['std_consumption'] = df_consumption.std(axis=1).fillna(0)
    features['max_consumption'] = df_consumption.max(axis=1)
    features['min_consumption'] = df_consumption.min(axis=1)
    features['median_consumption'] = df_consumption.median(axis=1)
    features['zero_count'] = (df_consumption == 0).sum(axis=1)
    features['peak_ratio'] = features['max_consumption'] / (features['mean_consumption'] + 1e-6)
    return features

def main():
    print("Preparing training dataset...")
    # Mock data generator (Simulating SGCC Smart-Meter dataset structure)
    np.random.seed(42)
    n_samples = 1200
    days = 30
    
    # 85% normal usage, 15% theft patterns
    normal_usage = np.random.normal(loc=18, scale=3, size=(int(n_samples * 0.85), days)).clip(min=0)
    theft_usage = np.random.normal(loc=4, scale=1.5, size=(int(n_samples * 0.15), days)).clip(min=0)
    
    consumption = np.vstack([normal_usage, theft_usage])
    labels = np.array([0] * int(n_samples * 0.85) + [1] * int(n_samples * 0.15))
    
    df_raw = pd.DataFrame(consumption, columns=[f'day_{i+1}' for i in range(days)])
    
    # Feature Engineering
    X = extract_features(df_raw)
    y = labels
    
    # Split & Scale
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Algorithms to train and compare
    models = {
        'RandomForest': RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42),
        'SVM': SVC(kernel='rbf', probability=True, class_weight='balanced', random_state=42),
    }
    if XGBClassifier is not None:
        models['XGBoost'] = XGBClassifier(n_estimators=100, eval_metric='logloss', random_state=42)

    best_model = None
    best_f1 = -1.0
    best_name = ""
    
    for name, model in models.items():
        model.fit(X_train_scaled, y_train)
        preds = model.predict(X_test_scaled)
        score = f1_score(y_test, preds)
        print(f"Model: {name} | F1-Score: {score:.4f}")
        
        if score > best_f1:
            best_f1 = score
            best_model = model
            best_name = name
            
    print(f"\nBest Model: {best_name} (Saved to disk)")
    joblib.dump(best_model, 'theft_detection_model.pkl')
    joblib.dump(scaler, 'scaler.pkl')

    # Generate a sample CSV file for dashboard testing
    test_df = pd.DataFrame(consumption[:25], columns=[f'day_{i+1}' for i in range(days)])
    test_df.insert(0, 'consumer_id', [f'CUST-{1000+i}' for i in range(25)])
    test_df.insert(1, 'consumer_name', [f'User {i+1}' for i in range(25)])
    test_df.insert(2, 'meter_number', [f'MTR-{5000+i}' for i in range(25)])
    test_df.insert(3, 'area', ['Feeder-1' if i % 2 == 0 else 'Feeder-2' for i in range(25)])
    test_df.to_csv('sample_smart_meter_data.csv', index=False)
    print("Generated 'sample_smart_meter_data.csv' for testing.")

if __name__ == '__main__':
    main()