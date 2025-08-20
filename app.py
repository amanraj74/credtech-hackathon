# app.py
import streamlit as st
import requests
from textblob import TextBlob
import os

# --- API Key Configuration ---
# It's best practice to use Streamlit's secrets management for API keys
# For now, we'll place them here. Replace "YOUR_KEY" with your actual keys.
# To make it more secure, you can set them as environment variables.
ALPHA_VANTAGE_KEY = "YOUR_ALPHA_VANTAGE_KEY"
NEWS_API_KEY = "YOUR_NEWS_API_KEY"

# --- Real Data Fetching and Processing Functions ---

def fetch_financial_data(ticker):
    """Fetches key financial ratios from Alpha Vantage."""
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={ALPHA_VANTAGE_KEY}'
    try:
        r = requests.get(url)
        r.raise_for_status()  # Raises an exception for bad status codes
        data = r.json()
        if "DebtToEquity" in data and data["DebtToEquity"] is not None:
            return {'debt_to_equity': float(data['DebtToEquity'])}
        else:
            return {'debt_to_equity': 1.0} # Return a neutral default value
    except (requests.exceptions.RequestException, KeyError, ValueError) as e:
        st.error(f"Error fetching financial data: {e}")
        return None

def fetch_news_sentiment(ticker):
    """Fetches news headlines from NewsAPI and calculates average sentiment."""
    url = f'https://newsapi.org/v2/everything?q={ticker}&sortBy=publishedAt&apiKey={NEWS_API_KEY}&language=en&pageSize=20'
    try:
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        articles = data.get('articles', [])
        if not articles:
            return {'news_sentiment_score': 0.0}
        
        sentiment_sum = 0
        for article in articles:
            # TextBlob provides sentiment polarity between -1 (negative) and 1 (positive)
            sentiment_sum += TextBlob(article['title']).sentiment.polarity
        
        return {'news_sentiment_score': sentiment_sum / len(articles)}
    except (requests.exceptions.RequestException, KeyError, ValueError) as e:
        st.error(f"Error fetching news data: {e}")
        return None

def predict_credit_score(financial_data, news_data):
    """
    Calculates a credit score based on real data and provides an explanation.
    This is a rule-based model, which is highly explainable. [cite: 37]
    """
    score = 50  # Start with a neutral score
    explanation = ["Base Score: 50"]

    # --- Rule 1: Analyze Debt-to-Equity Ratio ---
    dte_ratio = financial_data['debt_to_equity']
    if dte_ratio < 0.5:
        score += 20
        explanation.append(f"✔️ Very Low Debt-to-Equity ({dte_ratio:.2f}) is a strong positive signal. (+20 pts)")
    elif dte_ratio < 1.0:
        score += 10
        explanation.append(f"✔️ Healthy Debt-to-Equity ({dte_ratio:.2f}) is a good sign. (+10 pts)")
    else:
        score -= 20
        explanation.append(f"❌ High Debt-to-Equity ({dte_ratio:.2f}) increases risk. (-20 pts)")

    # --- Rule 2: Analyze News Sentiment ---
    sentiment = news_data['news_sentiment_score']
    if sentiment > 0.2:
        score += 20
        explanation.append(f"✔️ Strong Positive News Sentiment ({sentiment:.2f}) suggests a good outlook. (+20 pts)")
    elif sentiment < -0.2:
        score -= 20
        explanation.append(f"❌ Strong Negative News Sentiment ({sentiment:.2f}) suggests potential issues. (-20 pts)")
    else:
        explanation.append(f"➖ Neutral News Sentiment ({sentiment:.2f}) has no major impact. (+0 pts)")

    final_score = max(0, min(100, score))
    return final_score, explanation

# --- Streamlit App UI ---
st.set_page_config(layout="wide")
st.title("CredTech: Real-Time Explainable Credit Intelligence 💡")

st.header("Enter Company Details")
ticker_input = st.text_input("Enter a US company stock ticker (e.g., AAPL, MSFT, NVDA)", "NVDA")

if st.button("Analyze Creditworthiness"):
    if not ticker_input:
        st.warning("Please enter a stock ticker.")
    else:
        # 1. Fetch data
        with st.spinner(f'Fetching real-time data for {ticker_input}...'):
            financial_data = fetch_financial_data(ticker_input)
            news_data = fetch_news_sentiment(ticker_input)

        # 2. Predict score if data was fetched successfully
        if financial_data and news_data:
            with st.spinner('Running AI model for prediction...'):
                score, explanation = predict_credit_score(financial_data, news_data)

            st.success("Analysis Complete!")
            
            # 3. Display the results
            st.metric(label=f"Credit Score for {ticker_input}", value=score)
            
            st.subheader("How was this score calculated?")
            for step in explanation:
                st.info(step)