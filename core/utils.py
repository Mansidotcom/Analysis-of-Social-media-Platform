import joblib
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

model = joblib.load(os.path.join(BASE_DIR, 'ml/spam_model.pkl'))
vectorizer = joblib.load(os.path.join(BASE_DIR, 'ml/vectorizer.pkl'))

def is_spam(text):
    # Simple keywords jo aksar spam mein hote hain
    spam_keywords = ['congratulations', 'won', 'click here', 'claim', 'prize', 'free', '₹']

    # Text ko lower case mein kar lo taaki case sensitive na ho
    text_lower = text.lower()

    # Agar spam keywords milte hain to turant spam maan lo
    for kw in spam_keywords:
        if kw in text_lower:
            return True

    # Nahi toh machine learning model se check karo
    text_vec = vectorizer.transform([text])
    prediction = model.predict(text_vec)
    return prediction[0] == 'spam'
