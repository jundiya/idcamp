import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Read csv file
df = pd.read_csv('D:/submission/dashboard/merged_dataset.csv')

# Add datetime column
df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])

# Clustering
def manual_grouping(pm25):
    if pm25 <= 12:
        return 'Rendah'
    elif pm25 <= 35:
        return 'Sedang'
    elif pm25 <= 55:
        return 'Tidak Sehat Untuk Kelompok Sensitif'
    elif pm25 <= 150:
        return 'Tidak Sehat'
    elif pm25 <= 250:
        return 'Sangat Tidak Sehat'
    else:
        return 'Berbahaya'
    
df['AQI'] = df['PM2.5'].apply(manual_grouping)

# Add helper functions
def create_daily_observation_df(df):
    daily_observation_df = df.resample(rule='D', on='datetime').agg({"PM2.5": "mean"})
    daily_observation_df = daily_observation_df.reset_index()
    return daily_observation_df

def create_monthly_observation_df(df):
    monthly_observation_df = df.resample(rule='M', on='datetime').agg({"PM2.5": "mean"})
    monthly_observation_df = monthly_observation_df.reset_index()
    return monthly_observation_df

def create_yearly_observation_df(df):
    yearly_observation_df = df.resample(rule='Y', on='datetime').agg({"PM2.5": "mean"})
    yearly_observation_df = yearly_observation_df.reset_index()
    return yearly_observation_df

def create_bystation_df(df):
    bystation_df = df.groupby('station').agg({"PM2.5": "mean"})
    bystation_df = bystation_df.reset_index()
    return bystation_df

def create_corr_df(df):
    corr_df = df[['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']].corr()
    return corr_df

# Add filter component
min_date = df["datetime"].min()
max_date = df["datetime"].max()
 
with st.sidebar:
    # Add picture
    st.image("https://plus.unsplash.com/premium_photo-1661436200971-0e3e0f2fc954?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D")
    
    # Add start and end date
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = df[(df['datetime'] >= str(start_date)) & (df['datetime'] <= str(end_date))]

# Create observation dataframes
daily_observation_df = create_daily_observation_df(main_df)
monthly_observation_df = create_monthly_observation_df(main_df)
yearly_observation_df = create_yearly_observation_df(main_df)
bystation_df = create_bystation_df(main_df)
corr_df = create_corr_df(main_df)

# Calculate mean AQI by station
mean_aqi_by_station_df = main_df.groupby('station')['PM2.5'].mean().reset_index()
mean_aqi_by_station_df['AQI Category'] = mean_aqi_by_station_df['PM2.5'].apply(manual_grouping)

# Add visualization
st.header('Air Quality Dashboard')

col1, col2 = st.columns(2)

with col1:
    total_stations = df['station'].nunique()
    st.metric("Total Station", value=str(total_stations))

# Daily observation plot
st.subheader('Daily Observation')
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_observation_df['datetime'],
    daily_observation_df['PM2.5'],
    marker='o',
    linewidth=2,
    color='blue'
)
ax.tick_params(axis='y', labelsize=15)
ax.tick_params(axis='x', labelsize=15)
ax.set_title("Daily Average PM2.5", fontsize=20)
ax.set_ylabel("PM2.5 Level", fontsize=15)
ax.set_xlabel(None)
st.pyplot(fig)

# Monthly observation plot
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    monthly_observation_df['datetime'],
    monthly_observation_df['PM2.5'],
    marker='o',
    linewidth=2,
    color='blue'
)
ax.tick_params(axis='y', labelsize=15)
ax.tick_params(axis='x', labelsize=15)
ax.set_title("Monthly Average PM2.5", fontsize=20)
ax.set_ylabel("PM2.5 Level", fontsize=15)
ax.set_xlabel(None)
st.pyplot(fig)

# Yearly observation plot
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    yearly_observation_df['datetime'],
    yearly_observation_df['PM2.5'],
    marker='o',
    linewidth=2,
    color='blue'
)
ax.tick_params(axis='y', labelsize=15)
ax.tick_params(axis='x', labelsize=15)
ax.set_title("Yearly Average PM2.5", fontsize=20)
ax.set_ylabel("PM2.5 Level", fontsize=15)
ax.set_xlabel(None)
st.pyplot(fig)

# Station observation bar chart
st.subheader("Station Observation")
fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#90CAF9"] + ["#D3D3D3"] * (len(bystation_df) - 1)
sns.barplot(
    x="PM2.5",
    y="station",
    data=bystation_df.sort_values(by="PM2.5", ascending=False),
    palette=colors,
    ax=ax
)
ax.tick_params(axis='y', labelsize=15)
ax.tick_params(axis='x', labelsize=15)
ax.set_title("Average PM2.5 by Station", loc="center", fontsize=20)
ax.set_ylabel(None)
ax.set_xlabel("PM2.5 Level", fontsize=15)
st.pyplot(fig)

# Correlation heatmap
st.subheader("Correlation")
fig, ax = plt.subplots(figsize=(20, 10))
sns.heatmap(corr_df, annot=True, cmap='coolwarm')
ax.set_title('Correlation Between Meteorological and Pollutant Variables', fontsize=20)
st.pyplot(fig)

# Calculate mean AQI by station
mean_aqi_by_station_df = main_df.groupby('station')['PM2.5'].mean().reset_index()
mean_aqi_by_station_df['AQI Category'] = mean_aqi_by_station_df['PM2.5'].apply(manual_grouping)

# Display mean AQI by station
st.subheader("Air Quality Index")
st.table(mean_aqi_by_station_df)