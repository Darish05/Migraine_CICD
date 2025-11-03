import streamlit as st
import requests
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="Migraine Prediction System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    .prediction-box {
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .high-risk {
        background-color: #ffebee;
        border-left: 5px solid #f44336;
    }
    .low-risk {
        background-color: #e8f5e9;
        border-left: 5px solid #4caf50;
    }
    </style>
""", unsafe_allow_html=True)

# API endpoint - configurable via environment variable
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Title and description
st.title("🏥 Migraine Prediction System")
st.markdown("### AI-Powered Migraine Risk Assessment & Severity Prediction")
st.markdown("---")

# Sidebar for navigation
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/brain.png", width=100)
    st.title("Navigation")
    page = st.radio("Select Page", ["🔮 Prediction", "📊 Models Info", "ℹ️ About"])
    
    st.markdown("---")
    st.markdown("### System Status")
    
    # Check API health
    try:
        health_response = requests.get(f"{API_URL}/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            st.success("✅ API Online")
            if health_data.get("models_loaded"):
                st.success("✅ Models Loaded")
            else:
                st.warning("⚠️ Models Not Loaded")
        else:
            st.error("❌ API Error")
    except:
        st.error("❌ API Offline")
        st.info("Make sure Docker containers are running")

# Page: Prediction
if page == "🔮 Prediction":
    st.header("Patient Information & Risk Assessment")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("👤 Demographics")
        age = st.slider("Age", 10, 100, 30)
        gender = st.selectbox("Gender", ["Male", "Female"])
        gender_val = 1 if gender == "Female" else 0
    
    with col2:
        st.subheader("💤 Sleep & Lifestyle")
        sleep_hours = st.slider("Sleep Hours", 0.0, 24.0, 7.0, 0.5)
        sleep_quality = st.slider("Sleep Quality (1-10)", 1, 10, 7)
        exercise = st.slider("Exercise Days/Week", 0, 7, 3)
        screen_time = st.slider("Screen Time (hours/day)", 0.0, 24.0, 6.0, 0.5)
    
    with col3:
        st.subheader("🧘 Stress & Habits")
        stress_level = st.slider("Stress Level (1-10)", 1, 10, 5)
        hydration = st.slider("Hydration Level (0-10)", 0, 10, 5)
        caffeine_intake = st.slider("Caffeine Intake (0-10)", 0, 10, 3)
        alcohol_intake = st.slider("Alcohol Intake (0-10)", 0, 10, 2)
    
    st.markdown("---")
    
    col4, col5 = st.columns(2)
    
    with col4:
        st.subheader("🌡️ Environmental Triggers")
        weather_changes = st.checkbox("Recent Weather Changes")
        bright_light = st.checkbox("Exposed to Bright Lights")
        loud_noises = st.checkbox("Exposed to Loud Noises")
        strong_smells = st.checkbox("Exposed to Strong Smells")
        
        st.subheader("🌤️ Weather Conditions")
        weather_pressure = st.number_input("Atmospheric Pressure (hPa)", 950.0, 1050.0, 1013.0, 0.1)
        humidity = st.slider("Humidity (%)", 0.0, 100.0, 50.0, 1.0)
        temperature_change = st.slider("Temperature Change (°C)", -20.0, 20.0, 0.0, 0.5)
    
    with col5:
        st.subheader("🍽️ Dietary & Physical Triggers")
        missed_meals = st.checkbox("Missed Meals")
        specific_foods = st.checkbox("Consumed Trigger Foods")
        dehydration = st.checkbox("Dehydrated")
        
        st.subheader("💪 Physical Factors")
        physical_activity = st.checkbox("Intense Physical Activity")
        neck_pain = st.checkbox("Neck Pain")
        menstrual_cycle = st.checkbox("Menstrual Cycle (if applicable)")
    
    st.markdown("---")
    
    # Prediction button
    if st.button("🔮 Predict Migraine Risk", type="primary", use_container_width=True):
        # Prepare input data
        patient_data = {
            "age": age,
            "gender": gender_val,
            "sleep_hours": sleep_hours,
            "sleep_quality": sleep_quality,
            "stress_level": stress_level,
            "hydration": hydration,
            "exercise": exercise,
            "screen_time": screen_time,
            "caffeine_intake": caffeine_intake,
            "alcohol_intake": alcohol_intake,
            "weather_changes": int(weather_changes),
            "menstrual_cycle": int(menstrual_cycle),
            "dehydration": int(dehydration),
            "bright_light": int(bright_light),
            "loud_noises": int(loud_noises),
            "strong_smells": int(strong_smells),
            "missed_meals": int(missed_meals),
            "specific_foods": int(specific_foods),
            "physical_activity": int(physical_activity),
            "neck_pain": int(neck_pain),
            "weather_pressure": weather_pressure,
            "humidity": humidity,
            "temperature_change": temperature_change
        }
        
        # Make API request
        with st.spinner("Analyzing patient data..."):
            try:
                response = requests.post(f"{API_URL}/predict", json=patient_data, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    predictions = result.get("predictions", {})
                    
                    st.success("✅ Prediction Complete!")
                    
                    # Display results
                    st.markdown("### 📊 Prediction Results")
                    
                    # Classification Results
                    st.markdown("#### 🎯 Migraine Occurrence Prediction")
                    
                    col_pred1, col_pred2 = st.columns(2)
                    
                    with col_pred1:
                        class_pred = predictions.get("classification_predictions", {})
                        model1 = class_pred.get("model_1", {})
                        
                        st.markdown("##### Model 1 (Top Performer)")
                        migraine_prob = model1.get("probabilities", [0, 0])[1] * 100
                        prediction = model1.get("prediction", 0)
                        
                        # Gauge chart for probability
                        fig = go.Figure(go.Indicator(
                            mode="gauge+number+delta",
                            value=migraine_prob,
                            domain={'x': [0, 1], 'y': [0, 1]},
                            title={'text': "Migraine Risk %"},
                            gauge={
                                'axis': {'range': [None, 100]},
                                'bar': {'color': "darkred" if migraine_prob > 50 else "green"},
                                'steps': [
                                    {'range': [0, 33], 'color': "lightgreen"},
                                    {'range': [33, 66], 'color': "yellow"},
                                    {'range': [66, 100], 'color': "lightcoral"}
                                ],
                                'threshold': {
                                    'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75,
                                    'value': 50
                                }
                            }
                        ))
                        fig.update_layout(height=250)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        if prediction == 1:
                            st.error(f"⚠️ **HIGH RISK**: {migraine_prob:.1f}% probability of migraine")
                        else:
                            st.success(f"✅ **LOW RISK**: {100-migraine_prob:.1f}% probability of NO migraine")
                    
                    with col_pred2:
                        model2 = class_pred.get("model_2", {})
                        
                        st.markdown("##### Model 2 (Backup)")
                        migraine_prob2 = model2.get("probabilities", [0, 0])[1] * 100
                        prediction2 = model2.get("prediction", 0)
                        
                        # Gauge chart for probability
                        fig2 = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=migraine_prob2,
                            domain={'x': [0, 1], 'y': [0, 1]},
                            title={'text': "Migraine Risk %"},
                            gauge={
                                'axis': {'range': [None, 100]},
                                'bar': {'color': "darkred" if migraine_prob2 > 50 else "green"},
                                'steps': [
                                    {'range': [0, 33], 'color': "lightgreen"},
                                    {'range': [33, 66], 'color': "yellow"},
                                    {'range': [66, 100], 'color': "lightcoral"}
                                ]
                            }
                        ))
                        fig2.update_layout(height=250)
                        st.plotly_chart(fig2, use_container_width=True)
                        
                        if prediction2 == 1:
                            st.error(f"⚠️ **HIGH RISK**: {migraine_prob2:.1f}%")
                        else:
                            st.success(f"✅ **LOW RISK**: {100-migraine_prob2:.1f}%")
                    
                    # Regression Results
                    st.markdown("#### 📈 Severity Prediction (if migraine occurs)")
                    
                    col_sev1, col_sev2 = st.columns(2)
                    
                    reg_pred = predictions.get("regression_predictions", {})
                    
                    with col_sev1:
                        severity1 = reg_pred.get("model_1", {}).get("severity", 0)
                        st.metric("Model 1 - Predicted Severity", f"{severity1:.2f}/10")
                        
                        # Progress bar
                        st.progress(min(severity1/10, 1.0))
                        
                        if severity1 < 3:
                            st.info("🟢 Mild severity expected")
                        elif severity1 < 7:
                            st.warning("🟡 Moderate severity expected")
                        else:
                            st.error("🔴 Severe migraine expected")
                    
                    with col_sev2:
                        severity2 = reg_pred.get("model_2", {}).get("severity", 0)
                        st.metric("Model 2 - Predicted Severity", f"{severity2:.2f}/10")
                        
                        # Progress bar
                        st.progress(min(severity2/10, 1.0))
                        
                        if severity2 < 3:
                            st.info("🟢 Mild severity expected")
                        elif severity2 < 7:
                            st.warning("🟡 Moderate severity expected")
                        else:
                            st.error("🔴 Severe migraine expected")
                    
                    # Recommendations
                    st.markdown("---")
                    st.markdown("### 💡 Recommendations")
                    
                    recommendations = []
                    
                    if sleep_hours < 7:
                        recommendations.append("😴 Increase sleep duration to 7-9 hours")
                    if sleep_quality < 5:
                        recommendations.append("🛏️ Improve sleep quality through better sleep hygiene")
                    if stress_level > 7:
                        recommendations.append("🧘 Practice stress reduction techniques (meditation, yoga)")
                    if hydration < 5:
                        recommendations.append("💧 Increase water intake to stay hydrated")
                    if exercise < 3:
                        recommendations.append("🏃 Increase physical activity to 3-5 days per week")
                    if screen_time > 8:
                        recommendations.append("📱 Reduce screen time and take regular breaks")
                    if caffeine_intake > 5:
                        recommendations.append("☕ Reduce caffeine consumption")
                    if missed_meals:
                        recommendations.append("🍽️ Maintain regular meal schedule")
                    if dehydration:
                        recommendations.append("💦 Address dehydration immediately")
                    
                    if recommendations:
                        for rec in recommendations:
                            st.info(rec)
                    else:
                        st.success("✅ Your lifestyle factors look good! Keep up the healthy habits.")
                    
                    # Export results
                    st.markdown("---")
                    
                    # Prepare export data
                    export_data = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "patient_data": patient_data,
                        "predictions": predictions,
                        "recommendations": recommendations
                    }
                    
                    st.download_button(
                        label="📥 Download Report (JSON)",
                        data=json.dumps(export_data, indent=2),
                        file_name=f"migraine_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                    
                else:
                    st.error(f"❌ Prediction failed: {response.status_code}")
                    st.error(response.text)
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Make sure Docker containers are running.")
                st.code("sudo docker-compose up -d")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Page: Models Info
elif page == "📊 Models Info":
    st.header("Model Performance Information")
    
    try:
        response = requests.get(f"{API_URL}/models-info", timeout=5)
        
        if response.status_code == 200:
            models_info = response.json()
            
            # Classification Models
            st.subheader("🎯 Classification Models (Migraine Occurrence)")
            class_models = models_info.get("classification", {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Top Model 1")
                model1 = class_models.get("top_model_1", {})
                st.json(model1)
            
            with col2:
                st.markdown("#### Top Model 2")
                model2 = class_models.get("top_model_2", {})
                st.json(model2)
            
            # Regression Models
            st.markdown("---")
            st.subheader("📈 Regression Models (Severity Prediction)")
            reg_models = models_info.get("regression", {})
            
            col3, col4 = st.columns(2)
            
            with col3:
                st.markdown("#### Top Model 1")
                reg_model1 = reg_models.get("top_model_1", {})
                st.json(reg_model1)
            
            with col4:
                st.markdown("#### Top Model 2")
                reg_model2 = reg_models.get("top_model_2", {})
                st.json(reg_model2)
            
        else:
            st.error("Failed to fetch model information")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Page: About
elif page == "ℹ️ About":
    st.header("About Migraine Prediction System")
    
    st.markdown("""
    ### 🏥 System Overview
    
    This AI-powered system predicts migraine occurrence and severity using machine learning models
    trained on various lifestyle, environmental, and physiological factors.
    
    ### 🎯 Features
    
    - **Dual Prediction Models**: Uses top 2 performing models for both classification and regression
    - **Classification**: Predicts whether a migraine will occur (Yes/No with probability)
    - **Regression**: Predicts severity level (0-10 scale)
    - **Real-time Analysis**: Instant predictions based on current patient data
    - **Personalized Recommendations**: Actionable advice based on risk factors
    
    ### 📊 Model Types
    
    The system uses ensemble of multiple algorithms including:
    - Random Forest
    - XGBoost
    - LightGBM
    - Gradient Boosting
    - Logistic Regression / Ridge Regression
    - Support Vector Machines
    - K-Nearest Neighbors
    - AdaBoost
    
    ### 🔬 Input Features
    
    **Demographics**: Age, Gender
    
    **Lifestyle Factors**:
    - Sleep hours and quality
    - Exercise frequency
    - Screen time
    - Stress levels
    - Hydration
    - Caffeine and alcohol intake
    
    **Environmental Triggers**:
    - Weather changes
    - Atmospheric pressure
    - Humidity
    - Temperature changes
    - Bright lights
    - Loud noises
    - Strong smells
    
    **Physical Factors**:
    - Missed meals
    - Dehydration
    - Trigger foods
    - Physical activity
    - Neck pain
    - Menstrual cycle
    
    ### 🚀 Technology Stack
    
    - **Backend**: FastAPI
    - **ML Framework**: Scikit-learn, XGBoost, LightGBM
    - **Deployment**: Docker & Docker Compose
    - **UI**: Streamlit
    - **Experiment Tracking**: MLflow
    
    ### 👨‍💻 Developer
    
    **Darish** - [GitHub](https://github.com/Darish05)
    
    ### 📄 License
    
    This project is licensed under the MIT License.
    
    ---
    
    *Made with ❤️ for Healthcare AI*
    """)
    
    st.markdown("---")
    
    # System info
    st.subheader("🔧 System Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("API Version", "2.0.0")
    with col2:
        st.metric("UI Framework", "Streamlit")
    with col3:
        try:
            health = requests.get(f"{API_URL}/health", timeout=5).json()
            status = "✅ Healthy" if health.get("status") == "healthy" else "❌ Unhealthy"
            st.metric("API Status", status)
        except:
            st.metric("API Status", "❌ Offline")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🏥 Migraine Prediction System v2.0 | Built with Streamlit & FastAPI</p>
        <p>⚠️ This tool is for educational purposes. Always consult healthcare professionals.</p>
    </div>
""", unsafe_allow_html=True)
