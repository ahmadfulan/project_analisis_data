import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import base64
from io import BytesIO
from PIL import Image
import datetime

# Set Seaborn style
sns.set(style='dark')

# Prepare the day_df data
day_df = pd.read_csv("dashboard/day.csv")
day_df.head()

# Remove unnecessary columns
columns_to_remove = ['windspeed']

for column in day_df.columns:
  if column in columns_to_remove:
    day_df.drop(labels=column, axis=1, inplace=True)

# Rename columns
day_df.rename(columns={
    'dteday': 'date',
    'yr': 'year',
    'mnth': 'month',
    'weathersit': 'weather_condition',
    'cnt': 'count'
}, inplace=True)

# Convert numbers to labels
day_df['month'] = day_df['month'].map({
    1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
    7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
})
day_df['season'] = day_df['season'].map({
    1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'
})
day_df['weekday'] = day_df['weekday'].map({
    0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday'
})
day_df['weather_condition'] = day_df['weather_condition'].map({
    1: 'Clear/Partly Cloudy',
    2: 'Mist/Cloudy',
    3: 'Light Rain/Snow',
    4: 'Extreme Weather'
})

# Prepare daily_rent_df
def create_daily_rent_df(df):
    daily_rent_df = df.groupby(by='date').agg({
        'count': 'sum'
    }).reset_index()
    return daily_rent_df

# Prepare daily_casual_rent_df
def create_daily_casual_rent_df(df):
    daily_casual_rent_df = df.groupby(by='date').agg({
        'casual': 'sum'
    }).reset_index()
    return daily_casual_rent_df

# Prepare daily_registered_rent_df
def create_daily_registered_rent_df(df):
    daily_registered_rent_df = df.groupby(by='date').agg({
        'registered': 'sum'
    }).reset_index()
    return daily_registered_rent_df
    
# Prepare season_rent_df
def create_season_rent_df(df):
    season_rent_df = df.groupby(by='season')[['registered', 'casual']].sum().reset_index()
    return season_rent_df

# Prepare monthly_rent_df
def create_monthly_rent_df(df):
    monthly_rent_df = df.groupby(by='month').agg({
        'count': 'sum'
    })
    ordered_months = [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ]
    monthly_rent_df = monthly_rent_df.reindex(ordered_months, fill_value=0)
    return monthly_rent_df

# Prepare weekday_rent_df
def create_weekday_rent_df(df):
    weekday_rent_df = df.groupby(by='weekday').agg({
        'count': 'sum'
    }).reset_index()
    return weekday_rent_df

# Prepare workingday_rent_df
def create_workingday_rent_df(df):
    workingday_rent_df = df.groupby(by='workingday').agg({
        'count': 'sum'
    }).reset_index()
    return workingday_rent_df

# Prepare holiday_rent_df
def create_holiday_rent_df(df):
    holiday_rent_df = df.groupby(by='holiday').agg({
        'count': 'sum'
    }).reset_index()
    return holiday_rent_df

# Prepare weather_rent_df
def create_weather_rent_df(df):
    weather_rent_df = df.groupby(by='weather_condition').agg({
        'count': 'sum'
    })
    return weather_rent_df

# Create filter components
min_date = pd.to_datetime(day_df['date']).dt.date.min()
max_date = pd.to_datetime(day_df['date']).dt.date.max()
 
# Sidebar
with st.sidebar:
    st.title("Date Range Selector")

    # Set default start and end dates to January 1, 2011, and December 31, 2012
    default_start_date = datetime.date(2011, 1, 1)
    default_end_date = datetime.date(2012, 12, 31)

    start_date, end_date = st.date_input(
        "Select date range",
        (default_start_date, default_end_date)
    )

# Main content
st.write(f"Selected Date Range: {start_date} to {end_date}")

main_df = day_df[(day_df['date'] >= str(start_date)) & 
                (day_df['date'] <= str(end_date))]

# Prepare various dataframes
daily_rent_df = create_daily_rent_df(main_df)
daily_casual_rent_df = create_daily_casual_rent_df(main_df)
daily_registered_rent_df = create_daily_registered_rent_df(main_df)
season_rent_df = create_season_rent_df(main_df)
monthly_rent_df = create_monthly_rent_df(main_df)
weekday_rent_df = create_weekday_rent_df(main_df)
workingday_rent_df = create_workingday_rent_df(main_df)
holiday_rent_df = create_holiday_rent_df(main_df)
weather_rent_df = create_weather_rent_df(main_df)

# Create Comprehensive Dashboard

# Create title
st.header('Bike Rental Dashboard 🚲')

# Create daily rental count
st.subheader('Daily Rentals')
column1, column2, column3 = st.columns(3)

