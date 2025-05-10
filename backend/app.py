from flask import Flask, request, jsonify
import joblib
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load all 5 artifacts
label_mappings = joblib.load('label_encoders.pkl')       # shared LabelEncoder logic
cat_scalers    = joblib.load('cat_scalers.pkl')          # one StandardScaler per categorical column
scaler_age     = joblib.load('scaler_age.pkl')           # MinMaxScaler for age
scaler_glucose = joblib.load('scaler_glucose.pkl')       # MinMaxScaler for avg_glucose_level
clf            = joblib.load('rf_model.pkl')

# Columns
cat_cols = ['gender', 'ever_married', 'work_type', 'Residence_type', 'smoking_status']
num_cols = ['age', 'avg_glucose_level']
all_cols = cat_cols + num_cols

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    print("🟡 Received payload:", data)

    if not data:
        print("🔴 Empty or invalid payload.")
        return jsonify({'error': 'Invalid or empty JSON payload'}), 400

    if 'features' in data and isinstance(data['features'], dict):
        data = data['features']
        print("🟡 Unwrapped 'features':", data)

    missing = [col for col in all_cols if col not in data]
    if missing:
        print("🔴 Missing fields:", missing)
        return jsonify({'error': 'Missing fields', 'missing_fields': missing}), 422

    try:
        print("🛠️ Starting transformation...")

        # Encode and scale categoricals
        cat_scaled = []
        for col in cat_cols:
            encoder = label_mappings[col]
            print(f"🔍 Encoding {col}: {data[col]}")
            value_encoded = encoder.transform([data[col]])[0]
            print(f"✅ Encoded {col}: {value_encoded}")
            scaled = cat_scalers[col].transform([[value_encoded]])[0][0]
            print(f"✅ Scaled {col}: {scaled}")
            cat_scaled.append(scaled)

        # Scale numerics
        age_val = float(data['age'])
        glucose_val = float(data['avg_glucose_level'])
        print(f"🔍 Scaling age: {age_val}")
        age_scaled = scaler_age.transform([[age_val]])[0][0]
        print(f"✅ Scaled age: {age_scaled}")

        print(f"🔍 Scaling glucose: {glucose_val}")
        glucose_scaled = scaler_glucose.transform([[glucose_val]])[0][0]
        print(f"✅ Scaled glucose: {glucose_scaled}")

    except Exception as e:
        print("🔴 Transformation error:", str(e))
        return jsonify({'error': 'Transformation error', 'details': str(e)}), 422

    # Combine all features
    try:
        # Reconstruct feature vector in training order:
        # ['gender', 'age', 'ever_married', 'work_type', 'Residence_type', 'avg_glucose_level', 'smoking_status']
        ordered_values = [
            cat_scaled[0],   # gender
            age_scaled,      # age
            cat_scaled[1],   # ever_married
            cat_scaled[2],   # work_type
            cat_scaled[3],   # Residence_type
            glucose_scaled,  # avg_glucose_level
            cat_scaled[4],   # smoking_status
        ]

        ordered_cols = [
            'gender', 'age', 'ever_married', 'work_type',
            'Residence_type', 'avg_glucose_level', 'smoking_status'
        ]

        X_final = pd.DataFrame([ordered_values], columns=ordered_cols)
        print("🟢 Final feature vector:", X_final.to_dict(orient="records"))
        
        # Predict
        probs = clf.predict_proba(X_final)[0]
        return jsonify({
            'no_stroke_probability': float(probs[0]),
            'stroke_probability': float(probs[1])
        })

    except Exception as e:
        print("🔴 Prediction error:", str(e))
        return jsonify({'error': 'Prediction error', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
