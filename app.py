from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import os
import google.generativeai as genai
import traceback
from config import GEMINI_API_KEY

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__)

# store last result for chatbot
latest_result = {}


# ---------------- LOCAL EXPLANATION (no API needed) ----------------
def local_explanation(result_dict, bias_gap, disparate_impact, sensitive):
    """Generate a meaningful explanation from bias metrics without any API call."""
    groups = list(result_dict.keys())
    rates  = list(result_dict.values())

    if len(groups) < 2:
        return "Only one group found — cannot compare for bias."

    max_group = max(result_dict, key=result_dict.get)
    min_group = min(result_dict, key=result_dict.get)
    max_rate  = result_dict[max_group]
    min_rate  = result_dict[min_group]

    lines = []

    # --- Summary ---
    if bias_gap > 20 or disparate_impact < 0.8:
        lines.append(f"⚠️ **Bias Detected** in the `{sensitive}` attribute.")
    else:
        lines.append(f"✅ **No significant bias** found in the `{sensitive}` attribute.")

    lines.append("")

    # --- Group breakdown ---
    lines.append("**Group Selection Rates:**")
    for g, r in result_dict.items():
        bar = "█" * int(r / 5)
        lines.append(f"- {g}: {r}%  {bar}")

    lines.append("")

    # --- Bias gap ---
    lines.append(f"**Bias Gap:** {bias_gap}% — "
                 + ("This gap is large and indicates unfair disparity." if bias_gap > 20
                    else "This gap is within an acceptable range."))

    # --- Disparate impact ---
    lines.append(f"**Disparate Impact Ratio:** {disparate_impact} — "
                 + ("Below 0.8, which violates the 80% rule used in employment law."
                    if disparate_impact < 0.8
                    else "Above 0.8, which meets the standard fairness threshold."))

    lines.append("")

    # --- Plain-language finding ---
    if min_rate > 0:
        lines.append(f"**Finding:** The group `{max_group}` has the highest selection rate "
                     f"({max_rate}%), while `{min_group}` has the lowest ({min_rate}%). "
                     f"That means `{max_group}` is selected {round(max_rate / min_rate, 1)}x "
                     f"more often than `{min_group}`.")
    else:
        lines.append(f"**Finding:** The group `{max_group}` has the highest selection rate "
                     f"({max_rate}%), while `{min_group}` has the lowest ({min_rate}%). "
                     f"`{min_group}` has 0% selections, indicating an extreme disparity.")

    lines.append("")

    # --- Recommendations ---
    lines.append("**Recommendations to reduce bias:**")
    if bias_gap > 20 or disparate_impact < 0.8:
        lines.append("1. Review decision criteria — check if the selection process uses features that correlate with the sensitive attribute.")
        lines.append("2. Apply the reweighing mitigation above to download a balanced dataset for model retraining.")
        lines.append("3. Consider fairness-aware machine learning algorithms (e.g., adversarial debiasing).")
        lines.append("4. Audit historical data collection for underrepresentation of certain groups.")
    else:
        lines.append("1. Continue monitoring over time as new data is collected.")
        lines.append("2. Even without significant bias, consider disaggregated reporting across intersectional groups.")

    return "\n".join(lines)


# ---------------- LOCAL CHAT REPLY (no API needed) ----------------
def local_chat_reply(question, result):
    """Answer common chatbot questions from stored metrics without any API."""
    q = question.lower()
    rd = result.get("result", {})
    bg = result.get("bias_gap", 0)
    di = result.get("disparate_impact", 1)
    sens = result.get("sensitive", "the sensitive attribute")
    msg = result.get("message", "")

    if any(w in q for w in ["bias", "biased", "fair", "unfair"]):
        return (f"The analysis shows a bias gap of **{bg}%** and a disparate impact ratio of **{di}**. "
                + ("This indicates potential bias." if bg > 20 or di < 0.8 else "No significant bias was detected."))

    if any(w in q for w in ["group", "rate", "selection", "percent", "%"]):
        breakdown = ", ".join(f"{k}: {v}%" for k, v in rd.items())
        return f"Selection rates by `{sens}`: {breakdown}."

    if any(w in q for w in ["disparate", "impact", "ratio", "di"]):
        return (f"The Disparate Impact Ratio is **{di}**. "
                "A value below 0.8 typically indicates bias (the '80% rule'). "
                + ("This dataset is below that threshold." if di < 0.8 else "This dataset passes that threshold."))

    if any(w in q for w in ["fix", "mitigate", "reduce", "debias", "solution"]):
        return ("To reduce bias: (1) Use the 'Download Debiased Dataset' button to get a reweighed CSV. "
                "(2) Retrain your model on that balanced data. "
                "(3) Remove or transform features correlated with the sensitive attribute.")

    if any(w in q for w in ["gap", "difference", "diff"]):
        return f"The bias gap between the highest and lowest group is **{bg}%**."

    return (f"Based on the analysis: {msg}. "
            f"Bias gap: {bg}%, Disparate Impact: {di}. "
            "Try asking about 'selection rates', 'bias gap', 'disparate impact', or 'how to fix bias'.") 


