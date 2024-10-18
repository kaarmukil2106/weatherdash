import streamlit as st
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt

# Title
st.title("Sentiment Analysis")

# User input text
text = st.text_area("Enter the text for sentiment analysis:", height=150)

# Sentiment Analysis using TextBlob
if text:
    blob = TextBlob(text)
    sentiment_textblob = blob.sentiment.polarity
    sentiment_label_textblob = "Positive" if sentiment_textblob > 0 else "Negative" if sentiment_textblob < 0 else "Neutral"
    
    # Sentiment using VADER
    analyzer = SentimentIntensityAnalyzer()
    sentiment_vader = analyzer.polarity_scores(text)
    sentiment_label_vader = "Positive" if sentiment_vader['compound'] > 0 else "Negative" if sentiment_vader['compound'] < 0 else "Neutral"

    st.write("### TextBlob Sentiment:")
    st.write(f"Sentiment Polarity: {sentiment_textblob:.2f} ({sentiment_label_textblob})")
    
    st.write("### VADER Sentiment:")
    st.write(f"Compound Score: {sentiment_vader['compound']:.2f} ({sentiment_label_vader})")

    # Visualization
    labels = ['Positive', 'Negative', 'Neutral']
    values = [sentiment_vader['pos'], sentiment_vader['neg'], sentiment_vader['neu']]
    
    fig, ax = plt.subplots()
    ax.bar(labels, values)
    st.pyplot(fig)