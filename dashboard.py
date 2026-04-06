import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style='dark')

# Load data
new_hour_df = pd.read_csv("new_hour_df.csv")
new_day_df = pd.read_csv("new_day_df.csv")

all_df = pd.merge(new_hour_df, new_day_df, on="dteday")
all_df = all_df.rename(columns={
    'yr_x': 'yr',
    'cnt_x': 'cnt'
})

# Ambil min & max date (convert ke date)
all_df['dteday'] = pd.to_datetime(all_df['dteday'])
min_date = all_df['dteday'].min().date()
max_date = all_df['dteday'].max().date()

# Sidebar
st.sidebar.header("Filter")
with st.sidebar:
    date_range = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Handle jika user pilih 1 atau 2 tanggal
if isinstance(date_range, list) or isinstance(date_range, tuple):
    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range[0]
else:
    start_date = end_date = date_range

# Filter data
main_df = all_df[
    (all_df['dteday'] >= pd.to_datetime(start_date)) &
    (all_df['dteday'] <= pd.to_datetime(end_date))
]

# Fungsi Pertanyaan 1
def countAverageBicycle(df):
    day_2012 = df[df['yr'] == 1]
    average_bicycles = day_2012.groupby(['mnth', 'workingday'])['cnt'].mean().reset_index()
    
    pivot_average_bicycles = average_bicycles.pivot(
        index='mnth',
        columns='workingday',
        values='cnt'
    )

    pivot_average_bicycles.columns = ['Holiday/Weekend', 'Working Day']

    return pivot_average_bicycles

def plot_averageBicycle(pivot_df):
    fig, ax = plt.subplots(figsize=(10,5))
    ax.plot(pivot_df.index,
            pivot_df['Working Day'],
            marker='o', label='Working Day')

    ax.plot(pivot_df.index,
            pivot_df['Holiday/Weekend'],
            marker='o', label='Holiday/Weekend')

    ax.set_title('Rata-rata Peminjaman Sepeda per Bulan (2012)')
    ax.set_xlabel('Bulan')
    ax.set_ylabel('Jumlah Peminjaman')
    ax.set_xticks(pivot_df.index)
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)

# Fungsi Pertanyaan 2
def countWeatherResult(df):
    day_2012 = df[df['yr'] == 1]

    weather_result = day_2012.groupby('weathersit')['cnt'].sum().reset_index()
    weather_result = weather_result.sort_values(by='cnt', ascending=False)

    return weather_result

def plot_weatherResult(weather_result):
    weather_labels = {
        1: 'Clear / Partly Cloudy',
        2: 'Mist / Cloudy',
        3: 'Light Rain / Snow'
    }

    weather_filtered = weather_result[weather_result['weathersit'].isin([1,2,3])].copy()
    weather_filtered['label'] = weather_filtered['weathersit'].map(weather_labels)

    colors = ['#08306b', '#2171b5', '#6baed6']
    
    fig, ax = plt.subplots(figsize=(8,5))
    ax.bar(weather_filtered['label'], weather_filtered['cnt'], color=colors)

    ax.set_title('Total Peminjaman Sepeda Berdasarkan Kondisi Cuaca (2012)')
    ax.set_xlabel('Kondisi Cuaca')
    ax.set_ylabel('Total Peminjaman')
    plt.xticks(rotation=20)
    ax.grid(axis='y')

    st.pyplot(fig)

# Fungsi Pertanyaan 3
def compareHours(df):
    hour_2011 = df[df['yr'] == 0]
    hour_result_2011 = hour_2011.groupby('hr')['cnt'].sum().reset_index()
    hour_result_2011 = hour_result_2011.sort_values(by='hr', ascending=True)

    hour_2012 = df[df['yr'] == 1]
    hour_result_2012 = hour_2012.groupby('hr')['cnt'].sum().reset_index()
    hour_result_2012 = hour_result_2012.sort_values(by='hr', ascending=True)

    hour_result_2011.rename(columns={'cnt': '2011'}, inplace=True)
    hour_result_2012.rename(columns={'cnt': '2012'}, inplace=True)

    hour_compare = pd.merge(hour_result_2011, hour_result_2012, on='hr')

    return hour_compare

def plot_compareHours(hour_compare):
    fig, ax = plt.subplots(figsize=(10,5))

    ax.plot(hour_compare['hr'], hour_compare['2011'],
            marker='o', label='2011')
    ax.plot(hour_compare['hr'], hour_compare['2012'],
            marker='o', label='2012')

    ax.set_title('Perbandingan Peminjaman Sepeda per Jam (2011 vs 2012)')
    ax.set_xlabel('Jam')
    ax.set_ylabel('Total Peminjaman')
    ax.set_xticks(range(0,24))
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)

# Fungsi Clustering
def add_time_group(df):
    def time_category(hour):
        if 5 <= hour < 10:
            return 'Pagi'
        elif 10 <= hour < 15:
            return 'Siang'
        elif 15 <= hour < 19:
            return 'Sore'
        else:
            return 'Malam'
    
    df = df.copy()
    df['time_group'] = df['hr'].apply(time_category)
    return df

def get_time_group_result(df):
    result = df.groupby('time_group')['cnt'].sum().reset_index()
    return result

def plot_time_group(result):
    color_map = {
        'Pagi': '#FFA500',   
        'Siang': '#FFD700',  
        'Sore': '#FF6347',   
        'Malam': '#2F4F4F'   
    }

    colors = [color_map[t] for t in result['time_group']]
    fig, ax = plt.subplots(figsize=(8,5))

    ax.bar(result['time_group'], result['cnt'],
           color=colors, edgecolor='black')

    ax.set_title('Total Peminjaman Sepeda Berdasarkan Waktu')
    ax.set_xlabel('Waktu')
    ax.set_ylabel('Total Peminjaman')
    ax.grid(axis='y')

    st.pyplot(fig)

# Home
st.title("Dashboard Bike Sharing")

home_dashboard = main_df.groupby('dteday')['cnt'].sum()
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Peminjaman", f"{home_dashboard.sum():,}")
with col2:
    st.metric("Rata-rata Harian", f"{home_dashboard.mean():.0f}")
with col3:
    st.metric("Peminjaman Tertinggi", f"{home_dashboard.max():,}")
    
tab1, tab2, tab3, tab4 = st.tabs(["📅 Analisis Bulanan", "🌦️ Analisis Cuaca (Dinamis)", "⏱️ Analisis Waktu", "⏱️ Clustering Waktu (Dinamis)"])

with tab1:
    st.subheader("Pola Bulanan (Working vs Holiday)")
    pivot_df = countAverageBicycle(new_day_df)
    plot_averageBicycle(pivot_df)

with tab2:
    st.subheader("Pengaruh Cuaca")
    weather_result = countWeatherResult(main_df)
    plot_weatherResult(weather_result)

with tab3: 
    st.subheader("Pengaruh Waktu")
    hour_compare = compareHours(new_hour_df)
    plot_compareHours(hour_compare)

with tab4:
    st.subheader("Clustering Waktu")
    df_time = add_time_group(main_df)
    time_result = get_time_group_result(df_time)
    plot_time_group(time_result)