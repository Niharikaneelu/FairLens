# 🚀 FairLens  
### AI-Powered Bias Detection for Fair Decision Making  

---

## 🧠 Problem  
Organizations often rely on historical data to make decisions such as hiring, loan approvals, and admissions.  
However, this data can contain **hidden biases**, leading to unfair outcomes for certain groups.

Most existing bias detection tools are **complex and require technical expertise**, making them inaccessible to NGOs and small organizations.

---

## 💡 Solution  
**FairLens** is a **no-code bias auditing tool** that helps non-technical users:

- 📂 Upload datasets (CSV)  
- 📊 Detect bias across demographic groups using statistical fairness metrics  
- 🧠 Understand results through simple AI-generated explanations  
- 🛠️ Get actionable suggestions to improve fairness  

---

## ⚙️ How It Works  

1. Upload dataset  
2. Select:
   - Target column (e.g., Selected / Approved)  
   - Sensitive attribute (e.g., Gender, Age)  
3. System computes fairness metrics  
4. View:
   - Bias detection results  
   - AI-generated explanation  
   - Suggested fixes  

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd FairLens
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **Mac/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

5. **Set up your Gemini API key** (optional but recommended for full AI features):
   - Create a `.env` file in the project root directory
   - Add your Google Gemini API key:
     ```
     GEMINI_API_KEY=your-api-key-here
     ```
   - Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

   **Note:** If you don't have an API key or quota is exhausted, the app will automatically use built-in explanations and chatbot responses—no setup required.

### Running the Application

6. **Start the Flask server:**
   ```bash
   python app.py
   ```

7. **Open your browser and navigate to:**
   ```
   http://localhost:5000
   ```

8. **Use the application:**
   - Upload a CSV file with your dataset
   - Select your target column (e.g., `hired`, `approved`)
   - Select your sensitive attribute (e.g., `gender`, `age`)
   - View the bias analysis results
   - Ask follow-up questions in the chatbot
   - Download a debiased version of your dataset

---

## 🧪 Core Methodology  

FairLens detects bias using **statistical fairness metrics**, including:

- 📊 **Selection Rate** – Measures how often each group receives positive outcomes  
- ⚖️ **Demographic Parity Difference** – Compares outcome differences between groups  
- 📉 **Disparate Impact Ratio** – Identifies potential discrimination using standard thresholds  

These methods provide a **simple and interpretable way** to identify potential bias in raw datasets.

---

## ✨ Key Features  

- ⚡ **Instant Bias Detection**  
  Quickly identifies disparities in outcomes across groups  

- 🧠 **AI-Powered Explanations**  
  Uses Google Gemini to explain results in plain language, with intelligent fallback to built-in explanations when API is unavailable  

- 💬 **Interactive Chatbot**  
  Ask follow-up questions about bias metrics and get contextual answers powered by AI or local fallback logic  

- 🛠️ **Actionable Fixes**  
  Suggests improvements such as data balancing and reweighting; download debiased datasets directly  

- 📊 **Simple Dashboard**  
  Clean and accessible interface for non-technical users  

- 🔄 **Resilient Offline Mode**  
  Built-in fallback explanations and chatbot responses work even without Gemini API availability  

---

## 🧰 Tech Stack  

- **Frontend:** HTML / CSS / JavaScript  
- **Backend:** Python (Flask)  
- **Data Processing:** pandas  
- **AI Integration:** Google Gemini API  

---

## 🎯 Use Case Example  

A small NGO uploads hiring data and discovers:  
👉 “Female candidates are selected 30% less than male candidates.”  

FairLens highlights this disparity, explains the possible cause, and suggests ways to improve fairness.

---

## 🌍 Impact  

- Promotes **ethical and fair decision-making**  
- Improves **transparency and accountability**  
- Helps reduce **unintentional discrimination**  

---

## 🛠️ Troubleshooting

### Gemini API Not Working (Getting 429 or "quota exceeded" errors)?
This is expected behavior and **not a bug**. The app automatically falls back to built-in explanations and chatbot responses. To use AI-powered responses:

1. Check your Google Gemini API quota at [Google Cloud Console](https://console.cloud.google.com/)
2. Ensure billing is enabled for your project
3. If quota is exhausted, wait for it to reset or upgrade your plan
4. Update `GEMINI_API_KEY` in your `.env` file if you're using a different API key

### Virtual Environment Not Activating?
- Ensure you're in the project directory before activating
- Try using the full path to the activation script if relative paths don't work

### Port 5000 Already in Use?
- Modify the last line of `app.py` to use a different port:
  ```python
  app.run(debug=True, port=8080)
  ```

---

## 📊 Sample Data

Sample datasets are included in the `Datasets/` folder for testing:
- `loan_approval_demo.csv` – Loan approval data with demographic info
- `college_admissions_demo.csv` – College admissions data
- `hr_hiring_demo.csv` – HR hiring data

---

## 🚀 Future Scope  

- 📈 Bias detection in machine learning model predictions  
- 🌐 Multi-language support  
- 📊 Advanced fairness metrics and visualizations  
- 🔄 Real-time monitoring of decision systems  

---

## 👥 Team  

- Niharika C  
- Elna Susan Kuriakose
- Rithika Sankar
- Harinarayan S

---

## 📌 Status  

🚧 Built as part of a hackathon project  
