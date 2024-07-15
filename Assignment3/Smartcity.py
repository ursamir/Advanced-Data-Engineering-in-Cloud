import streamlit as st
import pandas as pd
import boto3
from io import BytesIO
import json
import plotly.express as px
from datetime import datetime, timezone

# Read AWS credentials from aws.json
with open('aws.json', 'r') as f:
    configuration = json.load(f)

# Connect to S3
s3 = boto3.client('s3',
                  aws_access_key_id=configuration.get('AWS_ACCESS_KEY'),
                  aws_secret_access_key=configuration.get('AWS_SECRET_KEY'))

# Example bucket and file names
bucket_name = 'g23ai1052'
vehicle_data_key = 'new/part-00000-ae1b976c-a6eb-4ecc-b23d-cea47afcc9d4-c000.csv'
failures_data_key = 'new/part-00000-3d123824-00ff-4587-a97b-c861159630f5-c000.csv'
weather_data_key = 'new/part-00000-b9930110-e618-4208-8389-03e19fbb7480-c000.csv'

# Function to read CSV from S3
def read_csv_from_s3(bucket, key):
    obj = s3.get_object(Bucket=bucket, Key=key)
    df = pd.read_csv(BytesIO(obj['Body'].read()))
    return df

# Read data from S3
df_vehicle = read_csv_from_s3(bucket_name, vehicle_data_key)
df_failures = read_csv_from_s3(bucket_name, failures_data_key)
df_weather = read_csv_from_s3(bucket_name, weather_data_key)

# Convert timestamp column to pd.Timestamp if not already
df_vehicle['timestamp'] = pd.to_datetime(df_vehicle['timestamp'], utc=True)
df_failures['timestamp'] = pd.to_datetime(df_failures['timestamp'], utc=True)
df_weather['timestamp'] = pd.to_datetime(df_weather['timestamp'], utc=True)

# Title of the app
st.title('Smart City Visualization App')

# Date and time range selection
st.sidebar.subheader('Date and Time Range Selection')

# Calculate min and max datetime from timestamp column for all datasets
min_datetime_all = min(df_vehicle['timestamp'].min(), df_failures['timestamp'].min(), df_weather['timestamp'].min())
max_datetime_all = max(df_vehicle['timestamp'].max(), df_failures['timestamp'].max(), df_weather['timestamp'].max())

# Date and time input widgets for all datasets
start_date_all = st.sidebar.date_input('Start Date', min_value=min_datetime_all.date(), max_value=max_datetime_all.date(), value=min_datetime_all.date())
end_date_all = st.sidebar.date_input('End Date', min_value=min_datetime_all.date(), max_value=max_datetime_all.date(), value=max_datetime_all.date())
start_time_all = st.sidebar.time_input('Start Time', value=datetime.min.time())
end_time_all = st.sidebar.time_input('End Time', value=datetime.max.time())

# Combine date and time into datetime objects for all datasets
start_datetime_all = datetime.combine(start_date_all, start_time_all)
end_datetime_all = datetime.combine(end_date_all, end_time_all)

# Convert start_datetime and end_datetime to pd.Timestamp in UTC for all datasets
start_datetime_utc_all = pd.Timestamp(start_datetime_all, tzinfo=timezone.utc)
end_datetime_utc_all = pd.Timestamp(end_datetime_all, tzinfo=timezone.utc)

# Filter data for all datasets based on unified date and time range
filtered_vehicle_data = df_vehicle[(df_vehicle['timestamp'] >= start_datetime_utc_all) & (df_vehicle['timestamp'] <= end_datetime_utc_all)]
filtered_failures_data = df_failures[(df_failures['timestamp'] >= start_datetime_utc_all) & (df_failures['timestamp'] <= end_datetime_utc_all)]
filtered_weather_data = df_weather[(df_weather['timestamp'] >= start_datetime_utc_all) & (df_weather['timestamp'] <= end_datetime_utc_all)]

# Display filtered data for all datasets
st.header('Filtered Vehicle Data')
st.write(filtered_vehicle_data)

st.header('Filtered Failures Data')
st.write(filtered_failures_data)

st.header('Filtered Weather Data')
st.write(filtered_weather_data)

# Example chart with Plotly for vehicle data
st.header('Vehicle Speed Over Time')
fig_vehicle = px.line(filtered_vehicle_data, x='timestamp', y='speed', title='Vehicle Speed Over Time')
st.plotly_chart(fig_vehicle)

# Example chart with Plotly for failures data
st.header('Failures Count Over Time')
fig_failures = px.line(filtered_failures_data, x='timestamp', title='Failures Count Over Time')
st.plotly_chart(fig_failures)

# Example chart with Plotly for weather data
st.header('Weather Data Visualization')
fig_weather = px.line(filtered_weather_data, x='timestamp', y='temperature', title='Temperature Over Time')
st.plotly_chart(fig_weather)
