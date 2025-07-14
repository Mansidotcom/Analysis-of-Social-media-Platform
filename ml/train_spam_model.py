import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
import joblib

# CSV file ka path
csv_file = 'ml/social_media_spam.csv'

# Data load karo
data = pd.read_csv(csv_file)

# Assume CSV mein do columns hain: 'text' (message) aur 'label' (spam ya ham)
print(data.head())

# Features aur labels define karo
X = data['text']
y = data['label']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Text ko number mein convert karne ke liye TF-IDF vectorizer
vectorizer = TfidfVectorizer(stop_words='english')
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Model train karo (Logistic Regression)
model = LogisticRegression()
model.fit(X_train_vec, y_train)

# Test set pe prediction
y_pred = model.predict(X_test_vec)

# Accuracy aur report print karo
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# Vectorizer aur model save karo taaki future mein prediction kar sakein
joblib.dump(vectorizer, 'ml/vectorizer.pkl')
joblib.dump(model, 'ml/spam_model.pkl')

print("Model aur vectorizer save ho gaye hain.")
