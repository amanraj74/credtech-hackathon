# app.py
# Main file for the CredTech Hackathon Project

# --- Step 1: Import necessary libraries ---
# Streamlit is for building the web app UI.
# Requests is for making API calls to get data from the internet.
# TextBlob is for simple sentiment analysis on news headlines.
# Pandas and NumPy are for data manipulation.
# Altair is for creating beautiful, interactive charts.
# OS is used here for potentially accessing environment variables (a secure way to handle API keys).
import streamlit as st
import requests
from textblob import TextBlob
import pandas as pd
import numpy as np
import altair as alt
import os

# --- Step 2: API Key Configuration ---
# IMPORTANT: Replace "YOUR_KEY" with the actual API keys you received.
# For a real-world application, it's safer to store these as secrets.
# You can learn about Streamlit's secrets management for a more secure way.
ALPHA_VANTAGE_KEY = "YOUR_ALPHA_VANTAGE_KEY"
NEWS_API_KEY = "YOUR_NEWS_API_KEY"


# --- Step 3: Data Fetching and Processing Functions ---

def fetch_financial_data(ticker):
    """
    Fetches key financial overview data for a given stock ticker from Alpha Vantage.
    Specifically, we are looking for the Debt-to-Equity ratio.
    """
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={ALPHA_VANTAGE_KEY}'
    try:
        response = requests.get(url)
        response.raise_for_status()  # This will raise an error for bad responses (like 404 or 500)
        data = response.json()
        
        # Check if the required data point exists and is not None
        if "DebtToEquity" in data and data["DebtToEquity"] is not None:
            return {'debt_to_equity': float(data['DebtToEquity'])}
        else:
            # If the data is missing, return a neutral default value to avoid errors
            st.warning(f"Debt-to-Equity ratio not available for {ticker}. Using a neutral value.")
            return {'debt_to_equity': 1.0}
            
    except (requests.exceptions.RequestException, KeyError, ValueError) as e:
        # Handle potential errors during the API call or data processing
        st.error(f"Error fetching financial data: {e}")
        return None

def fetch_news_sentiment(ticker):
    """
    Fetches recent news headlines for a ticker from NewsAPI and calculates the average sentiment score.
    Sentiment is calculated using TextBlob.
    """
    url = f'https://newsapi.org/v2/everything?q={ticker}&sortBy=publishedAt&apiKey={NEWS_API_KEY}&language=en&pageSize=20'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        articles = data.get('articles', [])
        
        if not articles:
            st.warning(f"No recent news articles found for {ticker}.")
            return {'news_sentiment_score': 0.0}
        
        # Calculate sentiment for each article title and find the average
        sentiment_sum = 0
        for article in articles:
            # TextBlob's sentiment.polarity gives a score from -1 (very negative) to +1 (very positive)
            sentiment_sum += TextBlob(article['title']).sentiment.polarity
        
        average_sentiment = sentiment_sum / len(articles)
        return {'news_sentiment_score': average_sentiment}
        
    except (requests.exceptions.RequestException, KeyError, ValueError) as e:
        st.error(f"Error fetching news data: {e}")
        return None

# --- Step 4: The Scoring and Explainability Engine ---

def predict_credit_score(financial_data, news_data):
    """
    Calculates a credit score based on the fetched data using a simple, rule-based model.
    The key feature is that it also generates a step-by-step explanation for its decision.
    """
    score = 50  # Start with a neutral base score
    explanation = ["Base Score: 50"]

    # Rule 1: Analyze the Debt-to-Equity Ratio from financial data
    dte_ratio = financial_data['debt_to_equity']
    if dte_ratio < 0.5:
        score += 20
        explanation.append(f"✔️ Very Low Debt-to-Equity ({dte_ratio:.2f}) is a strong positive signal. (+20 pts)")
    elif dte_ratio < 1.0:
        score += 10
        explanation.append(f"✔️ Healthy Debt-to-Equity ({dte_ratio:.2f}) is a good sign. (+10 pts)")
    else:
        score -= 20
        explanation.append(f"❌ High Debt-to-Equity ({dte_ratio:.2f}) increases financial risk. (-20 pts)")

    # Rule 2: Analyze the average sentiment from news headlines
    sentiment = news_data['news_sentiment_score']
    if sentiment > 0.2:
        score += 20
        explanation.append(f"✔️ Strong Positive News Sentiment ({sentiment:.2f}) suggests a good public outlook. (+20 pts)")
    elif sentiment < -0.2:
        score -= 20
        explanation.append(f"❌ Strong Negative News Sentiment ({sentiment:.2f}) suggests potential issues. (-20 pts)")
    else:
        explanation.append(f"➖ Neutral News Sentiment ({sentiment:.2f}) has no major impact. (+0 pts)")

    # Final score is capped between 0 and 100
    final_score = max(0, min(100, score))
    
    return final_score, explanation


# --- Step 5: Build the Streamlit User Interface ---

# Set the page configuration for a wider layout and a title
st.set_page_config(layout="wide", page_title="CredTech Intelligence Platform")

# Main title of the application
st.title("CredTech: Real-Time Explainable Credit Intelligence 💡")

# Header for the user input section
st.header("Enter Company Details")

# Text input box for the user to enter a company's stock ticker
ticker_input = st.text_input("Enter a US company stock ticker (e.g., AAPL, MSFT, NVDA)", "NVDA")

# The main button that triggers the entire analysis process
if st.button("Analyze Creditworthiness"):
    if not ticker_input:
        st.warning("Please enter a stock ticker to analyze.")
    else:
        # Show spinners while the backend processes are running
        with st.spinner(f'Fetching real-time financial and news data for {ticker_input}...'):
            financial_data = fetch_financial_data(ticker_input)
            news_data = fetch_news_sentiment(ticker_input)

        # Only proceed if both data fetching steps were successful
        if financial_data and news_data:
            with st.spinner('Running AI model for prediction...'):
                score, explanation = predict_credit_score(financial_data, news_data)

            st.success("Analysis Complete!")
            
            # Display the final score using a prominent metric display
            st.metric(label=f"Credit Score for {ticker_input}", value=score)
            
            # Display the detailed explanation of how the score was calculated
            st.subheader("How was this score calculated?")
            for step in explanation:
                st.info(step) # Using st.info gives it a nice blue box style

            # Display the illustrative historical chart
            st.subheader("Historical Score Trend (Illustrative)")
            # Create some fake historical data points for the purpose of the chart
            hist_data = pd.DataFrame({
                'Date': pd.to_datetime(['2025-08-18', '2025-08-19', '2025-08-20']),
                'Score': [np.clip(score - 10, 0, 100), np.clip(score + 5, 0, 100), score]
            })
            
            chart = alt.Chart(hist_data).mark_line(point=True, strokeWidth=3).encode(
                x='Date',
                y=alt.Y('Score', scale=alt.Scale(domain=[0, 100])),
                tooltip=['Date', 'Score']
            ).properties(
                title='Score over the last 3 days'
            ).interactive()
            
            st.altair_chart(chart, use_container_width=True)