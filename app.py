from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import google.generativeai as genai
import traceback
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__)

# store last result for chatbot
latest_result = {}

# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template('index.html')


# ---------------- ANALYZE ----------------
@app.route('/analyze', methods=['POST'])
def analyze():
    print("ANALYZE ROUTE HIT")
    global latest_result

    try:
        file = request.files['file']
        target = request.form['target']
        sensitive = request.form['sensitive']

        if not file.filename.endswith('.csv'):
            return render_template('index.html', error="Only CSV files allowed")

        os.makedirs("uploads", exist_ok=True)
        filepath = os.path.join("uploads", file.filename)
        file.save(filepath)

        df = pd.read_csv(filepath)

        if target not in df.columns or sensitive not in df.columns:
            return render_template('index.html', error="Column not found")

        df[target] = pd.to_numeric(df[target], errors='coerce')
        df = df.dropna(subset=[target, sensitive])

        # ✅ selection rate
        result = df.groupby(sensitive)[target].mean()

        result_dict = {
            str(k): round(float(v) * 100, 2)
            for k, v in result.items()
        }

        # ✅ FIXED bias logic
        values = list(result)
        bias_gap = round((max(values) - min(values)) * 100, 2) if len(values) > 1 else 0

        if bias_gap > 20:
            bias_message = "⚠️ Potential bias detected"
            bias_class = "alert-warning"
        else:
            bias_message = "✅ No significant bias detected"
            bias_class = "alert-ok"

        # AI explanation
        prompt = f"""
        Bias analysis results:
        {result_dict}
        Bias gap: {bias_gap}%

        Explain simply and suggest fixes.
        """

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        explanation = response.text

        # store for chatbot
        latest_result = {
            "result": result_dict,
            "bias_gap": bias_gap,
            "message": bias_message
        }

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
        print("ANALYZE ERROR:", e)
        traceback.print_exc()
        return render_template('index.html', error=str(e))


# ---------------- CHATBOT ----------------
@app.route('/chat', methods=['POST'])
def chat():
    try:
        if not latest_result:
            return jsonify({"reply": "Please run an analysis first."})

        data = request.json
        user_question = data.get("question")

        prompt = f"""
        You are FairLens AI assistant.

        Current Analysis:
        {latest_result}

        User Question:
        {user_question}

        Answer clearly in simple language.
        """

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)

        return jsonify({"reply": response.text})

    except Exception as e:
        print("CHAT ERROR:", e)
        traceback.print_exc()
        return jsonify({"reply": str(e)})


# ---------------- RUN ----------------
if __name__ == '__main__':
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)