import streamlit as st
from pymongo import MongoClient
import pandas as pd
from darts import TimeSeries
from darts.models import LightGBMModel
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# Load the model
model = LightGBMModel.load("modelscawol.pkl")

# Set up the MongoDB client
client = MongoClient("mongodb+srv://aylascawol:scawolmenyala@ayla-sic5-scawol.grwwhow.mongodb.net/?retryWrites=true&w=majority")
db = client['scawol-database']
collection = db['sensor-colection3']

def opsi():
    mint = st.number_input('Pilihlah berapa menit kedepan:', min_value=5, max_value=100, value=5,step=5)
    return int(mint/5)

def lakukan_forecast():
    data_list = list(collection.find({}))
    if not data_list:
        st.write("No data available in the collection.")
        return

    data_raw = pd.DataFrame(data_list).drop("_id", axis=1)
    data_raw["timestamp"] = pd.to_datetime(data_raw["timestamp"]).dt.round("5min")
    data = (
        data_raw.groupby("timestamp")
        .agg({"jarak": "mean"})
        .reset_index()
    )
    
    target_series = TimeSeries.from_dataframe(data, time_col="timestamp", fill_missing_dates=True, freq="5min")
    input_value = opsi()
    
    if st.button('Prediksi'):
        predicted = model.predict(input_value, series=target_series)
        predicted_df = predicted.pd_dataframe()
        
        st.write("Berikut adalah data prediksi ketinggian air:")
        for col in predicted_df.columns:
            st.metric(label="Ketinggian Air", value=int(predicted_df[col].iloc[-1]))

        # min_value = predicted_df.min().min()
        # st.write(f"Ketinggian dari prediksi adalah: {int(min_value)} ")

        # Plot historical and forecast data
        historical_df = data.set_index("timestamp")
        predicted_df.index = pd.date_range(start=historical_df.index[-1], periods=len(predicted_df) + 1, freq="5min")[1:]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=historical_df.index, y=historical_df["jarak"], mode='lines', name='Historical Data'))
        fig.add_trace(go.Scatter(x=predicted_df.index, y=predicted_df.iloc[:, 0], mode='lines', name='Forecasted Data'))
        
        fig.update_layout(
            title='Historical and Forecasted Water Levels',
            xaxis_title='Time',
            yaxis_title='Water Level',
            legend_title='Legend'
        )

        st.plotly_chart(fig)

# Fungsi untuk halaman Data
def data_page():
    st.title("Data Treker Solar Panel")
    data = list(collection.find())

    if data:
        df = pd.DataFrame(data)
        st.write("Berikut adalah data dari panel surya Anda:")
        chart_data = pd.DataFrame(np.random.randn(10, 1), columns=["jarak"])
        st.dataframe(df)
        st.area_chart(chart_data)
        st.line_chart(chart_data)
    else:
        st.write("Tidak ada data yang tersedia.")

# Fungsi untuk halaman Riwayat
def history_page():
    st.title("Riwayat")
    st.write("Riwayat data yang terkumpul dalam waktu 1 hari:")
    # Tambahkan grafik atau tabel riwayat kinerja di sini

# Fungsi untuk halaman Notification
def notification_page():
    st.title("Notification")
    st.write("Panduan untuk memberi peringatan akan problem yang:")
    # Tambahkan informasi pemecahan masalah di sini

# Fungsi untuk halaman Informasi
def info_page():
    st.title("Informasi")
    st.write("Informasi umum tentang cara kerja dari Treker Solar Panel:")
    # Tambahkan informasi umum di sini

# Fungsi utama untuk menjalankan aplikasi
def main():
    st.sidebar.title("Navigasi")
    page = st.sidebar.selectbox("Pilih halaman", ["Data", "Prediksi", "Riwayat", "Notification", "Informasi"])

    if page == "Data":
        data_page()
    elif page == "Prediksi":
        lakukan_forecast()
    elif page == "Riwayat":
        history_page()
    elif page == "Notification":
        notification_page()
    elif page == "Informasi":
        info_page()

if __name__ == "__main__":
    main()
