import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import base64
from io import BytesIO
from PIL import Image
import datetime

# Setel gaya seaborn
sns.set(style='dark')

# Persiapkan data day_df
day_df = pd.read_csv("dashboard/day.csv")
day_df.head()

# Hapus kolom yang tidak diperlukan
kolom_hapus = ['windspeed']

for kolom in day_df.columns:
  if kolom in kolom_hapus:
    day_df.drop(labels=kolom, axis=1, inplace=True)

# Ubah nama kolom
day_df.rename(columns={
    'dteday': 'tanggal',
    'yr': 'tahun',
    'mnth': 'bulan',
    'weathersit': 'kondisi_cuaca',
    'cnt': 'jumlah'
}, inplace=True)

# Ubah angka menjadi keterangan
day_df['bulan'] = day_df['bulan'].map({
    1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'Mei', 6: 'Jun',
    7: 'Jul', 8: 'Ags', 9: 'Sep', 10: 'Okt', 11: 'Nov', 12: 'Des'
})
day_df['season'] = day_df['season'].map({
    1: 'Musim Semi', 2: 'Musim Panas', 3: 'Musim Gugur', 4: 'Musim Dingin'
})
day_df['weekday'] = day_df['weekday'].map({
    0: 'Minggu', 1: 'Senin', 2: 'Selasa', 3: 'Rabu', 4: 'Kamis', 5: 'Jumat', 6: 'Sabtu'
})
day_df['kondisi_cuaca'] = day_df['kondisi_cuaca'].map({
    1: 'Cerah/Setengah Berawan',
    2: 'Berembun/Berawan',
    3: 'Hujan Ringan/Salju',
    4: 'Cuaca Ekstrem'
})


# Persiapkan daily_rent_df
def buat_daily_rent_df(df):
    daily_rent_df = df.groupby(by='tanggal').agg({
        'jumlah': 'sum'
    }).reset_index()
    return daily_rent_df

# Persiapkan daily_casual_rent_df
def buat_daily_casual_rent_df(df):
    daily_casual_rent_df = df.groupby(by='tanggal').agg({
        'casual': 'sum'
    }).reset_index()
    return daily_casual_rent_df

# Persiapkan daily_registered_rent_df
def buat_daily_registered_rent_df(df):
    daily_registered_rent_df = df.groupby(by='tanggal').agg({
        'registered': 'sum'
    }).reset_index()
    return daily_registered_rent_df
    
# Persiapkan season_rent_df
def buat_season_rent_df(df):
    season_rent_df = df.groupby(by='season')[['registered', 'casual']].sum().reset_index()
    return season_rent_df

# Persiapkan monthly_rent_df
def buat_monthly_rent_df(df):
    monthly_rent_df = df.groupby(by='bulan').agg({
        'jumlah': 'sum'
    })
    ordered_months = [
        'Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun',
        'Jul', 'Ags', 'Sep', 'Okt', 'Nov', 'Des'
    ]
    monthly_rent_df = monthly_rent_df.reindex(ordered_months, fill_value=0)
    return monthly_rent_df

# Persiapkan weekday_rent_df
def buat_weekday_rent_df(df):
    weekday_rent_df = df.groupby(by='weekday').agg({
        'jumlah': 'sum'
    }).reset_index()
    return weekday_rent_df

# Persiapkan workingday_rent_df
def buat_workingday_rent_df(df):
    workingday_rent_df = df.groupby(by='workingday').agg({
        'jumlah': 'sum'
    }).reset_index()
    return workingday_rent_df

# Persiapkan holiday_rent_df
def buat_holiday_rent_df(df):
    holiday_rent_df = df.groupby(by='holiday').agg({
        'jumlah': 'sum'
    }).reset_index()
    return holiday_rent_df

# Persiapkan weather_rent_df
def buat_weather_rent_df(df):
    weather_rent_df = df.groupby(by='kondisi_cuaca').agg({
        'jumlah': 'sum'
    })
    return weather_rent_df


# Buat komponen filter
min_tanggal = pd.to_datetime(day_df['tanggal']).dt.date.min()
max_tanggal = pd.to_datetime(day_df['tanggal']).dt.date.max()
 
# Sidebar
with st.sidebar:
    st.title("Pemilih Rentang Tanggal")

    # Setel tanggal awal dan akhir default menjadi Januari 2011 dan Desember 2012
    tanggal_awal_default = datetime.date(2011, 1, 1)
    tanggal_akhir_default = datetime.date(2012, 12, 31)

    tanggal_awal, tanggal_akhir = st.date_input(
        "Pilih rentang tanggal",
        (tanggal_awal_default, tanggal_akhir_default)
    )

# Konten utama
st.write(f"Rentang Tanggal Terpilih: {tanggal_awal} hingga {tanggal_akhir}")


main_df = day_df[(day_df['tanggal'] >= str(tanggal_awal)) & 
                (day_df['tanggal'] <= str(tanggal_akhir))]

# Persiapkan berbagai dataframe
daily_rent_df = buat_daily_rent_df(main_df)
daily_casual_rent_df = buat_daily_casual_rent_df(main_df)
daily_registered_rent_df = buat_daily_registered_rent_df(main_df)
season_rent_df = buat_season_rent_df(main_df)
monthly_rent_df = buat_monthly_rent_df(main_df)
weekday_rent_df = buat_weekday_rent_df(main_df)
workingday_rent_df = buat_workingday_rent_df(main_df)
holiday_rent_df = buat_holiday_rent_df(main_df)
weather_rent_df = buat_weather_rent_df(main_df)


# Buat Dasbor secara Lengkap

