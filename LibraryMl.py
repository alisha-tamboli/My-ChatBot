from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

def vectorize_data(training_data):
    sentences = [item[0] for item in training_data]

    vectorizer = CountVectorizer()
    vectors = vectorizer.fit_transform(sentences)

    return vectorizer, vectors


def train_chatbot(training_data):
    vectorizer, vectors = vectorize_data(training_data)
    labels = [item[1] for item in training_data]
    
    # Train the Naive Bayes classifier
    classifier = MultinomialNB()
    classifier.fit(vectors, labels)
    
    return vectorizer, classifier

def predict_category(user_input, vectorizer, classifier):
    # Transform the user's input using the same vectorizer
    input_vector = vectorizer.transform([user_input])
    
    # Predict the category
    prediction = classifier.predict(input_vector)
    return prediction[0]

def chatbot_response_ml(user_input, vectorizer, classifier):
    category = predict_category(user_input, vectorizer, classifier)
    
    if category == "greeting":
        return "Hello! How can I help you?"
    elif category == "question":
        return "I am a chatbot here to assist you!"
    elif category == "farewell":
        return "Goodbye! Have a great day!"
    else:
        return "I'm sorry, I don't understand that."
    

training_data = [
    ("hello", "greeting"),
    ("hi", "greeting"),
    ("how are you?", "question"),
    ("what is your name?", "question"),
    ("bye", "farewell"),
    ("see you later", "farewell")
]

vectorizer, classifier = train_chatbot(training_data)