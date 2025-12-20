import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import json

# ------------------ SETTINGS & THEME ------------------
st.set_page_config(
    page_title="Weather Analytics Dashboard",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for history tracking
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'favorite_cities' not in st.session_state:
    st.session_state.favorite_cities = []
if 'temp_unit' not in st.session_state:
    st.session_state.temp_unit = 'Celsius'
if 'compare_cities' not in st.session_state:
    st.session_state.compare_cities = []

# Custom Theme Colors
THEME_COLOR = "#00d4ff"
DARK_BG = "#0a0e27"
CARD_BG = "#1a1f3a"
TEXT_PRIMARY = "#ffffff"
ACCENT_COLOR = "#ff6b9d"
SUCCESS_COLOR = "#00ff88"
WARNING_COLOR = "#ff9500"

# ------------------ CUSTOM CSS ------------------
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    * {{ 
        font-family: 'Inter', sans-serif;
        box-sizing: border-box;
    }}
    
    .stApp {{
        background: radial-gradient(circle at top right, #1e293b, {DARK_BG});
        color: {TEXT_PRIMARY};
    }}
    
    [data-testid="stSidebar"] {{
        background: rgba(26, 31, 58, 0.95);
        border-right: 1px solid rgba(0, 212, 255, 0.1);
    }}
    
    .main-title {{
        background: linear-gradient(135deg, {THEME_COLOR} 0%, {ACCENT_COLOR} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 0.5rem;
        margin-top: 0;
        line-height: 1.2;
        word-wrap: break-word;
        display: block;
        padding: 10px 0;
    }}
    
    .metric-card {{
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px 18px;
        transition: all 0.3s ease;
        min-height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        overflow: visible;
        word-wrap: break-word;
    }}
    
    .metric-card:hover {{
        border-color: {THEME_COLOR};
        transform: translateY(-2px);
        background: rgba(0, 212, 255, 0.05);
        box-shadow: 0 8px 24px rgba(0, 212, 255, 0.15);
    }}
    
    .kpi-value {{
        font-size: 1.8rem;
        font-weight: 700;
        color: {THEME_COLOR};
        line-height: 1.1;
        margin: 5px 0;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }}
    
    .kpi-label {{
        font-size: 0.75rem;
        color: rgba(255, 255, 255, 0.6);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 3px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }}
    
    .kpi-subtitle {{
        font-size: 0.75rem;
        line-height: 1.3;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        margin-bottom: 2px;
    }}
    
    .status-badge {{
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        display: inline-block;
        margin-top: 2px;
        max-width: 100%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }}
    
    .alert-box {{
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
        border-left: 3px solid;
        min-height: 80px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        overflow: hidden;
        word-wrap: break-word;
    }}
    
    .alert-box strong {{
        display: block;
        margin-bottom: 5px;
        word-wrap: break-word;
        overflow-wrap: break-word;
        font-size: 0.9rem;
    }}
    
    .alert-box small {{
        display: block;
        line-height: 1.3;
        word-wrap: break-word;
        overflow-wrap: break-word;
        font-size: 0.8rem;
    }}
    
    .alert-warning {{
        background: rgba(255, 149, 0, 0.1);
        border-color: {WARNING_COLOR};
    }}
    
    .alert-danger {{
        background: rgba(255, 107, 157, 0.1);
        border-color: {ACCENT_COLOR};
    }}
    
    .alert-success {{
        background: rgba(0, 255, 136, 0.1);
        border-color: {SUCCESS_COLOR};
    }}
    
    .recommendation-card {{
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.05), rgba(255, 107, 157, 0.05));
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        min-height: 100px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        overflow: hidden;
        word-wrap: break-word;
    }}
    
    .recommendation-card strong {{
        display: block;
        margin-bottom: 5px;
        word-wrap: break-word;
        overflow-wrap: break-word;
        font-size: 0.9rem;
    }}
    
    .recommendation-card small {{
        display: block;
        line-height: 1.3;
        word-wrap: break-word;
        overflow-wrap: break-word;
        font-size: 0.8rem;
    }}
    
    /* Ensure consistent column heights */
    [data-testid="column"] {{
        display: flex;
        flex-direction: column;
        overflow: visible !important;
        padding: 5px 0;
    }}
    
    /* Prevent Streamlit from clipping cards */
    [data-testid="stHorizontalBlock"] {{
        overflow: visible !important;
        padding: 5px 0;
    }}
    
    [data-testid="stVerticalBlock"] {{
        overflow: visible !important;
    }}
    
    /* Better spacing for sections */
    .element-container {{
        margin-bottom: 0.5rem;
    }}
    
    /* Reduce section header spacing */
    h3 {{
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }}
    
    /* Align tabs properly */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px;
        overflow-x: auto;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        padding: 8px 16px;
        border-radius: 6px 6px 0 0;
        white-space: nowrap;
    }}
    
    /* Better dataframe styling */
    .stDataFrame {{
        border-radius: 8px;
        overflow: hidden;
    }}
    
    /* Fix text overflow in streamlit components */
    .stMarkdown {{
        overflow-wrap: break-word;
        word-wrap: break-word;
    }}
    
    /* Prevent horizontal scroll */
    .main .block-container {{
        max-width: 100%;
        padding-left: 2rem;
        padding-right: 2rem;
        padding-top: 1rem;
        padding-bottom: 1rem;
    }}
    
    /* Fix metric card content overflow */
    [data-testid="stMetric"] {{
        overflow: hidden;
    }}
    
    /* Better button alignment in sidebar */
    .stButton > button {{
        width: 100%;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    
    /* Curve the edges of charts */
    .js-plotly-plot {{
        border-radius: 15px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.05);
        background: rgba(255, 255, 255, 0.01);
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }}
    
    .js-plotly-plot:hover {{
        border-color: rgba(0, 212, 255, 0.2);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }}
    
    /* Reduce divider spacing */
    hr {{
        margin-top: 1rem !important;
        margin-bottom: 1rem !important;
    }}
    
    /* Landing Page Styling */
    .landing-hero {{
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.05), rgba(255, 107, 157, 0.05));
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 60px 40px;
        text-align: center;
        margin-bottom: 40px;
    }}
    
    .feature-card {{
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 25px;
        height: 100%;
        transition: all 0.3s ease;
    }}
    
    .feature-card:hover {{
        background: rgba(255, 255, 255, 0.05);
        border-color: {THEME_COLOR};
        transform: translateY(-5px);
    }}
    
    .cta-text {{
        font-size: 1.2rem;
        color: {THEME_COLOR};
        font-weight: 600;
        letter-spacing: 1px;
    }}
    /* Responsive Design Media Queries */
    @media (max-width: 1024px) {{
        .main-title {{
            font-size: 2.5rem;
        }}
        .main .block-container {{
            padding-left: 1rem;
            padding-right: 1rem;
        }}
    }}

    @media (max-width: 768px) {{
        .main-title {{
            font-size: 2rem;
            text-align: center;
        }}
        .metric-card {{
            min-height: 130px;
            padding: 15px 12px;
        }}
        .kpi-value {{
            font-size: 1.5rem;
        }}
        .kpi-label {{
            font-size: 0.7rem;
        }}
        /* Stack columns on small screens */
        [data-testid="stHorizontalBlock"] {{
            flex-direction: column !important;
        }}
        [data-testid="column"] {{
            width: 100% !important;
            min-width: 100% !important;
        }}
    }}

    @media (max-width: 480px) {{
        .main-title {{
            font-size: 1.5rem;
        }}
        .metric-card {{
            min-height: 110px;
            margin-bottom: 10px;
        }}
    }}
