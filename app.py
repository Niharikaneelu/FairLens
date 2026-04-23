from flask import Flask, render_template, request
import pandas as pd
import os
import google.generativeai as genai

from config import GEMINI_API_KEY
genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__)

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Analyze route
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        file = request.files['file']
        target = request.form['target']
        sensitive = request.form['sensitive']

        # Save uploaded file temporarily
        os.makedirs("uploads", exist_ok=True)
        filepath = os.path.join("uploads", file.filename)
        file.save(filepath)

        # Read CSV
        df = pd.read_csv(filepath)

        # Validate columns
        if target not in df.columns or sensitive not in df.columns:
            return render_template('index.html', error="Error: Column names not found in dataset.")

        # Ensure target is numeric (0/1)
        df[target] = pd.to_numeric(df[target], errors='coerce')

        # Drop missing values
        df = df.dropna(subset=[target, sensitive])

        # Calculate selection rates per group
        result = df.groupby(sensitive)[target].mean()
        result_dict = {str(k): round(float(v) * 100, 1) for k, v in result.items()}

        # Calculate bias gap (for 2+ groups)
        if len(result) >= 2:
            values = list(result)
            bias_gap = round(abs(values[0] - values[1]) * 100, 1)
        else:
            bias_gap = 0

        # Bias decision
        if bias_gap > 20:
            bias_message = "⚠️ Potential bias detected"
            bias_class = "alert-warning"
        else:
            bias_message = "✅ No significant bias detected"
            bias_class = "alert-ok"

        # Generate AI explanation using Gemini
        prompt = f"""
        A bias analysis was run on a dataset.
        Selection rates by group ({sensitive}): {result_dict}
        Bias gap: {bias_gap}%

        Explain in simple terms whether there is bias and why it matters.
        Also suggest 2 concrete ways to fix it.
        Keep it concise (3-4 sentences).
        """

        # FIX: Use gemini-1.5-flash instead of deprecated gemini-pro
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        explanation = response.text

        return render_template(
            "result.html",
            result=result_dict,
            bias=bias_message,
            bias_class=bias_class,
            bias_gap=bias_gap,
            sensitive=sensitive,
            explanation=explanation
        )

    except Exception as e:
        return render_template('index.html', error=f"Error: {str(e)}")


if __name__ == '__main__':
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    app.run(debug=True)