with column1:
    daily_rent_casual = daily_casual_rent_df['casual'].sum()
    st.metric('Casual Users', value=daily_rent_casual)

with column2:
    daily_rent_registered = daily_registered_rent_df['registered'].sum()
    st.metric('Registered Users', value=daily_rent_registered)
 
with column3:
    daily_rent_total = daily_rent_df['count'].sum()
    st.metric('Total Users', value=daily_rent_total)

# Create monthly rental count
st.subheader('Monthly Rentals')
figure, axis = plt.subplots(figsize=(24, 8))
axis.plot(
    monthly_rent_df.index,
    monthly_rent_df['count'],
    marker='o', 
    linewidth=2,
    color='tab:blue'
)

for index, value in enumerate(monthly_rent_df['count']):
    axis.text(index, value + 1, str(value), ha='center', va='bottom', fontsize=12)

axis.tick_params(axis='x', labelsize=25, rotation=45)
axis.tick_params(axis='y', labelsize=20)
st.pyplot(figure)

# Create seasonal rental count
st.subheader('Seasonal Rentals')

figure, axis = plt.subplots(figsize=(16, 8))

sns.barplot(
    x='season',
    y='registered',
    data=season_rent_df,
    label='Registered',
    color='tab:blue',
    ax=axis
)

sns.barplot(
    x='season',
    y='casual',
    data=season_rent_df,
    label='Casual',
    color='tab:orange',
    ax=axis
)

for index, row in season_rent_df.iterrows():
    axis.text(index, row['registered'], str(row['registered']), ha='center', va='bottom', fontsize=12)
    axis.text(index, row['casual'], str(row['casual']), ha='center', va='bottom', fontsize=12)

axis.set_xlabel(None)
axis.set_ylabel(None)
axis.tick_params(axis='x', labelsize=20, rotation=0)
axis.tick_params(axis='y', labelsize=15)
axis.legend()
st.pyplot(figure)

# Create rental count based on weather condition
st.subheader('Rentals Based on Weather Condition')

figure, axis = plt.subplots(figsize=(16, 8))

colors=["tab:blue", "tab:orange", "tab:green"]

sns.barplot(
    x=weather_rent_df.index,
    y=weather_rent_df['count'],
    palette=colors,
    ax=axis
)

for index, value in enumerate(weather_rent_df['count']):
    axis.text(index, value + 1, str(value), ha='center', va='bottom', fontsize=12)

axis.set_xlabel(None)
axis.set_ylabel(None)
axis.tick_params(axis='x', labelsize=20)
axis.tick_params(axis='y', labelsize=15)
st.pyplot(figure)

# Create rental count based on working day, non-working day, and holiday
st.subheader('Rentals Based on Working Day, Non-Working Day, and Holiday')

figure, axes = plt.subplots(nrows=3, ncols=1, figsize=(15,10))

colors1=["tab:blue", "tab:orange"]
colors2=["tab:blue", "tab:orange"]
colors3=["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple", "tab:brown", "tab:pink"]

# Based on working day
sns.barplot(
    x='workingday',
    y='count',
    data=workingday_rent_df,
    palette=colors1,
    ax=axes[0])

for index, value in enumerate(workingday_rent_df['count']):
    axes[0].text(index, value + 1, str(value), ha='center', va='bottom', fontsize=12)

axes[0].set_title('Rental Count Based on Working Day')
axes[0].set_ylabel(None)
axes[0].tick_params(axis='x', labelsize=15)
axes[0].tick_params(axis='y', labelsize=10)

# Based on holiday
sns.barplot(
  x='holiday',
  y='count',
  data=holiday_rent_df,
  palette=colors2,
  ax=axes[1])

for index, value in enumerate(holiday_rent_df['count']):
    axes[1].text(index, value + 1, str(value), ha='center', va='bottom', fontsize=12)

axes[1].set_title('Rental Count Based on Holiday')
axes[1].set_ylabel(None)
axes[1].tick_params(axis='x', labelsize=15)
axes[1].tick_params(axis='y', labelsize=10)

# Based on weekday
sns.barplot(
  x='weekday',
  y='count',
  data=weekday_rent_df,
  palette=colors3,
  ax=axes[2])

for index, value in enumerate(weekday_rent_df['count']):
    axes[2].text(index, value + 1, str(value), ha='center', va='bottom', fontsize=12)

axes[2].set_title('Rental Count Based on Weekday')
axes[2].set_ylabel(None)
axes[2].tick_params(axis='x', labelsize=15)
axes[2].tick_params(axis='y', labelsize=10)

plt.tight_layout()
st.pyplot(figure)

st.caption('Copyright @ 2023 Dimas Raihan Pratama')
