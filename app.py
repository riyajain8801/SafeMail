from flask import Flask, render_template, request
import joblib

app = Flask(__name__)

# Load model & vectorizer
model = joblib.load("phishing_model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None
    confidence = None

    if request.method == "POST":
        subject = request.form["subject"]
        body = request.form["body"]

        # 🛑 Empty input check
        if not subject.strip() or not body.strip():
            prediction = "⚠️ Please enter both subject and email content"
            confidence = 0.0
            return render_template(
                "index.html",
                prediction=prediction,
                confidence=confidence
            )

        email_text = subject + " " + body

        # 🛑 Very short input check
        if len(email_text.split()) < 5:
            prediction = "✅ Email looks safe (Not enough content to analyze)"
            confidence = 0.0
            return render_template(
                "index.html",
                prediction=prediction,
                confidence=confidence
            )

        email_vectorized = vectorizer.transform([email_text])

        result = model.predict(email_vectorized)[0]
        prob = model.predict_proba(email_vectorized)[0]
        confidence = round(max(prob) * 100, 2)

        if confidence < 50:
            prediction = "✅ Safe Email (Low Confidence)"
        elif result == 1:
            prediction = "🚨 Phishing Email"
        else:
            prediction = "✅ Safe Email"

    return render_template(
        "index.html",
        prediction=prediction,
        confidence=confidence
    )

if __name__ == "__main__":
    app.run(debug=True)
