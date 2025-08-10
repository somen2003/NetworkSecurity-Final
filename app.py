import streamlit as st
import pandas as pd
import os
import sys
import certifi
from dotenv import load_dotenv
import pymongo

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.pipeline.training_pipeline import TrainingPipeline
from networksecurity.utils.main_utils.utils import load_object
from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.constant.training_pipeline import DATA_INGESTION_COLLECTION_NAME, DATA_INGESTION_DATABASE_NAME

# Load environment variables
load_dotenv()
mongo_db_url = os.getenv("MONGODB_URL_KEY")
ca = certifi.where()

# Connect to MongoDB (if needed)
client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)
database = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]

st.set_page_config(page_title="Phishing URL Detection", layout="wide")
st.title("🔍 Phishing URL Detection")

# -------- Train Model --------
if st.button("Train Model"):
    try:
        train_pipeline = TrainingPipeline()
        train_pipeline.run_pipeline()
        st.success("✅ Model training completed successfully!")
    except Exception as e:
        st.error(f"❌ Training failed: {e}")

# -------- Prediction Section --------
uploaded_file = st.file_uploader("Upload CSV file for prediction", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        # Load saved preprocessor and model
        preprocessor = load_object("final_model/preprocessor.pkl")
        final_model = load_object("final_model/model.pkl")
        network_model = NetworkModel(preprocessor=preprocessor, model=final_model)

        # Predict
        y_pred = network_model.predict(df)
        df["predicted_column"] = y_pred

        # Map predictions for readability
        mapping = {1: "Phishy", 0: "Non-Phishy", -1: "Non-Phishy"}
        df["Prediction Label"] = df["predicted_column"].map(mapping)

        # Count results
        phishy_count = (df["Prediction Label"] == "Phishy").sum()
        non_phishy_count = (df["Prediction Label"] == "Non-Phishy").sum()

        # Display counts
        st.subheader("📊 Prediction Summary")
        col1, col2 = st.columns(2)
        col1.metric("Phishy URLs", phishy_count)
        col2.metric("Non-Phishy URLs", non_phishy_count)

        # Show table
        st.subheader("📄 Predictions Table")
        st.dataframe(df)

        # Download results
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇ Download Predictions",
            data=csv,
            file_name="predictions.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"❌ Prediction failed: {e}")
