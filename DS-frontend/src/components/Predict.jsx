// src/components/Predict.jsx
import React, { useState } from 'react';
import '../styling/Predict.css';

const Predict = () => {
  // form state
  const [form, setForm] = useState({
    gender: '',
    age: '',
    ever_married: '',
    work_type: '',
    Residence_type: '',
    avg_glucose_level: '',
    smoking_status: '',
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  // handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
  };

  // simple validation
  const validate = () => {
    const errs = {};
    if (!form.gender)            errs.gender = 'Required';
    if (!form.age || form.age <= 0)           errs.age = 'Enter a positive age';
    if (!form.ever_married)      errs.ever_married = 'Required';
    if (!form.work_type)         errs.work_type = 'Required';
    if (!form.Residence_type)    errs.Residence_type = 'Required';
    if (!form.avg_glucose_level || form.avg_glucose_level <= 0)
                                 errs.avg_glucose_level = 'Enter a positive number';
    if (!form.smoking_status)    errs.smoking_status = 'Required';
    return errs;
  };

  // on submit
  const handleSubmit = async (e) => {
    e.preventDefault();
    setResult(null);
    const errs = validate();
    setErrors(errs);
    if (Object.keys(errs).length) return;

    setLoading(true);
    try {
      // Option A: send raw form data and let backend transform
      const payload = { ...form, age: Number(form.age), avg_glucose_level: Number(form.avg_glucose_level) };

      // Option B: frontend-side transform (uncomment & adjust to match your scaler/encoders)
      // const payload = transform(form);

      const res = await fetch('http://127.0.0.1:5000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ features: payload }),
      });
      if (!res.ok) throw new Error(`Status ${res.status}`);
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      setResult({ error: err.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="predict-container">
      <h2>Stroke Prediction</h2>
      <form onSubmit={handleSubmit} noValidate>
        {[
          { label: 'Gender', name: 'gender', type: 'select', options: ['', 'Male', 'Female'] },
          { label: 'Age (years)', name: 'age', type: 'number' },
          { label: 'Ever Married', name: 'ever_married', type: 'select', options: ['', 'Yes', 'No'] },
          { label: 'Work Type', name: 'work_type', type: 'select', options: ['', 'Private', 'Self-employed', 'Govt_job', 'children', 'Never_worked'] },
          { label: 'Residence', name: 'Residence_type', type: 'select', options: ['', 'Urban', 'Rural'] },
          { label: 'Avg Glucose Level (mg/dl)', name: 'avg_glucose_level', type: 'number', step: 'any' },
          { label: 'Smoking Status', name: 'smoking_status', type: 'select', options: ['', 'formerly smoked', 'never smoked', 'smokes', 'Unknown'] },
        ].map(field => (
          <div className="field" key={field.name}>
            <label htmlFor={field.name}>{field.label}:</label>
            {field.type === 'select' ? (
              <select
                id={field.name}
                name={field.name}
                value={form[field.name]}
                onChange={handleChange}
              >
                {field.options.map(opt => (
                  <option key={opt} value={opt}>{opt || '-- select --'}</option>
                ))}
              </select>
            ) : (
              <input
                id={field.name}
                name={field.name}
                type={field.type}
                step={field.step}
                value={form[field.name]}
                onChange={handleChange}
              />
            )}
            {errors[field.name] && (
              <div className="error">{errors[field.name]}</div>
            )}
          </div>
        ))}

        <button id='predict-btn' type="submit" disabled={loading}>
          {loading ? 'Predicting…' : 'Submit'}
        </button>
      </form>

      {result && (
        <div className="result">
          {result.error ? (
            <p className="error">Error: {result.error}</p>
          ) : (
            <>
              <p>
                <strong>Prediction:</strong>{' '}
                {result.prediction === 1 ? 'Stroke' : 'No Stroke'}
              </p>
              <p>
                <strong>Probabilities:</strong><br />
                No Stroke: {(result.no_stroke_probability * 100).toFixed(1)}%<br/>
                Stroke:    {(result.stroke_probability   * 100).toFixed(1)}%

              </p>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default Predict;
