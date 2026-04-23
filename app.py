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
        filepath = os.path.join("uploads", file.filename)
        file.save(filepath)

        # Read CSV
        df = pd.read_csv(filepath)

        # Validate columns
        if target not in df.columns or sensitive not in df.columns:
            return "Error: Column names not found in dataset"

        # Ensure target is numeric (0/1)
        df[target] = pd.to_numeric(df[target], errors='coerce')

        # Drop missing values
        df = df.dropna(subset=[target, sensitive])

        # Calculate selection rates
        result = df.groupby(sensitive)[target].mean()

        # Convert to dictionary
        result_dict = result.to_dict()

        # Calculate bias gap (for 2 groups)
        if len(result) >= 2:
            values = list(result)
            bias_gap = abs(values[0] - values[1])
        else:
            bias_gap = 0

        # Bias decision
        if bias_gap > 0.2:
            bias_message = "⚠️ Potential bias detected"
        else:
            bias_message = "✅ No significant bias detected"

        # 🧠 Generate AI explanation
        prompt = f"""
        Dataset results:
        {result_dict}

        Explain in simple terms whether there is bias.
        Also suggest 2 ways to fix it.
        """

        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        explanation = response.text

        # Send to result page
        return render_template(
            "result.html",
            result=result_dict,
            bias=bias_message,
            explanation=explanation
        )

    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == '__main__':
    # Create uploads folder if not exists
    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    app.run(debug=True)