</style>
""", unsafe_allow_html=True)

# ------------------ API UTILITIES ------------------
API_KEY = "67b92f0af5416edbfe58458f502b0a31"

def celsius_to_fahrenheit(celsius):
    """Convert Celsius to Fahrenheit"""
    return (celsius * 9/5) + 32

def convert_temp(temp, unit):
    """Convert temperature based on selected unit"""
    if unit == 'Fahrenheit':
        return celsius_to_fahrenheit(temp)
    return temp

def get_temp_symbol(unit):
    """Get temperature symbol"""
    return '°F' if unit == 'Fahrenheit' else '°C'

def fetch_weather_data(city):
    """Unified data fetching"""
    curr_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    fore_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    
    try:
        curr_res = requests.get(curr_url).json()
        fore_res = requests.get(fore_url).json()
        
        if curr_res.get("cod") != 200:
            return None
            
        lat, lon = curr_res['coord']['lat'], curr_res['coord']['lon']
        
        # Air Pollution
        poll_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
        poll_res = requests.get(poll_url).json()
        
        return {
            "current": curr_res,
            "forecast": fore_res,
            "pollution": poll_res
        }
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# ------------------ ANALYTICS ENGINE ------------------
def process_forecast(forecast_data):
    """Convert raw forecast to meaningful pandas analysis"""
    rows = []
    for item in forecast_data['list']:
        rows.append({
            "timestamp": datetime.fromtimestamp(item['dt']),
            "temp": item['main']['temp'],
            "feels_like": item['main']['feels_like'],
            "humidity": item['main']['humidity'],
            "pressure": item['main']['pressure'],
            "wind_speed": item['wind']['speed'],
            "clouds": item['clouds']['all'],
            "weather": item['weather'][0]['main'],
            "description": item['weather'][0]['description']
        })
    df = pd.DataFrame(rows)
    df['date'] = df['timestamp'].dt.date
    df['hour'] = df['timestamp'].dt.hour
    return df

def get_aqi_label(aqi):
    labels = {
        1: ("Good", SUCCESS_COLOR),
        2: ("Fair", "#a3e635"),
        3: ("Moderate", WARNING_COLOR),
        4: ("Poor", "#fb923c"),
        5: ("Very Poor", ACCENT_COLOR)
    }
    return labels.get(aqi, ("Unknown", "#888"))

def generate_weather_alerts(cw, poll):
    """Generate weather alerts based on conditions"""
    alerts = []
    
    # Temperature alerts
    temp = cw['main']['temp']
    if temp > 35:
        alerts.append(("⚠️ Extreme Heat Warning", f"Temperature is {temp}°C. Stay hydrated and avoid outdoor activities.", "danger"))
    elif temp < 5:
        alerts.append(("❄️ Cold Weather Alert", f"Temperature is {temp}°C. Dress warmly and protect against frostbite.", "warning"))
    
    # Wind alerts
    wind_speed = cw['wind']['speed']
    if wind_speed > 15:
        alerts.append(("💨 High Wind Advisory", f"Wind speed is {wind_speed} m/s. Secure loose objects.", "warning"))
    
    # Humidity alerts
    humidity = cw['main']['humidity']
    if humidity > 85:
        alerts.append(("💧 High Humidity Alert", f"Humidity is {humidity}%. May feel uncomfortable.", "warning"))
    
    # Air quality alerts
    if poll:
        aqi = poll['main']['aqi']
        if aqi >= 4:
            alerts.append(("🏭 Poor Air Quality", "Air quality is poor. Limit outdoor exposure and wear a mask.", "danger"))
        elif aqi == 3:
            alerts.append(("🌫️ Moderate Air Quality", "Air quality is moderate. Sensitive groups should limit prolonged outdoor activities.", "warning"))
    
    return alerts

def generate_recommendations(cw, df, poll):
    """Generate personalized recommendations"""
    recommendations = []
    temp = cw['main']['temp']
    weather = cw['weather'][0]['main']
    
    # Clothing recommendations
    if temp > 25:
        recommendations.append(("👕 Clothing", "Light, breathable clothing recommended. Don't forget sunscreen!"))
    elif temp < 15:
        recommendations.append(("🧥 Clothing", "Warm layers recommended. Consider a jacket or coat."))
    else:
        recommendations.append(("👔 Clothing", "Comfortable casual wear. A light jacket might be useful."))
    
    # Activity recommendations
    if weather in ['Clear', 'Clouds'] and temp > 15 and temp < 30:
        recommendations.append(("🏃 Activities", "Perfect weather for outdoor activities! Great for jogging, cycling, or picnics."))
    elif weather == 'Rain':
        recommendations.append(("☔ Activities", "Indoor activities recommended. Carry an umbrella if going out."))
    
    # Best time to go out
    best_hour = df.loc[df['temp'].idxmax()]
    worst_hour = df.loc[df['temp'].idxmin()]
    recommendations.append((
        "⏰ Best Time", 
        f"Warmest at {best_hour['timestamp'].strftime('%I:%M %p')} ({best_hour['temp']:.1f}°C), "
        f"Coolest at {worst_hour['timestamp'].strftime('%I:%M %p')} ({worst_hour['temp']:.1f}°C)"
    ))
    
    return recommendations

# ------------------ SIDEBAR ------------------
with st.sidebar:
    try:
        st.image("Assets/meteorology.png", width=120)
    except:
        st.image("https://cdn-icons-png.flaticon.com/512/1146/1146869.png", width=80)
    
    st.markdown("### 🌍 Weather Analytics Dashboard")
    
    # Temperature Unit Toggle
    st.session_state.temp_unit = st.radio("🌡️ Temperature Unit", ["Celsius", "Fahrenheit"], horizontal=True)
    
    st.divider()
    
    # City Input
    city_input = st.text_input("📍 Search City", "Mumbai", placeholder="Enter city name...")
    
    # Quick city buttons
    st.markdown("**Quick Select:**")
    quick_cities = ["Mumbai", "Delhi", "New York", "London", "Tokyo", "Paris"]
    cols = st.columns(3)
    for idx, city in enumerate(quick_cities):
        with cols[idx % 3]:
            if st.button(city, key=f"quick_{city}", use_container_width=True):
                city_input = city
    
    st.divider()
    
    # Favorites
    st.markdown("⭐ **Favorite Cities**")
    if st.session_state.favorite_cities:
        for fav_city in st.session_state.favorite_cities:
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(f"📍 {fav_city}", key=f"fav_{fav_city}", use_container_width=True):
                    city_input = fav_city
            with col2:
                if st.button("❌", key=f"remove_{fav_city}"):
                    st.session_state.favorite_cities.remove(fav_city)
                    st.rerun()
    
    if city_input and city_input not in st.session_state.favorite_cities:
        if st.button("⭐ Add to Favorites", use_container_width=True):
            st.session_state.favorite_cities.append(city_input)
            st.rerun()
    
    st.divider()
    
    # Multi-city comparison
    st.markdown("🔄 **Compare Cities**")
    compare_mode = st.checkbox("Enable Comparison Mode")
    if compare_mode:
        compare_city = st.text_input("Add city to compare", placeholder="Enter another city...")
        if compare_city and st.button("Add to Comparison"):
            if compare_city not in st.session_state.compare_cities:
                st.session_state.compare_cities.append(compare_city)
                st.rerun()
        
        if st.session_state.compare_cities:
            st.write("Comparing:")
            for comp_city in st.session_state.compare_cities:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"• {comp_city}")
                with col2:
                    if st.button("🗑️", key=f"comp_remove_{comp_city}"):
                        st.session_state.compare_cities.remove(comp_city)
                        st.rerun()
            
            if st.button("🗑️ Clear All Comparison", use_container_width=True):
                st.session_state.compare_cities = []
                st.rerun()
    
    st.divider()
    st.info("🔍 System Status: Connected to OpenWeather API")
    
    # Search History
    if st.session_state.search_history:
        with st.expander("📜 Recent Searches"):
            for hist in st.session_state.search_history[-5:]:
                st.caption(f"• {hist}")

# ------------------ HEADER ------------------
st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

# Use Streamlit's native title for better visibility
st.title("🌦️ Weather Analytics Dashboard")
st.markdown(f"<p style='color:rgba(255,255,255,0.6); font-size:1.1rem; margin-top:-10px;'>Real-time Intelligence & Predictive Analysis • {datetime.now().strftime('%B %d, %Y')}</p>", unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

# ------------------ DATA FETCHING ------------------
if city_input:
    # Add to search history
    if city_input not in st.session_state.search_history:
        st.session_state.search_history.append(city_input)
    
    data = fetch_weather_data(city_input)
    
    if data:
        cw = data['current']
        df = process_forecast(data['forecast'])
        poll = data['pollution']['list'][0] if data['pollution'].get('list') else None
        
        # Temperature conversion
        temp_symbol = get_temp_symbol(st.session_state.temp_unit)
        current_temp = convert_temp(cw['main']['temp'], st.session_state.temp_unit)
        feels_like_temp = convert_temp(cw['main']['feels_like'], st.session_state.temp_unit)
        
        # ------------------ WEATHER ALERTS ------------------
        alerts = generate_weather_alerts(cw, poll)
        if alerts:
            st.markdown("### 🚨 Active Weather Alerts")
            # Display alerts in rows of max 3 columns for better alignment
            num_alerts = len(alerts)
            for i in range(0, num_alerts, 3):
                alert_cols = st.columns(min(3, num_alerts - i))
                for idx, (title, message, severity) in enumerate(alerts[i:i+3]):
                    with alert_cols[idx]:
                        st.markdown(f"""
                        <div class='alert-box alert-{severity}'>
                            <strong>{title}</strong><br>
                            <small>{message}</small>
                        </div>
                        """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
        
        st.divider()
        
        # ------------------ TOP KPI SECTION ------------------
        st.markdown(f"### 📊 Current Conditions - {city_input.title()}")
        st.markdown("<div style='margin: 15px 0;'></div>", unsafe_allow_html=True)
        
        # Wrapper container to prevent cutoff
        st.markdown("<div style='padding: 10px 0;'>", unsafe_allow_html=True)
        
        kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
        
        with kpi1:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='kpi-label'>Temperature</div>
                <div class='kpi-value'>{current_temp:.1f}{temp_symbol}</div>
                <div class='kpi-subtitle' style='color:{SUCCESS_COLOR};'>Feels like {feels_like_temp:.1f}{temp_symbol}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with kpi2:
            status, color = get_aqi_label(poll['main']['aqi']) if poll else ("N/A", "#888")
            st.markdown(f"""
            <div class='metric-card'>
                <div class='kpi-label'>Air Quality</div>
                <div class='kpi-value'>{poll['main']['aqi'] if poll else '--'}</div>
                <div class='status-badge' style='background:{color}; color:#000'>{status}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with kpi3:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='kpi-label'>Humidity</div>
                <div class='kpi-value'>{cw['main']['humidity']}%</div>
                <div class='kpi-subtitle' style='color:{THEME_COLOR};'>Pressure: {cw['main']['pressure']} hPa</div>
            </div>
            """, unsafe_allow_html=True)
            
        with kpi4:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='kpi-label'>Wind Speed</div>
                <div class='kpi-value'>{cw['wind']['speed']} <span style='font-size:0.9rem'>m/s</span></div>
                <div class='kpi-subtitle' style='color:rgba(255,255,255,0.5);'>Direction: {cw['wind'].get('deg', 'N/A')}°</div>
            </div>
            """, unsafe_allow_html=True)
            
        with kpi5:
            weather_emoji = '☀️' if cw['weather'][0]['main'] == 'Clear' else '☁️' if cw['weather'][0]['main'] == 'Clouds' else '🌧️' if cw['weather'][0]['main'] == 'Rain' else '⛈️' if cw['weather'][0]['main'] == 'Thunderstorm' else '🌫️' if cw['weather'][0]['main'] == 'Mist' else '🌦️'
            st.markdown(f"""
            <div class='metric-card'>
                <div class='kpi-label'>Conditions</div>
                <div style='font-size:1.8rem; line-height:1; margin:6px 0; text-align:center;'>{weather_emoji}</div>
                <div class='kpi-subtitle' style='color:rgba(255,255,255,0.7); text-align:center;'>{cw['weather'][0]['description'].title()}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)  # Close wrapper

        st.divider()
        
        # ------------------ RECOMMENDATIONS ------------------
        recommendations = generate_recommendations(cw, df, poll)
        if recommendations:
            st.markdown("### 💡 Smart Recommendations")
            # Always use 3 columns for consistent layout
            rec_cols = st.columns(3)
            for idx, (title, message) in enumerate(recommendations[:3]):  # Limit to 3 recommendations
                with rec_cols[idx]:
                    st.markdown(f"""
                    <div class='recommendation-card'>
                        <strong style='color:{THEME_COLOR}'>{title}</strong><br>
                        <small style='color:rgba(255,255,255,0.8)'>{message}</small>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.divider()
        st.markdown("<div style='margin: 10px 0;'></div>", unsafe_allow_html=True)

        # ------------------ MAIN TABS ------------------
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 Forecast Trends", 
            "🌬️ Air Quality", 
            "📊 Statistical Analysis", 
            "📄 Data Explorer",
            "🔄 City Comparison"
        ])

        with tab1:
            st.subheader("🔮 Predictive Time-Series Analysis")
            
            # Convert temperatures for display
            df_display = df.copy()
            df_display['temp'] = df_display['temp'].apply(lambda x: convert_temp(x, st.session_state.temp_unit))
            df_display['feels_like'] = df_display['feels_like'].apply(lambda x: convert_temp(x, st.session_state.temp_unit))
            
            # Interactive Plotly Chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_display['timestamp'], 
                y=df_display['temp'], 
                name="Temperature",
                line=dict(color=THEME_COLOR, width=3),
                fill='tozeroy', 
                fillcolor='rgba(0, 212, 255, 0.1)',
                hovertemplate=f'<b>Temp</b>: %{{y:.1f}}{temp_symbol}<br><b>Time</b>: %{{x}}<extra></extra>'
            ))
            fig.add_trace(go.Scatter(
                x=df_display['timestamp'], 
                y=df_display['feels_like'], 
                name="Feels Like",
                line=dict(color=ACCENT_COLOR, width=2, dash='dot'),
                hovertemplate=f'<b>Feels Like</b>: %{{y:.1f}}{temp_symbol}<br><b>Time</b>: %{{x}}<extra></extra>'
            ))
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=TEXT_PRIMARY),
                margin=dict(l=0, r=0, t=30, b=0),
                xaxis=dict(gridcolor='rgba(255,255,255,0.05)', title="Time"),
                yaxis=dict(gridcolor='rgba(255,255,255,0.05)', title=f"Temperature ({temp_symbol})"),
                hovermode='x unified',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Mini Insights
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("#### 📊 Temperature Stats")
                max_temp = convert_temp(df['temp'].max(), st.session_state.temp_unit)
                min_temp = convert_temp(df['temp'].min(), st.session_state.temp_unit)
                avg_temp = convert_temp(df['temp'].mean(), st.session_state.temp_unit)
                st.write(f"• Peak: **{max_temp:.1f}{temp_symbol}**")
                st.write(f"• Low: **{min_temp:.1f}{temp_symbol}**")
                st.write(f"• Average: **{avg_temp:.1f}{temp_symbol}**")
                st.write(f"• Range: **{(max_temp - min_temp):.1f}{temp_symbol}**")
            
            with c2:
                st.markdown("#### 🌡️ Comfort Index")
                avg_humidity = df['humidity'].mean()
                avg_wind = df['wind_speed'].mean()
                comfort_score = 100 - (abs(avg_temp - 22) * 2) - (abs(avg_humidity - 50) * 0.5)
                comfort_score = max(0, min(100, comfort_score))
                
                st.metric("Comfort Score", f"{comfort_score:.0f}/100")
                st.progress(comfort_score / 100)
                if comfort_score > 70:
                    st.success("Excellent conditions!")
                elif comfort_score > 50:
                    st.info("Moderate conditions")
                else:
                    st.warning("Challenging conditions")
            
            with c3:
                # Weather Condition Distribution
                cond_counts = df['weather'].value_counts()
                fig_pie = px.pie(
                    values=cond_counts.values, 
                    names=cond_counts.index, 
                    hole=0.5, 
                    color_discrete_sequence=px.colors.sequential.Blues
                )
                fig_pie.update_layout(
                    showlegend=True, 
                    margin=dict(l=0,r=0,t=30,b=0), 
                    height=250, 
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=TEXT_PRIMARY)
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            # Hourly breakdown - Cyber-Temporal Matrix
            st.markdown("#### ⏰ 24-Hour Predictive Breakdown")
            hourly_df = df_display.head(12)  # Show next 12 hours for cleaner mobile view
            
            hourly_fig = go.Figure()
            hourly_fig.add_trace(go.Bar(
                x=hourly_df['timestamp'].dt.strftime('%I %p'),
                y=hourly_df['temp'],
                marker=dict(
                    color=hourly_df['temp'],
                    colorscale=[[0, THEME_COLOR], [1, ACCENT_COLOR]],
                    line=dict(color='rgba(255,255,255,0.2)', width=1)
                ),
                text=hourly_df['temp'].apply(lambda x: f"{x:.1f}°"),
                textposition='outside',
                hovertemplate="<b>%{x}</b><br>Temperature: %{y:.1f}" + temp_symbol + "<extra></extra>"
            ))
            
            hourly_fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=TEXT_PRIMARY),
                margin=dict(l=0, r=0, t=30, b=0),
                height=300,
                xaxis=dict(
                    gridcolor='rgba(255,255,255,0.05)', 
                    title="<b>TIMELINE</b>", 
                    titlefont=dict(size=10),
                    tickangle=0
                ),
                yaxis=dict(
                    gridcolor='rgba(255,255,255,0.05)', 
                    title=f"<b>TEMP ({temp_symbol})</b>", 
                    titlefont=dict(size=10),
                    showticklabels=False # Use text labels on bars instead
                ),
                showlegend=False
            )
            st.plotly_chart(hourly_fig, use_container_width=True)

        with tab2:
            st.subheader("🏭 Pollutant Concentration Analysis")
            if poll:
                comp = poll['components']
                poll_df = pd.DataFrame({
                    "Pollutant": ["CO", "NO₂", "O₃", "SO₂", "PM2.5", "PM10"],
                    "Concentration (μg/m³)": [
                        comp.get('co', 0), 
                        comp.get('no2', 0), 
                        comp.get('o3', 0), 
                        comp.get('so2', 0), 
                        comp.get('pm2_5', 0), 
                        comp.get('pm10', 0)
                    ],
                    "Safe Limit": [10000, 200, 180, 350, 25, 50]  # WHO guidelines (approximate)
                })
                
                col_p1, col_p2 = st.columns([2, 1])
                with col_p1:
                    fig_pol = go.Figure()
                    fig_pol.add_trace(go.Bar(
                        x=poll_df["Pollutant"],
                        y=poll_df["Concentration (μg/m³)"],
                        name="Current Level",
                        marker_color=THEME_COLOR
                    ))
                    fig_pol.add_trace(go.Scatter(
                        x=poll_df["Pollutant"],
                        y=poll_df["Safe Limit"],
                        name="Safe Limit",
                        mode='lines+markers',
                        line=dict(color=ACCENT_COLOR, dash='dash', width=2)
                    ))
                    fig_pol.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color=TEXT_PRIMARY),
                        yaxis=dict(title="Concentration (μg/m³)", gridcolor='rgba(255,255,255,0.05)'),
                        xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    st.plotly_chart(fig_pol, use_container_width=True)
                
                with col_p2:
                    st.markdown("#### 🎯 AQI Breakdown")
                    aqi_score = poll['main']['aqi']
                    st.metric("AQI Level", f"{aqi_score}/5")
                    st.progress(aqi_score / 5.0)
                    
                    status, color = get_aqi_label(aqi_score)
                    st.markdown(f"**Status:** <span style='color:{color}'>{status}</span>", unsafe_allow_html=True)
                    
                    st.markdown("#### 📋 Health Recommendations")
                    if aqi_score <= 2:
                        st.success("✅ Air quality is good. Enjoy outdoor activities!")
                    elif aqi_score == 3:
                        st.warning("⚠️ Sensitive groups should limit prolonged outdoor exposure.")
                    else:
                        st.error("🚨 Everyone should reduce outdoor activities. Wear a mask if going out.")
                
                # Pollutant details table
                st.markdown("#### 📊 Detailed Pollutant Analysis")
                poll_df['Status'] = poll_df.apply(
                    lambda row: '✅ Safe' if row['Concentration (μg/m³)'] < row['Safe Limit'] else '⚠️ Elevated',
                    axis=1
                )
                st.dataframe(poll_df, use_container_width=True)
            else:
                st.info("Air quality data not available for this location.")

        with tab3:
            st.subheader("📊 Statistical Variable Distributions")
            
            col_s1, col_s2 = st.columns(2)
            
            with col_s1:
                # Correlation Matrix - Futuristic HUD Style
                st.markdown("#### 🔗 Variable Correlations")
                corr_data = df[['temp', 'humidity', 'pressure', 'wind_speed']].corr()
                fig_corr = px.imshow(
                    corr_data,
                    text_auto='.2f',
                    color_continuous_scale=[[0, '#ff0055'], [0.5, '#1a1f3a'], [1, '#00d4ff']],
                    labels=dict(color="Correlation"),
                    x=['TEMP', 'HUMIDITY', 'PRESSURE', 'WIND'],
                    y=['TEMP', 'HUMIDITY', 'PRESSURE', 'WIND']
                )
                fig_corr.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=TEXT_PRIMARY, family="Inter, sans-serif"),
                    margin=dict(l=0, r=0, t=20, b=0),
                    height=350,
                    xaxis=dict(side="bottom", gridcolor='rgba(255,255,255,0.05)', tickfont=dict(size=10)),
                    yaxis=dict(gridcolor='rgba(255,255,255,0.05)', tickfont=dict(size=10)),
                    coloraxis_showscale=True,
                    coloraxis_colorbar=dict(
                        title="CORR",
                        tickfont=dict(size=9),
                        thickness=15,
                        len=0.7,
                        yanchor="middle",
                        y=0.5
                    )
                )
                st.plotly_chart(fig_corr, use_container_width=True)
                
                # Scatter plot - Glow Density Style
                st.markdown("#### 🎯 Humidity vs Temperature")
                fig_scatter = px.scatter(
                    df, 
                    x="humidity", 
                    y="temp", 
                    size="wind_speed", 
                    color="temp",
                    color_continuous_scale=[[0, '#00d4ff'], [1, '#ff6b9d']],
                    render_mode='svg'
                )
                fig_scatter.update_traces(
                    marker=dict(line=dict(width=1, color='rgba(255,255,255,0.3)'), opacity=0.8),
                    selector=dict(mode='markers')
                )
                fig_scatter.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,10,20,0.3)',
                    font=dict(color=TEXT_PRIMARY),
                    margin=dict(l=0, r=0, t=30, b=0),
                    height=350,
                    xaxis=dict(gridcolor='rgba(255,255,255,0.05)', title="<b>HUMIDITY (%)</b>", titlefont=dict(size=10)),
                    yaxis=dict(gridcolor='rgba(255,255,255,0.05)', title="<b>TEMP (°C)</b>", titlefont=dict(size=10)),
                    coloraxis_showscale=True,
                    coloraxis_colorbar=dict(
                        title="TEMP",
                        tickfont=dict(size=9),
                        thickness=15,
                        len=0.7,
                        yanchor="middle",
                        y=0.5
                    )
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
            
            with col_s2:
                # Wind Speed Distribution - Cyber Gradient Style
                st.markdown("#### 💨 Wind Speed Distribution")
                fig_wind = px.histogram(
                    df, 
                    x="wind_speed", 
                    nbins=15,
                    color_discrete_sequence=['#00ff88'],
                    opacity=0.7
                )
                fig_wind.update_traces(
                    marker=dict(
                        line=dict(width=1.5, color='#00ff88'),
                        color='#00ff88'
                    )
                )
                fig_wind.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,255,136,0.03)',
                    font=dict(color=TEXT_PRIMARY),
                    margin=dict(l=0, r=0, t=20, b=0),
                    height=350,
                    xaxis=dict(gridcolor='rgba(255,255,255,0.05)', title="<b>WIND VELOCITY (m/s)</b>", titlefont=dict(size=10)),
                    yaxis=dict(gridcolor='rgba(255,255,255,0.05)', title="<b>DENSITY</b>", titlefont=dict(size=10))
                )
                st.plotly_chart(fig_wind, use_container_width=True)
                
                # Pressure trend - Neon Spline Area
                st.markdown("#### 📉 Pressure Trend")
                fig_pressure = go.Figure()
                fig_pressure.add_trace(go.Scatter(
                    x=df['timestamp'],
                    y=df['pressure'],
                    mode='lines+markers',
                    line=dict(color=SUCCESS_COLOR, width=3, shape='spline'),
                    fill='tozeroy',
                    fillcolor='rgba(0, 255, 136, 0.1)',
                    marker=dict(size=6, color='#ffffff', line=dict(color=SUCCESS_COLOR, width=2)),
                    name="Atmospheric Pressure"
                ))
                fig_pressure.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=TEXT_PRIMARY),
                    margin=dict(l=0, r=0, t=30, b=0),
                    height=350,
                    xaxis=dict(gridcolor='rgba(255,255,255,0.05)', title="<b>TIMELINE</b>", titlefont=dict(size=10)),
                    yaxis=dict(gridcolor='rgba(255,255,255,0.05)', title="<b>PRESSURE (hPa)</b>", titlefont=dict(size=10), range=[df['pressure'].min()-5, df['pressure'].max()+5])
                )
                st.plotly_chart(fig_pressure, use_container_width=True)

        with tab4:
            st.subheader("🗂️ Forecast Data Explorer")
            
            # Filters
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                search_query = st.text_input("🔍 Filter by description", placeholder="e.g., 'cloudy', 'rain'")
            with col_f2:
                temp_filter = st.slider(f"Temperature Range ({temp_symbol})", 
                                       float(convert_temp(df['temp'].min(), st.session_state.temp_unit)), 
                                       float(convert_temp(df['temp'].max(), st.session_state.temp_unit)),
                                       (float(convert_temp(df['temp'].min(), st.session_state.temp_unit)), 
                                        float(convert_temp(df['temp'].max(), st.session_state.temp_unit))))
            with col_f3:
                weather_filter = st.multiselect("Weather Type", df['weather'].unique(), default=df['weather'].unique())
            
            # Apply filters
            display_df = df.copy()
            display_df['temp'] = display_df['temp'].apply(lambda x: convert_temp(x, st.session_state.temp_unit))
            display_df['feels_like'] = display_df['feels_like'].apply(lambda x: convert_temp(x, st.session_state.temp_unit))
            
            if search_query:
                display_df = display_df[display_df['description'].str.contains(search_query, case=False, na=False)]
            
            display_df = display_df[
                (display_df['temp'] >= temp_filter[0]) & 
                (display_df['temp'] <= temp_filter[1]) &
                (display_df['weather'].isin(weather_filter))
            ]
            
            # Display styled dataframe
            st.markdown(f"**Showing {len(display_df)} of {len(df)} records**")
            st.dataframe(
                display_df.style.background_gradient(subset=['temp', 'humidity'], cmap='Blues'),
                use_container_width=True,
                height=400
            )
            
            # Export Section
            st.divider()
            col_e1, col_e2, col_e3 = st.columns(3)
            with col_e1:
                csv = display_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f'weather_analysis_{city_input}_{datetime.now().strftime("%Y%m%d")}.csv',
                    mime='text/csv',
                )
            with col_e2:
                json_data = display_df.to_json(orient='records', date_format='iso')
                st.download_button(
                    label="📥 Download JSON",
                    data=json_data,
                    file_name=f'weather_analysis_{city_input}_{datetime.now().strftime("%Y%m%d")}.json',
                    mime='application/json',
                )
            with col_e3:
                st.markdown("#### 📊 Dataset Info")
                st.write(f"• Total Records: {len(display_df)}")
                st.write(f"• Time Span: {(df['timestamp'].max() - df['timestamp'].min()).days} days")
                st.write(f"• Variables: {len(display_df.columns)}")

        with tab5:
            st.subheader("🔄 Multi-City Comparison")
            
            if compare_mode and st.session_state.compare_cities:
                comparison_data = []
                
                # Fetch data for all cities
                for comp_city in [city_input] + st.session_state.compare_cities:
                    comp_data = fetch_weather_data(comp_city)
                    if comp_data:
                        comp_cw = comp_data['current']
                        comp_poll = comp_data['pollution']['list'][0] if comp_data['pollution'].get('list') else None
                        
                        comparison_data.append({
                            'City': comp_city.title(),
                            'Temperature': convert_temp(comp_cw['main']['temp'], st.session_state.temp_unit),
                            'Feels Like': convert_temp(comp_cw['main']['feels_like'], st.session_state.temp_unit),
                            'Humidity': comp_cw['main']['humidity'],
                            'Pressure': comp_cw['main']['pressure'],
                            'Wind Speed': comp_cw['wind']['speed'],
                            'AQI': comp_poll['main']['aqi'] if comp_poll else None,
                            'Weather': comp_cw['weather'][0]['main']
                        })
                
                if comparison_data:
                    comp_df = pd.DataFrame(comparison_data)
                    
                    # Temperature comparison
                    col_c1, col_c2 = st.columns(2)
                    with col_c1:
                        fig_comp_temp = px.bar(
                            comp_df,
                            x='City',
                            y='Temperature',
                            color='Temperature',
                            color_continuous_scale='thermal',
                            title=f'Temperature Comparison ({temp_symbol})'
                        )
                        fig_comp_temp.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(color=TEXT_PRIMARY)
                        )
                        st.plotly_chart(fig_comp_temp, use_container_width=True)
                    
                    with col_c2:
                        fig_comp_aqi = px.bar(
                            comp_df,
                            x='City',
                            y='AQI',
                            color='AQI',
                            color_continuous_scale='reds',
                            title='Air Quality Index Comparison'
                        )
                        fig_comp_aqi.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(color=TEXT_PRIMARY)
                        )
                        st.plotly_chart(fig_comp_aqi, use_container_width=True)
                    
                    # Radar chart for multi-dimensional comparison
                    st.markdown("#### 🎯 Multi-Dimensional Environmental Profile")
                    
                    # Absolute normalization for meaningful comparison
                    radar_df = comp_df.copy()
                    
                    # Define professional ranges for normalization
                    ranges = {
                        'Temperature': (0, 50) if st.session_state.temp_unit == "Celsius" else (32, 122),
                        'Humidity': (0, 100),
                        'Pressure': (950, 1050),
                        'Wind Speed': (0, 20),
                        'AQI': (1, 5)
                    }
                    
                    for col, (min_val, max_val) in ranges.items():
                        if col in radar_df.columns:
                            # Clamp values to ranges and normalize to 0-100
                            vals = radar_df[col].clip(min_val, max_val)
                            radar_df[f'{col}_norm'] = (vals - min_val) / (max_val - min_val) * 100
                    
                    fig_radar = go.Figure()
                    
                    # Professional Color Palette for multiple cities
                    colors = [THEME_COLOR, ACCENT_COLOR, SUCCESS_COLOR, '#FF00A0', '#FFD700']
                    
                    categories = ['Temperature', 'Humidity', 'Pressure', 'Wind Speed', 'Air Quality (AQI)']
                    
                    for idx, row in radar_df.iterrows():
                        # Close the circle by repeating the first value
                        r_values = [
                            row.get('Temperature_norm', 0), 
                            row.get('Humidity_norm', 0), 
                            row.get('Pressure_norm', 0), 
                            row.get('Wind Speed_norm', 0),
                            row.get('AQI_norm', 0) if pd.notnull(row.get('AQI_norm')) else 0
                        ]
                        r_values.append(r_values[0])
                        theta_values = categories + [categories[0]]
                        
                        fig_radar.add_trace(go.Scatterpolar(
                            r=r_values,
                            theta=theta_values,
                            fill='toself',
                            name=row['City'],
                            line=dict(color=colors[idx % len(colors)], width=2),
                            fillcolor=f"rgba{tuple(list(int(colors[idx % len(colors)].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + [0.15])}",
                            marker=dict(size=8)
                        ))
                    
                    fig_radar.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True, 
                                range=[0, 100],
                                showticklabels=False,
                                gridcolor='rgba(255,255,255,0.1)',
                                linecolor='rgba(255,255,255,0.1)'
                            ),
                            angularaxis=dict(
                                gridcolor='rgba(255,255,255,0.1)',
                                linecolor='rgba(255,255,255,0.1)',
                                tickfont=dict(size=11)
                            ),
                            bgcolor='rgba(0,0,0,0)'
                        ),
                        showlegend=True,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=-0.2,
                            xanchor="center",
                            x=0.5
                        ),
                        margin=dict(l=40, r=40, t=40, b=40),
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color=TEXT_PRIMARY, size=12)
                    )
                    st.plotly_chart(fig_radar, use_container_width=True)
                    
                    # Comparison table
                    st.markdown("#### 📋 Detailed Comparison Matrix")
                    styled_comp = comp_df.style.format({
                        'Temperature': '{:.1f}' + temp_symbol,
                        'Feels Like': '{:.1f}' + temp_symbol,
                        'Humidity': '{:.0f}%',
                        'Pressure': '{:.0f} hPa',
                        'Wind Speed': '{:.1f} m/s',
                        'AQI': '{:.0f}'
                    }).background_gradient(subset=['Temperature', 'Humidity', 'AQI'], cmap='Blues')
                    
                    st.dataframe(styled_comp, use_container_width=True)
                    
                    # Download Feature for Comparison Data
                    st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
                    c_col1, c_col2, c_col3 = st.columns([1, 1, 2])
                    with c_col1:
                        csv_comp = comp_df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Export CSV",
                            data=csv_comp,
                            file_name=f'city_comparison_{datetime.now().strftime("%Y%m%d")}.csv',
                            mime='text/csv',
                            use_container_width=True
                        )
                    with c_col2:
                        json_comp = comp_df.to_json(orient='records')
                        st.download_button(
                            label="📥 Export JSON",
                            data=json_comp,
                            file_name=f'city_comparison_{datetime.now().strftime("%Y%m%d")}.json',
                            mime='application/json',
                            use_container_width=True
                        )
                else:
                    st.warning("Unable to fetch data for comparison cities.")
            else:
                st.info("👆 Enable 'Comparison Mode' in the sidebar and add cities to compare weather conditions across multiple locations.")
                
                # Show example
                st.markdown("""
                ### How to use City Comparison:
                1. ✅ Check **"Enable Comparison Mode"** in the sidebar
                2. 📝 Enter a city name in the comparison input
                3. ➕ Click **"Add to Comparison"**
                4. 🔄 Repeat for multiple cities
                5. 📊 View side-by-side comparisons here!
                """)

    else:
        st.error("⚠️ City not found! Please check the spelling and try again.")
        st.info("💡 Try searching for major cities like: Mumbai, Delhi, New York, London, Tokyo, Paris")
