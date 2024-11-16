import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
from utils import get_past_predictions
import pandas as pd

# Function to show the past predictions page
def show_past_predictions():
    if 'user_id' not in st.session_state or st.session_state.user_id is None:
        st.error("Please log in to continue.")
        return

    st.subheader("Past Predictions")

    # Get past predictions from the database
    past_predictions_df = get_past_predictions(st.session_state.user_id)

    # If there are past predictions, display them
    if not past_predictions_df.empty:
        # Display the predictions in a table format
        st.write("### Past Predictions Overview")
        st.dataframe(past_predictions_df)
        
        # Layout: Columns for various charts
        col1, col2 = st.columns(2)

        # Matplotlib Bar Chart (Disease Count)
        with col1:
            st.write("### Disease Count Distribution (Bar Chart)")
            fig, ax = plt.subplots()
            ax.bar(past_predictions_df['disease_name'], past_predictions_df['count'], color='lightblue')
            ax.set_xlabel('Disease')
            ax.set_ylabel('Count')
            ax.set_title('Past Predictions (Bar Chart)')
            ax.set_xticklabels(past_predictions_df['disease_name'], rotation=45, ha='right')
            st.pyplot(fig)

        # Plotly Pie Chart (Disease Distribution)
        with col2:
            st.write("### Disease Distribution (Pie Chart)")
            fig_pie = px.pie(past_predictions_df, names='disease_name', values='count', title='Disease Distribution')
            st.plotly_chart(fig_pie)

        # Insights: Show the top 3 most common diseases
        st.subheader("Top 3 Most Common Diseases")
        top_diseases = past_predictions_df.nlargest(3, 'count')
        st.write(top_diseases)

        # Additional Visualization: Top Diseases Bar Chart
        st.subheader("Top 3 Most Common Diseases (Bar Chart)")
        fig_top_diseases, ax_top = plt.subplots()
        ax_top.bar(top_diseases['disease_name'], top_diseases['count'], color='lightgreen')
        ax_top.set_xlabel('Disease')
        ax_top.set_ylabel('Count')
        ax_top.set_title('Top 3 Most Common Diseases')
        ax_top.set_xticklabels(top_diseases['disease_name'], rotation=45, ha='right')
        st.pyplot(fig_top_diseases)

    else:
        st.write("No past predictions found. Try uploading an image to get predictions.")
