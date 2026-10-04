import os
import joblib
import numpy as np
import pandas as pd
import shap
from django.shortcuts import render
from django.conf import settings
from .models import ConsumerRecord

MODEL_PATH = os.path.join(settings.BASE_DIR, 'theft_detection_model.pkl')
SCALER_PATH = os.path.join(settings.BASE_DIR, 'scaler.pkl')

FEATURE_LABELS = {
    'mean_consumption': 'Average Consumption',
    'std_consumption': 'Consumption Variance',
    'max_consumption': 'Peak Consumption',
    'min_consumption': 'Minimum Consumption',
    'median_consumption': 'Typical Consumption',
    'zero_count': 'Zero Consumption Days',
    'peak_ratio': 'Peak/Mean Ratio',
}

ANOMALY_LEVELS = (
    ('normal', 'Normal', 'normal'),
    ('slight', 'Slight Anomaly', 'slight'),
    ('suspicious', 'Suspicious', 'suspicious'),
    ('high', 'Highly Anomalous', 'high'),
)


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


def get_numeric_consumption_frame(df):
    normalized_columns = [str(col).strip().lower() for col in df.columns]
    df = df.copy()
    df.columns = normalized_columns

    meta_cols = ['consumer_id', 'consumer_name', 'meter_number', 'area', 'cons_no', 'flag', 'target', 'label']
    present_meta = [col for col in meta_cols if col in df.columns]

    consumption_frame = df.drop(columns=present_meta, errors='ignore')
    consumption_frame = consumption_frame.apply(pd.to_numeric, errors='coerce')
    consumption_frame = consumption_frame.dropna(axis=1, how='all')

    if consumption_frame.empty:
        raise ValueError('No numeric consumption columns were found in the uploaded CSV file.')

    return consumption_frame


def get_shap_explanation(model, scaled_features, feature_names, row_index):
    """Return serializable class-1 SHAP contributions for one prediction."""
    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(scaled_features)
        if isinstance(shap_values, list):
            values = shap_values[1 if len(shap_values) > 1 else 0][row_index]
        else:
            values = shap_values[row_index]
            if getattr(values, 'ndim', 1) == 2:
                values = values[:, 1]

        contributions = [
            {
                'feature': feature,
                'label': FEATURE_LABELS.get(feature, feature.replace('_', ' ').title()),
                'value': round(float(value), 5),
                'percentage': round(float(value) * 100, 2),
                'bar_width': min(round(abs(float(value)) * 100, 2), 100),
                'direction': 'increases' if value >= 0 else 'reduces',
            }
            for feature, value in zip(feature_names, values)
        ]
        return sorted(contributions, key=lambda item: abs(item['value']), reverse=True)
    except Exception:
        return []


def get_anomaly_calendar(consumption_row):
    """Classify each available period using z-score thresholds.

    Monthly columns are used when present. For this project's day_1..day_30
    input, the available sequence is split into up to 12 equal periods so no
    months are invented beyond the uploaded observations.
    """
    values = pd.to_numeric(consumption_row, errors='coerce').dropna()
    if values.empty:
        return []

    monthly_columns = [column for column in values.index if str(column).lower()[:3] in {
        'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'
    }]
    if monthly_columns:
        periods = [(str(column)[:3].title(), float(values[column])) for column in monthly_columns]
    else:
        period_count = min(12, len(values))
        chunks = [chunk for chunk in np.array_split(values.to_numpy(), period_count)]
        periods = [(f'P{index + 1}', float(chunk.mean())) for index, chunk in enumerate(chunks) if len(chunk)]

    period_values = pd.Series([value for _, value in periods])
    mean = float(period_values.mean())
    std = float(period_values.std(ddof=0))
    calendar = []
    for label, value in periods:
        z_score = 0 if std == 0 else abs(value - mean) / std
        if z_score < 0.75:
            key, name, css = ANOMALY_LEVELS[0]
        elif z_score < 1.5:
            key, name, css = ANOMALY_LEVELS[1]
        elif z_score < 2.25:
            key, name, css = ANOMALY_LEVELS[2]
        else:
            key, name, css = ANOMALY_LEVELS[3]
        calendar.append({'label': label, 'value': round(value, 2), 'severity': key, 'name': name, 'css_class': css})
    return calendar


def dashboard_view(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        df = pd.read_csv(csv_file)

        if df.empty:
            return render(request, 'dashboard.html', {
                'records': ConsumerRecord.objects.none(),
                'total': 0,
                'suspicious': 0,
                'normal': 0,
            })

        try:
            consumption_series = get_numeric_consumption_frame(df)
        except ValueError:
            return render(request, 'dashboard.html', {
                'records': ConsumerRecord.objects.none(),
                'total': 0,
                'suspicious': 0,
                'normal': 0,
            })

        clean_series = consumption_series.interpolate(method='linear', axis=1).bfill(axis=1).ffill(axis=1)
        features = extract_features(clean_series)

        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        features_scaled = scaler.transform(features)

        feature_names = list(getattr(scaler, 'feature_names_in_', features.columns))

        preds = model.predict(features_scaled)
        probs = model.predict_proba(features_scaled)[:, 1]

        ConsumerRecord.objects.all().delete()
        for idx, row in df.iterrows():
            ConsumerRecord.objects.create(
                consumer_id=row.get('consumer_id', f'CID-{idx+1}'),
                consumer_name=row.get('consumer_name', f'Consumer {idx+1}'),
                meter_number=row.get('meter_number', f'MTR-{idx+100}'),
                area=row.get('area', 'Main Grid'),
                avg_consumption=features['mean_consumption'].iloc[idx],
                peak_consumption=features['max_consumption'].iloc[idx],
                prediction_result='Theft' if preds[idx] == 1 else 'Normal',
                theft_probability=round(float(probs[idx]) * 100, 2),
                shap_explanation=get_shap_explanation(model, features_scaled, feature_names, idx),
                anomaly_calendar=get_anomaly_calendar(clean_series.iloc[idx]),
            )

    records = ConsumerRecord.objects.all().order_by('-theft_probability')
    total = records.count()
    suspicious = records.filter(prediction_result='Theft').count()
    normal = total - suspicious

    return render(request, 'dashboard.html', {
        'records': records,
        'total': total,
        'suspicious': suspicious,
        'normal': normal,
    })