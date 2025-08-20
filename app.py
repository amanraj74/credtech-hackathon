# app.py
import streamlit as st
import pandas as pd
import random # To generate fake data

# --- Placeholder Functions (You will replace these with your real code) ---

def fetch_data(ticker):
    """
    A placeholder function to simulate fetching data.
    In your real app, this will call APIs (NewsAPI, Alpha Vantage, etc.).
    """
    # Simulate fetching financial and news data
    print(f"Fetching data for {ticker}...")
    dummy_data = {
        'debt_to_equity': round(random.uniform(0.2, 1.5), 2),
        'news_sentiment_score': round(random.uniform(-0.8, 0.8), 2)
    }
    return dummy_data

def predict_credit_score(data):
    """
    A placeholder function to simulate model prediction.
    In your real app, this will load your trained model and predict.
    """
    print("Running prediction model...")
    # Simple rule-based logic for our dummy model
    score = 50 # Start with a neutral score
    explanation = ["Base Score: 50"]

    # Adjust score based on debt-to-equity
    if data['debt_to_equity'] < 0.5:
        score += 25
        explanation.append("✔️ Low Debt-to-Equity Ratio (+25 pts)")
    else:
        score -= 15
        explanation.append("❌ High Debt-to-Equity Ratio (-15 pts)")
    
    # Adjust score based on news sentiment
    if data['news_sentiment_score'] > 0.3:
        score += 25
        explanation.append("✔️ Positive News Sentiment (+25 pts)")
    elif data['news_sentiment_score'] < -0.3:
        score -= 25
        explanation.append("❌ Negative News Sentiment (-25 pts)")
    else:
        explanation.append("➖ Neutral News Sentiment (+0 pts)")

    # Ensure score is within 0-100
    final_score = max(0, min(100, score))
    
    return final_score, explanation


# --- Streamlit App UI ---

st.title("CredTech: Explainable Credit Intelligence 💡")

st.header("Enter Company Details")
ticker_input = st.text_input("Enter company stock ticker (e.g., AAPL, GOOGL)", "AAPL")

analyze_button = st.button("Analyze Creditworthiness")

if analyze_button:
    # 1. Fetch data using our placeholder function
    with st.spinner(f'Fetching real-time data for {ticker_input}...'):
        data = fetch_data(ticker_input)
    
    # 2. Predict score using our placeholder function
    with st.spinner('Running AI model for prediction...'):
        score, explanation = predict_credit_score(data)

    st.success("Analysis Complete!")
    
    # 3. Display the results
    st.header(f"Credit Score for {ticker_input}:")
    
    # Use st.metric to display the score in a nice big box
    st.metric(label="Score (0-100)", value=score)
    
    st.subheader("How was this score calculated?")
    # Display the step-by-step explanation
    for step in explanation:
        st.info(step)