def generate_gemini_text(prompt: str):
    """Return Gemini text if available; otherwise raise to trigger local fallback."""
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is missing")

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    response_text = getattr(response, "text", None)

    if not response_text:
        raise RuntimeError("Gemini returned an empty response")

    return response_text

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

        # Calculate Disparate Impact Ratio (min / max)
        disparate_impact = round(min(values) / max(values), 2) if len(values) > 1 and max(values) > 0 else 1.0

        if bias_gap > 20 or disparate_impact < 0.8:
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
        Disparate Impact Ratio: {disparate_impact} (Values < 0.8 typically indicate bias)

        Explain simply and suggest fixes.
        """

        try:
            explanation = generate_gemini_text(prompt)
        except Exception as api_e:
            print("Gemini API Error (using local explanation):", api_e)
            explanation = local_explanation(result_dict, bias_gap, disparate_impact, sensitive)

        # store for chatbot + mitigation
        latest_result = {
            "result": result_dict,
            "bias_gap": bias_gap,
            "disparate_impact": disparate_impact,
            "message": bias_message,
            "filepath": filepath,
            "target": target,
            "sensitive": sensitive
        }

        return render_template(
            "result.html",
            result=result_dict,
            bias=bias_message,
            bias_class=bias_class,
            bias_gap=bias_gap,
            disparate_impact=disparate_impact,
            sensitive=sensitive,
            explanation=explanation
        )

    except Exception as e:
        print("ANALYZE ERROR:", e)
        traceback.print_exc()
        return render_template('index.html', error=str(e))


# ---------------- MITIGATE ----------------
@app.route('/mitigate')
def mitigate():
    try:
        if not latest_result or 'filepath' not in latest_result:
            return jsonify({"error": "Please run an analysis first."}), 400

        filepath = latest_result['filepath']
        target = latest_result['target']
        sensitive = latest_result['sensitive']

        df = pd.read_csv(filepath)
        df[target] = pd.to_numeric(df[target], errors='coerce')
        df = df.dropna(subset=[target, sensitive])

        # --- Reweighing Algorithm ---
        total = len(df)
        weights = []
        for _, row in df.iterrows():
            s_val = row[sensitive]
            t_val = row[target]

            # P(sensitive group) and P(target outcome)
            p_s = (df[sensitive] == s_val).sum() / total
            p_t = (df[target] == t_val).sum() / total
            p_st = ((df[sensitive] == s_val) & (df[target] == t_val)).sum() / total

            # Expected vs observed probability
            expected = p_s * p_t
            observed = p_st if p_st > 0 else 1e-6

            weights.append(round(expected / observed, 4))

        df['FairLens_Weight'] = weights

        # --- Apply weights via resampling so the exported CSV is actually debiased ---
        # Normalize weights to use as sampling probabilities
        import numpy as np
        weight_arr = np.array(weights, dtype=float)
        weight_arr = weight_arr / weight_arr.sum()   # normalize to sum=1

        # Resample to the same size using the weights (with replacement)
        resampled_df = df.sample(n=len(df), replace=True, weights=weight_arr, random_state=42)
        resampled_df = resampled_df.drop(columns=['FairLens_Weight'])  # clean up helper column
        resampled_df = resampled_df.reset_index(drop=True)

        output_path = os.path.join('uploads', 'dataset_debiased.csv')
        resampled_df.to_csv(output_path, index=False)

        return send_file(
            output_path,
            as_attachment=True,
            download_name='FairLens_Debiased_Dataset.csv',
            mimetype='text/csv'
        )

    except Exception as e:
        print("MITIGATE ERROR:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ---------------- CHATBOT ----------------
@app.route('/chat', methods=['POST'])
def chat():
    try:
        if not latest_result:
            return jsonify({"reply": "Please run an analysis first."})

        data = request.get_json(silent=True) or {}
        user_question = (data.get("question") or "").strip()

        if not user_question:
            return jsonify({"reply": "Please enter a question first."})

        prompt = f"""
        You are FairLens AI assistant.

        Current Analysis:
        {latest_result}

        User Question:
        {user_question}

        Answer clearly in simple language.
        """

        try:
            reply_text = generate_gemini_text(prompt)
        except Exception as api_e:
            print("Gemini API Error (using local reply):", api_e)
            reply_text = local_chat_reply(user_question, latest_result)

        return jsonify({"reply": reply_text})

    except Exception as e:
        print("CHAT ERROR:", e)
        traceback.print_exc()
        return jsonify({"reply": str(e)})


# ---------------- RUN ----------------
if __name__ == '__main__':
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)