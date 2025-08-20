# app.py
# Final Professional Version for the CredTech Hackathon Project

# --- Step 1: Import necessary libraries ---
import streamlit as st
import requests
from textblob import TextBlob
import pandas as pd
import numpy as np
import altair as alt
import os

# --- Step 2: API Key Configuration ---
# Your API keys are correctly placed here.
ALPHA_VANTAGE_KEY = "MTRM49G88OINC1WZ"
NEWS_API_KEY = "60cf318aea8e45c2bda0e5e5f0d81392"


# --- Step 3: Data Fetching and Processing Functions (with Caching) ---

@st.cache_data(ttl=600) # PROFESSIONAL UPGRADE: Cache data for 10 minutes
def fetch_financial_data(ticker):
    """
    Fetches key financial overview data for a given stock ticker from Alpha Vantage.
    """
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={ALPHA_VANTAGE_KEY}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if "DebtToEquity" in data and data["DebtToEquity"] is not None:
            return {'debt_to_equity': float(data['DebtToEquity'])}
        else:
            st.warning(f"Debt-to-Equity ratio not available for {ticker}. Using a neutral value.")
            return {'debt_to_equity': 1.0}
    except (requests.exceptions.RequestException, KeyError, ValueError) as e:
        st.error(f"Error fetching financial data: {e}")
        return None

@st.cache_data(ttl=600) # PROFESSIONAL UPGRADE: Cache data for 10 minutes
def fetch_news_sentiment(ticker):
    """
    Fetches recent news, calculates average sentiment, and finds the most impactful headline.
    """
    url = f'https://newsapi.org/v2/everything?q={ticker}&sortBy=publishedAt&apiKey={NEWS_API_KEY}&language=en&pageSize=20'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        articles = data.get('articles', [])
        
        if not articles:
            st.warning(f"No recent news articles found for {ticker}.")
            return {'news_sentiment_score': 0.0, 'top_headline': "N/A"}
        
        sentiment_sum = 0
        top_article = None
        max_sentiment = -1

        for article in articles:
            sentiment = TextBlob(article['title']).sentiment.polarity
            sentiment_sum += sentiment
            # Find the article with the highest absolute sentiment
            if abs(sentiment) > max_sentiment:
                max_sentiment = abs(sentiment)
                top_article = article['title']
        
        average_sentiment = sentiment_sum / len(articles)
        # PROFESSIONAL UPGRADE: Return the top headline as well
        return {'news_sentiment_score': average_sentiment, 'top_headline': top_article}
        
    except (requests.exceptions.RequestException, KeyError, ValueError) as e:
        st.error(f"Error fetching news data: {e}")
        return None

# --- Step 4: The Scoring and Explainability Engine ---
# This part remains the same as your logic is sound.
def predict_credit_score(financial_data, news_data):
    score = 50
    explanation = ["Base Score: 50"]
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
    sentiment = news_data['news_sentiment_score']
    if sentiment > 0.2:
        score += 20
        explanation.append(f"✔️ Strong Positive News Sentiment ({sentiment:.2f}) suggests a good public outlook. (+20 pts)")
    elif sentiment < -0.2:
        score -= 20
        explanation.append(f"❌ Strong Negative News Sentiment ({sentiment:.2f}) suggests potential issues. (-20 pts)")
    else:
        explanation.append(f"➖ Neutral News Sentiment ({sentiment:.2f}) has no major impact. (+0 pts)")
    final_score = max(0, min(100, score))
    return final_score, explanation


# --- Step 5: Build the Professional Streamlit User Interface ---

st.set_page_config(layout="wide", page_title="CredTech Intelligence Platform")
st.title("CredTech: Real-Time Explainable Credit Intelligence 💡")
st.header("Enter Company Details")
ticker_input = st.text_input("Enter a US company stock ticker (e.g., AAPL, MSFT, NVDA)", "NVDA")

if st.button("Analyze Creditworthiness"):
    if not ticker_input:
        st.warning("Please enter a stock ticker to analyze.")
    else:
        with st.spinner(f'Fetching and analyzing data for {ticker_input}...'):
            financial_data = fetch_financial_data(ticker_input)
            news_data = fetch_news_sentiment(ticker_input)

        if financial_data and news_data:
            score, explanation = predict_credit_score(financial_data, news_data)
            st.success("Analysis Complete!")
            
            # PROFESSIONAL UPGRADE: Organize results into tabs
            tab1, tab2 = st.tabs(["📊 Score Summary", "🔍 Raw Data Sources"])

            with tab1:
                st.metric(label=f"Credit Score for {ticker_input}", value=score)
                st.subheader("How this score was calculated:")
                
                # PROFESSIONAL UPGRADE: Use columns for a cleaner explanation layout
                col1, col2 = st.columns(2)
                with col1:
                    st.info(explanation[0]) # Base Score
                    for item in explanation[1:]:
                        if "✔️" in item:
                            st.success(item) # Green for positive factors
                with col2:
                     for item in explanation[1:]:
                        if "❌" in item or "➖" in item:
                            st.warning(item) # Yellow for negative/neutral factors

                st.subheader("Key Unstructured Event Driver:")
                st.markdown(f"> _{news_data['top_headline']}_")

                st.subheader("Historical Score Trend (Illustrative)")
                hist_data = pd.DataFrame({
                    'Date': pd.to_datetime(['2025-08-18', '2025-08-19', '2025-08-20']),
                    'Score': [np.clip(score - 10, 0, 100), np.clip(score + 5, 0, 100), score]
                })
                chart = alt.Chart(hist_data).mark_line(point=True, strokeWidth=3).encode(
                    x='Date',
                    y=alt.Y('Score', scale=alt.Scale(domain=[0, 100])),
                    tooltip=['Date', 'Score']
                ).properties(title='Score over the last 3 days').interactive()
                st.altair_chart(chart, use_container_width=True)

            with tab2:
                st.subheader("Financial Data Fetched")
                st.json(financial_data)
                st.subheader("News Sentiment Analysis")
                st.json(news_data)
