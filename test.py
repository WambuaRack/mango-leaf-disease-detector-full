import streamlit as st
from pages import login, upload_image, view_predictions
import pandas as pd
import mysql.connector
from io import StringIO



# Title of the web app with an emoji for appeal
st.title("Mango Leaf Disease Detection System 🍃🌿")

# Sidebar with page navigation and icons
page = st.sidebar.radio(
    "Select a Page", 
    ["Login/Signup 🔑", "Upload Image 📷", "View Past Predictions 📊", "Generate Report 📑"]
)

# Function to fetch data from the database based on date range
def fetch_data_from_db(start_date, end_date):
    try:
        # Example: connect to the MySQL database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="mango"
        )
        
        # SQL query to fetch the data between the provided date range
        query = """
        SELECT created_at, disease_name, probability, treatment 
        FROM predictions
        WHERE created_at BETWEEN %s AND %s
        """
        
        # Print query and parameters for debugging
        st.write(f"Executing query: {query} with parameters {start_date} and {end_date}")
        
        cursor = conn.cursor()
        cursor.execute(query, (start_date, end_date))
        rows = cursor.fetchall()

        # Convert the results into a pandas DataFrame
        if rows:
            df = pd.DataFrame(rows, columns=["Date", "Disease", "Probability", "Treatment"])
        else:
            st.warning(f"No records found for {start_date} to {end_date}.")
            df = pd.DataFrame()
        
        conn.close()
        return df
    except mysql.connector.Error as err:
        st.error(f"Error fetching data from database: {err}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

# Function to allow downloading the report
def download_report(df):
    # Convert the DataFrame to CSV
    csv = df.to_csv(index=False)
    buffer = StringIO(csv)
    
    # Add a button to download the report
    st.download_button(
        label="Download Report as CSV",
        data=buffer,
        file_name="mango_leaf_disease_report.csv",
        mime="text/csv"
    )

# Display different content based on the selected page
if page == "Login/Signup 🔑":
    st.header("Login or Sign Up to Continue")
    login.show_login_signup()
elif page == "Upload Image 📷":
    st.header("Upload Mango Leaf Image for Disease Prediction")
    try:
        upload_image.show_upload_image()
    except Exception as e:
        st.error(f"An error occurred while uploading the image: {e}")
elif page == "View Past Predictions 📊":
    st.header("Past Predictions History")
    view_predictions.show_past_predictions()
elif page == "Generate Report 📑":
    st.header("Generate Mango Leaf Disease Report")
    
    # Date range selection for report (starting from 2024-11-16)
    start_date = st.date_input("Select Start Date", pd.to_datetime('2024-11-16'))
    end_date = st.date_input("Select End Date", pd.to_datetime('2024-11-16'))

    # Ensure start date is not later than end date
    if start_date > end_date:
        st.error("Start date cannot be later than end date.")
    else:
        # Button to generate the report
        if st.button("Generate Report"):
            # Fetch data from the database
            filtered_data = fetch_data_from_db(start_date, end_date)

            # Check if there's any data to show
            if not filtered_data.empty:
                st.write(f"Report from {start_date} to {end_date}")
                st.dataframe(filtered_data)  # Display the report

                # Provide the option to download the report as a CSV
                download_report(filtered_data)
            else:
                st.error("No data available for the selected date range.")
            
# Adding additional visual elements like icons and styling
st.sidebar.markdown(
    """
    ## Mango Leaf Disease Detection
    🥭 The system helps to detect diseases in mango leaves by uploading an image and providing predictions based on the condition of the leaf. 
    """
)

# Footer with a relevant emoji for a more appealing end
st.markdown("---")
st.markdown("Powered by 🌱 Mango Leaf Disease Detection System 🍃")