else:
    # ------------------ LANDING PAGE ------------------
    st.markdown(f"""
        <div class='landing-hero'>
            <div style='font-size: 0.8rem; color: {THEME_COLOR}; font-weight: 700; text-transform: uppercase; letter-spacing: 3px; margin-bottom: 15px;'>
                Scientific Observation Platform
            </div>
            <h1 style='font-size: 3.5rem; font-weight: 800; margin-bottom: 20px; line-height: 1.1;'>
                Meteorological <span style='color: {THEME_COLOR};'>Intelligence</span> Hub
            </h1>
            <p style='font-size: 1.2rem; color: rgba(255,255,255,0.6); max-width: 800px; margin: 0 auto 30px auto;'>
                Access high-precision atmospheric data, predictive environmental modeling, and 
                air quality intelligence for professional-grade meteorological analysis.
            </p>
            <div class='cta-text animate-pulse'>
                ← ENTER A CITY IN THE SIDEBAR TO BEGIN ANALYSIS
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        st.markdown(f"""
            <div class='feature-card'>
                <div style='font-size: 2rem; margin-bottom: 15px;'>📡</div>
                <h4 style='color: {THEME_COLOR}; margin-bottom: 10px;'>Real-time Tracking</h4>
                <p style='font-size: 0.9rem; color: rgba(255,255,255,0.5);'>
                    Live atmospheric monitoring across 200,000+ cities with enterprise-grade data accuracy.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
    with col_f2:
        st.markdown(f"""
            <div class='feature-card'>
                <div style='font-size: 2rem; margin-bottom: 15px;'>📈</div>
                <h4 style='color: {THEME_COLOR}; margin-bottom: 10px;'>Predictive Analysis</h4>
                <p style='font-size: 0.9rem; color: rgba(255,255,255,0.5);'>
                    Advanced time-series forecasting and statistical distributions of environmental variables.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
    with col_f3:
        st.markdown(f"""
            <div class='feature-card'>
                <div style='font-size: 2rem; margin-bottom: 15px;'>🌫️</div>
                <h4 style='color: {THEME_COLOR}; margin-bottom: 10px;'>AQI Intelligence</h4>
                <p style='font-size: 0.9rem; color: rgba(255,255,255,0.5);'>
                    Deep pollution profiling including concentration metrics for all major atmospheric pollutants.
                </p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

# ------------------ FOOTER ------------------
st.markdown("<div style='margin-top: 80px;'></div>", unsafe_allow_html=True)
st.markdown("<div style='border-top: 1px solid rgba(255,255,255,0.1); padding-top: 30px;'></div>", unsafe_allow_html=True)

# Minimal Professional Footer
st.markdown(f"""
    <div style='text-align: center;'>
        <div style='font-size: 1.2rem; font-weight: 800; background: linear-gradient(135deg, {THEME_COLOR} 0%, {ACCENT_COLOR} 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px;'>
            METEOROLOGY ANALYTICS DASHBOARD
        </div>
        <div style='display: flex; justify-content: center; gap: 20px; margin-bottom: 15px; color: rgba(255,255,255,0.6); font-size: 0.85rem;'>
            <span>📊 Enterprise Data</span>
            <span>•</span>
            <span>🛡️ Secure Connection</span>
            <span>•</span>
            <span>⚡ Real-time Processing</span>
        </div>
        <div style='color: rgba(255,255,255,0.4); font-size: 0.75rem; max-width: 600px; margin: 0 auto 20px auto; line-height: 1.6;'>
            A high-performance meteorological observation platform providing precision data analytics, 
            environmental charting, and predictive atmospheric insights for professional researchers and analysts.
        </div>
        <div style='background: rgba(255,255,255,0.03); border-radius: 50px; display: inline-flex; align-items: center; padding: 5px 20px; gap: 15px; border: 1px solid rgba(255,255,255,0.05);'>
            <div style='display: flex; align-items: center; gap: 5px;'>
                <div style='width: 8px; height: 8px; background: {SUCCESS_COLOR}; border-radius: 50%;'></div>
                <span style='font-size: 0.7rem; color: rgba(255,255,255,0.7);'>API STATUS: OPTIMAL</span>
            </div>
            <div style='width: 1px; height: 12px; background: rgba(255,255,255,0.1);'></div>
            <span style='font-size: 0.7rem; color: rgba(255,255,255,0.5);'>VERSION 2.1.4</span>
            <div style='width: 1px; height: 12px; background: rgba(255,255,255,0.1);'></div>
            <span style='font-size: 0.7rem; color: rgba(255,255,255,0.5);'>{datetime.now().strftime("%Y")} PRECISION METRICS</span>
        </div>
    </div>
    <div style='margin-bottom: 40px;'></div>
""", unsafe_allow_html=True)
