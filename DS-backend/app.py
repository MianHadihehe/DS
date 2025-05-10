from flask import Flask, request, jsonify
import joblib
import numpy as np
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 

# Load your artifacts
label_encoders = joblib.load('label_encoders.pkl')
scaler_cat      = joblib.load('scaler_cat.pkl')
scaler_num      = joblib.load('scaler_num.pkl')
clf             = joblib.load('rf_model.pkl')

cat_cols = ['gender', 'ever_married', 'work_type', 'Residence_type', 'smoking_status']
num_cols = ['age', 'avg_glucose_level']
all_cols = cat_cols + num_cols

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    if not data:
        return jsonify({'error': 'Invalid or empty JSON payload'}), 400

    # 1. Unwrap nested "features" if needed
    if 'features' in data and isinstance(data['features'], dict):
        data = data['features']

    # 2. Check for missing fields
    missing = [col for col in all_cols if col not in data]
    if missing:
        return jsonify({
            'error': 'Missing fields in payload',
            'missing_fields': missing
        }), 422

    # 3. Encode & scale categoricals
    try:
        cat_enc = [
            label_encoders[col].transform([data[col]])[0]
            for col in cat_cols
        ]
    except Exception as e:
        return jsonify({
            'error': f'Error encoding "{col}"',
            'details': str(e)
        }), 422
    cat_scaled = scaler_cat.transform([cat_enc])[0]

    # 4. Scale numerics
    try:
        num_raw = [float(data[col]) for col in num_cols]
    except ValueError:
        return jsonify({
            'error': 'Numeric features must be convertible to float',
            'num_cols': num_cols
        }), 422
    num_scaled = scaler_num.transform([num_raw])[0]

    # 5. Build feature vector & get probabilities
    X_new = np.concatenate([cat_scaled, num_scaled]).reshape(1, -1)
    probs = clf.predict_proba(X_new)[0]
    no_stroke_prob = float(probs[0])
    stroke_prob    = float(probs[1])

    return jsonify({
        'no_stroke_probability': no_stroke_prob,
        'stroke_probability': stroke_prob
    })

if __name__ == '__main__':
    app.run(debug=True)