# Buat judul
st.header('Dasbor Rental Sepeda 🚲')

# Buat jumlah sewaan harian
st.subheader('Sewaan Harian')
kolom1, kolom2, kolom3 = st.columns(3)

with kolom1:
    daily_rent_casual = daily_casual_rent_df['casual'].sum()
    st.metric('Pengguna Biasa', value= daily_rent_casual)

with kolom2:
    daily_rent_registered = daily_registered_rent_df['registered'].sum()
    st.metric('Pengguna Terdaftar', value= daily_rent_registered)
 
with kolom3:
    daily_rent_total = daily_rent_df['jumlah'].sum()
    st.metric('Total Pengguna', value= daily_rent_total)

# Buat jumlah sewaan bulanan
st.subheader('Sewaan Bulanan')
figur, sumbu = plt.subplots(figsize=(24, 8))
sumbu.plot(
    monthly_rent_df.index,
    monthly_rent_df['jumlah'],
    marker='o', 
    linewidth=2,
    color='tab:blue'
)

for index, nilai in enumerate(monthly_rent_df['jumlah']):
    sumbu.text(index, nilai + 1, str(nilai), ha='center', va='bottom', fontsize=12)

sumbu.tick_params(axis='x', labelsize=25, rotation=45)
sumbu.tick_params(axis='y', labelsize=20)
st.pyplot(figur)

# Buat jumlah sewaan berdasarkan musim
st.subheader('Sewaan Musiman')

figur, sumbu = plt.subplots(figsize=(16, 8))

sns.barplot(
    x='season',
    y='registered',
    data=season_rent_df,
    label='Terdaftar',
    color='tab:blue',
    ax=sumbu
)

sns.barplot(
    x='season',
    y='casual',
    data=season_rent_df,
    label='Biasa',
    color='tab:orange',
    ax=sumbu
)

for index, baris in season_rent_df.iterrows():
    sumbu.text(index, baris['registered'], str(baris['registered']), ha='center', va='bottom', fontsize=12)
    sumbu.text(index, baris['casual'], str(baris['casual']), ha='center', va='bottom', fontsize=12)

sumbu.set_xlabel(None)
sumbu.set_ylabel(None)
sumbu.tick_params(axis='x', labelsize=20, rotation=0)
sumbu.tick_params(axis='y', labelsize=15)
sumbu.legend()
st.pyplot(figur)

# Buat jumlah sewaan berdasarkan kondisi cuaca
st.subheader('Sewaan Berdasarkan Cuaca')

figur, sumbu = plt.subplots(figsize=(16, 8))

warna=["tab:blue", "tab:orange", "tab:green"]

sns.barplot(
    x=weather_rent_df.index,
    y=weather_rent_df['jumlah'],
    palette=warna,
    ax=sumbu
)

for index, nilai in enumerate(weather_rent_df['jumlah']):
    sumbu.text(index, nilai + 1, str(nilai), ha='center', va='bottom', fontsize=12)

sumbu.set_xlabel(None)
sumbu.set_ylabel(None)
sumbu.tick_params(axis='x', labelsize=20)
sumbu.tick_params(axis='y', labelsize=15)
st.pyplot(figur)

# Buat jumlah sewaan berdasarkan hari kerja, hari biasa, dan hari libur
st.subheader('Sewaan Berdasarkan Hari Kerja, Hari Biasa, dan Hari Libur')

figur, sumbu2 = plt.subplots(nrows=3, ncols=1, figsize=(15,10))

warna1=["tab:blue", "tab:orange"]
warna2=["tab:blue", "tab:orange"]
warna3=["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple", "tab:brown", "tab:pink"]

# Berdasarkan hari kerja
sns.barplot(
    x='workingday',
    y='jumlah',
    data=workingday_rent_df,
    palette=warna1,
    ax=sumbu2[0])

for index, nilai in enumerate(workingday_rent_df['jumlah']):
    sumbu2[0].text(index, nilai + 1, str(nilai), ha='center', va='bottom', fontsize=12)

sumbu2[0].set_title('Jumlah Rents berdasarkan Hari Kerja')
sumbu2[0].set_ylabel(None)
sumbu2[0].tick_params(axis='x', labelsize=15)
sumbu2[0].tick_params(axis='y', labelsize=10)

# Berdasarkan hari libur
sns.barplot(
  x='holiday',
  y='jumlah',
  data=holiday_rent_df,
  palette=warna2,
  ax=sumbu2[1])

for index, nilai in enumerate(holiday_rent_df['jumlah']):
    sumbu2[1].text(index, nilai + 1, str(nilai), ha='center', va='bottom', fontsize=12)

sumbu2[1].set_title('Jumlah Rents berdasarkan Hari Libur')
sumbu2[1].set_ylabel(None)
sumbu2[1].tick_params(axis='x', labelsize=15)
sumbu2[1].tick_params(axis='y', labelsize=10)

# Berdasarkan hari biasa
sns.barplot(
  x='weekday',
  y='jumlah',
  data=weekday_rent_df,
  palette=warna3,
  ax=sumbu2[2])

for index, nilai in enumerate(weekday_rent_df['jumlah']):
    sumbu2[2].text(index, nilai + 1, str(nilai), ha='center', va='bottom', fontsize=12)

sumbu2[2].set_title('Jumlah Rents berdasarkan Hari Biasa')
sumbu2[2].set_ylabel(None)
sumbu2[2].tick_params(axis='x', labelsize=15)
sumbu2[2].tick_params(axis='y', labelsize=10)

plt.tight_layout()
st.pyplot(figur)

st.caption('Copyright @ 2023 Dimas Raihan Pratama')
