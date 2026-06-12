import streamlit as st
import pandas as pd 
import requests
from fpdf import FPDF
import plotly.express as px
from groq import Groq
from data.rainfall_data import cities, city_coordinates
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
client = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)
def get_weather_data(city):

    try:
        API_KEY = st.secrets["OPENWEATHER_API_KEY"]
    except Exception:
        API_KEY = None

    fallback_weather = {
        "Nagpur": {"temperature_2m": 32, "relative_humidity_2m": 55, "precipitation": 0, "wind_speed_10m": 10},
        "Mumbai": {"temperature_2m": 29, "relative_humidity_2m": 78, "precipitation": 1.2, "wind_speed_10m": 14},
        "Pune": {"temperature_2m": 27, "relative_humidity_2m": 65, "precipitation": 0.3, "wind_speed_10m": 9},
        "Delhi": {"temperature_2m": 35, "relative_humidity_2m": 40, "precipitation": 0, "wind_speed_10m": 12}
    }

    if not API_KEY:
        return fallback_weather.get(city)

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={API_KEY}&units=metric"
    )

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()

            return {
                "temperature_2m": data["main"]["temp"],
                "relative_humidity_2m": data["main"]["humidity"],
                "precipitation": data.get("rain", {}).get("1h", 0),
                "wind_speed_10m": data["wind"]["speed"]
            }

        return fallback_weather.get(city)

    except Exception:
        return fallback_weather.get(city)
st.markdown("""
<style>
/* Main App Background */
.stApp {
    background-color: #F5F7FA;
}

/* Modern Metric Cards */
div[data-testid="metric-container"] {
    background-color: #ffffff;
    border: 2px solid #caf0f8;
    padding: 18px;
    border-radius: 15px;
    box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.08);
    transition: 0.3s;
    width: 100%;
}

div[data-testid="metric-container"]:hover {
    transform: translateY(-5px);
    border-color: #0077b6;
    box-shadow: 0px 8px 20px rgba(0, 119, 182, 0.2);
}
            [data-testid="column"] {
    background-color: transparent;
    padding: 5px;
}
/* Headers */
h1, h2, h3 {
    color: #1E3A8A;
}

/* Input Boxes */
.stNumberInput, .stSelectbox {
    background-color: white;
    border-radius: 10px;
}

/* Buttons */
.stButton>button {
    background-color: #2563EB;
    color: white;
    border-radius: 10px;
    border: none;
    padding: 10px 20px;
}

</style>
""", unsafe_allow_html=True)
# Page config
st.set_page_config(
    page_title="AquaSave AI",
    layout="wide"
)

st.markdown("""
<div style="
    background: linear-gradient(135deg, #0077b6, #00b4d8, #90e0ef);
    padding: 28px;
    border-radius: 18px;
    text-align: center;
    margin-bottom: 20px;
">
    <h1 style="color: Navy blue; margin: 0;">💧 AquaSave AI Dashboard</h1>
    <p style="color: #f8fbff; font-size: 18px; margin-top: 8px;">
       Smart Rainwater Harvesting Analysis Tool
    </p>
</div>
""", unsafe_allow_html=True)
st.markdown("""
Calculate ROI, payback period, savings, and environmental impact for your
rainwater harvesting system. AquaSave AI also provides smart AI recommendations and weather insights to help
you improve system efficiency and make better decisions.
""")
tab1, tab2, tab3, tab4 = st.tabs([
    "Calculator",
    "How It Works",
    "Benefits",
    "About"
])

with tab1:
    left_col, right_col = st.columns([1, 2])
    
    with left_col:

        st.header("Enter Your Details")

        # Collection area (roof area in sq meters)
        area = st.number_input(
            "Roof Collection Area (sq meters)",
            min_value=10.0,
            max_value=5000.0,
            value=100.0,
            step=10.0,
            help="Total area of your roof that collects rainwater"
        )

        # Average annual rainfall (mm)
        # Select City
        selected_city = st.selectbox(
            "Select City",
            list(cities.keys())
        )

        # Auto rainfall from city
        rainfall = cities[selected_city]

        # Show rainfall value
        st.write(f"Average Annual Rainfall: {rainfall} mm")

        # Runoff coefficient (efficiency of collection)
        coefficient = st.slider(
            "Runoff Coefficient (Collection Efficiency)",
            min_value=0.5,
            max_value=0.95,
            value=0.85,
            step=0.05,
            help="0.85 = 85% of rain is collected (typical for metal roofs)"
        )

        # Cost per liter of tap water (INR)
        water_cost = st.number_input(
            "Cost per Liter of Tap Water (Rs)",
            min_value=0.01,
            max_value=50.0,
            value=0.05,
            step=0.01,
            help="Average cost of 1 liter of tap/borewell water"
        )

        # System cost (installation + materials)
        system_cost = st.number_input(
            "Total System Cost (Rs)",
            min_value=1000.0,
            max_value=500000.0,
            value=50000.0,
            step=1000.0,
            help="Total cost of tanks, pipes, filters, installation"
        )

        # Maintenance cost per year (Rs)
        maintenance_cost = st.number_input(
            "Annual Maintenance Cost (Rs)",
            min_value=0.0,
            max_value=10000.0,
            value=500.0,
            step=100.0,
            help="Yearly cost for cleaning filters, repairs, etc."
        )

        # System lifespan (years)
        lifespan = st.number_input(
            "System Lifespan (years)",
            min_value=5,
            max_value=50,
            value=20,
            step=1,
            help="Expected life of the rainwater harvesting system"
        )

        # Calculate water collection
        # Formula: Water (Liters) = Area (m²) × Rainfall (mm) × Coefficient
        # 1 mm rainfall on 1 m² = 1 liter
        annual_water_collection = area * rainfall * coefficient
        total_water_collection = annual_water_collection * lifespan

        # Calculate savings
        annual_savings = annual_water_collection * water_cost
        total_gross_savings = annual_savings * lifespan
        total_maintenance_cost = maintenance_cost * lifespan
        total_net_savings = total_gross_savings - total_maintenance_cost

        # ROI calculations
        net_annual_benefit = annual_savings - maintenance_cost
        if net_annual_benefit > 0:
            payback_years = system_cost / net_annual_benefit
            roi_percentage = ((total_net_savings - system_cost) / system_cost) * 100
        else:
            payback_years = float('inf')
            roi_percentage = -100.0

        # Environmental impact (water saved in cubic meters)
        recommended_tank = annual_water_collection * 0.2
        water_saved_m3 = total_water_collection / 1000
        if annual_water_collection < 50000:
            recommended_tank = 1000

        elif annual_water_collection < 150000:
            recommended_tank = 5000

        else:
            recommended_tank = 10000

    # Display results
    with right_col:
        st.header("📊 Dashboard Results")
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("💰 Financial Analysis")
        col1, col2, col3 = st.columns(3)

        card_style = """
        <style>
        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 18px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            border: 1px solid #caf0f8;
            text-align: center;
            transition: 0.3s;
        }

        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0,119,182,0.15);
        }

        .metric-title {
            font-size: 18px;
            color: #023e8a;
            font-weight: 600;
        }

        .metric-value {
            font-size: 42px;
            font-weight: bold;
            color: #0077b6;
        }

        .metric-sub {
            color: green;
            font-size: 15px;
        }
        </style>
        """

        st.markdown(card_style, unsafe_allow_html=True)

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">💧 Annual Water Collected</div>
                <div class="metric-value">{annual_water_collection:,.0f} L</div>
                <div class="metric-sub">↑ per year</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">💰 Annual Savings</div>
                <div class="metric-value">Rs{annual_savings:,.0f}</div>
                <div class="metric-sub">↑ per year</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            payback_text = f"{payback_years:.1f} years" if payback_years != float('inf') else "Never"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">📈 Payback Period</div>
                <div class="metric-value">{payback_text}</div>
                <div class="metric-sub">↑ to break even</div>
            </div>
            """, unsafe_allow_html=True)
        st.divider()

        col4, col5 = st.columns(2)

        with col4:
            st.subheader("💰 Financial Summary")
            st.write(f"**Total System Cost:** Rs{system_cost:,.0f}")
            st.write(f"**Total Gross Savings ({lifespan} yrs):** Rs{total_gross_savings:,.0f}")
            st.write(f"**Total Maintenance Cost ({lifespan} yrs):** Rs{total_maintenance_cost:,.0f}")
            st.write(f"**Total Net Savings:** Rs{total_net_savings:,.0f}")
            st.write(f"**ROI:** {roi_percentage:.1f}%")

        with col5:
            st.subheader("🌱 Environmental Impact")
            st.write(f"**Total Water Collected:** {total_water_collection:,.0f} Liters")
            st.write(f"**Water Saved:** {water_saved_m3:,.1f} m³")
            tanker_count = total_water_collection / 10000
            st.write(f"**Equivalent to:** {tanker_count:.1f} tanker trucks (10k L each)")

    st.divider()
    st.subheader("🌦️ Live Weather Insights")

    weather = get_weather_data(selected_city)

    if weather:
        w1, w2, w3, w4 = st.columns(4)

        with w1:
            st.metric("🌡️ Temperature", f"{weather.get('temperature_2m', 'N/A')} °C")

        with w2:
            st.metric("💧 Humidity", f"{weather.get('relative_humidity_2m', 'N/A')} %")

        with w3:
            st.metric("🌧️ Current Rainfall", f"{weather.get('precipitation', 'N/A')} mm")

        with w4:
            st.metric("🌬️ Wind Speed", f"{weather.get('wind_speed_10m', 'N/A')} km/h")
    else:
        st.warning("Weather data is currently unavailable.")
    # ROI Chart
    st.subheader(" Investment Growth Analysis")
    st.markdown("<br>", unsafe_allow_html=True)
    col_sum1, col_sum2 = st.columns(2)
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🛢️ Recommended Storage Tank")
    st.success(
            f"Recommended Tank Capacity: {recommended_tank:,} Liters"
            )

    with col_sum1:
        st.info(f"🌍 City: {selected_city}")
        st.info(f"🌧️ Rainfall: {rainfall} mm")
        st.info(f"🏠 Roof Area: {area:,.0f} m²")
        st.info(f"💧 Water Collection: {annual_water_collection:,.0f} L")

    with col_sum2:
        st.info(f"🛢️ Tank Size: {recommended_tank:,.0f} L")
        st.info(f"💰 Annual Savings: Rs{annual_savings:,.0f}")
        st.info(f"📈 ROI: {roi_percentage:.1f}%")
        st.info(f"⏳ Payback: {payback_text}")
    # Create data for chart
    years = list(range(1, lifespan + 1))
    cumulative_savings = []

    for year in years:
        cumulative_savings.append(net_annual_benefit * year)

    df_chart = pd.DataFrame({
        "Year": years,
        "Cumulative Net Savings": cumulative_savings[:len(years)],
        "Break-even Line": [system_cost for _ in years]
        })
    # Line chart
    st.subheader("Water Collection Efficiency")

    pie_data = pd.DataFrame({
        "Category": ["Collected Water", "Water Loss"],
        "Value": [
            annual_water_collection,
            area * rainfall * (1 - coefficient)
        ]
    })

    pie_fig = px.pie(
        pie_data,
        names="Category",
        values="Value",
        title="Rainwater Utilization",
        hole=0.45,
        color_discrete_sequence=["#9CD7F3", "#9061EF"]
    )

    pie_fig.update_traces(
        textinfo="label+percent",
        textposition="inside",
        insidetextorientation="horizontal",
        textfont=dict(color="#1F2937", size=14),
        marker=dict(line=dict(color="white", width=2)),
        hovertemplate="<b>%{label}</b><br>Value: %{value:,.0f} L<br>Share: %{percent}<extra></extra>"
    )

    pie_fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color="#4A91BC"),
        title=dict(text="Rainwater Utilization", x=0.5, font=dict(size=20, color="#0D2B67")),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(color="#A4B78E")
        ),
        margin=dict(t=70, l=20, r=20, b=80)
    )

    st.plotly_chart(pie_fig, use_container_width=True)
    fig = px.area(
    df_chart,
    x="Year",
    y="Cumulative Net Savings",
    title="Cumulative Savings Over Time",
    markers=True,
    )

    fig.update_traces(
    line=dict(
        width=4,
        shape='spline',
        smoothing=1.3
    ),
    opacity=0.7
    )
    fig.update_layout(
        paper_bgcolor="#fefae0",
        plot_bgcolor="#ffffff",
        font_color="#03045e",
        hovermode="x unified",
        transition_duration=3500,
        xaxis_title="Year",
        yaxis_title="Savings (₹)",
        title_x=0.25,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="animated_area_chart"
    )
    # PASTE MONTHLY ANALYSIS HERE
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📅 Monthly Water Collection Analysis")

    monthly_rainfall = [
        rainfall * 0.02,
        rainfall * 0.03,
        rainfall * 0.05,
        rainfall * 0.08,
        rainfall * 0.12,
        rainfall * 0.18,
        rainfall * 0.20,
        rainfall * 0.16,
        rainfall * 0.08,
        rainfall * 0.04,
        rainfall * 0.02,
        rainfall * 0.02
    ]

    months = [
        "Jan", "Feb", "Mar", "Apr",
        "May", "Jun", "Jul", "Aug",
        "Sep", "Oct", "Nov", "Dec"
    ]

    monthly_collection = [
        area * rain * coefficient
        for rain in monthly_rainfall
    ]

    monthly_df = pd.DataFrame({
        "Month": months,
        "Water Collection": monthly_collection
    })

    monthly_fig = px.bar(
        monthly_df,
        x="Month",
        y="Water Collection",
        title="Estimated Monthly Rainwater Collection",
        text_auto=".0f"
    )

    monthly_fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="beige",
        font_color="black",
        transition_duration=1000
    )

    st.plotly_chart(monthly_fig, use_container_width=True)
    # Conclusion
    st.divider()
    st.subheader(" Final Recommendation")

    if payback_years < lifespan and roi_percentage > 0:

        st.success(
            f"""
            Excellent Investment Opportunity ✅

            Your rainwater harvesting system will recover its cost
            in approximately {payback_years:.1f} years and generate
            an ROI of {roi_percentage:.1f}% over {lifespan} years.
            """
            )

    elif payback_years == float('inf'):

        st.error(
            """
            Investment Not Recommended ❌

            Annual savings are currently lower than maintenance costs.
            Try increasing roof area or adjusting water pricing.
            """
            )

    else:

        st.info(
        f"""
        Moderate Investment ⚠️

        The system breaks even in {payback_years:.1f} years
        with an ROI of {roi_percentage:.1f}%.
        """
        )
        st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("🤖 Smart AI Recommendations")

    if rainfall < 700:
        st.warning(
            "Low rainfall detected. Consider increasing storage capacity to maximize collection."
        )

    if coefficient < 0.7:
        st.info(
            "Your runoff coefficient is low. A smoother roof surface can improve efficiency."
        )

    if payback_years > 10:
        st.warning(
            "Payback period is high. Reducing installation cost may improve ROI."
        )

    if roi_percentage > 100:
        st.success(
            "Excellent ROI detected! This project is highly financially beneficial."
        )
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🤖 AquaSave AI Advisor")

    user_question = st.text_input(
        "Ask AquaSave AI about your rainwater harvesting system"
    )

    if st.button("Get AI Advice"):

        if user_question.strip() == "":
            st.warning("Please enter a question.")
        else:

            with st.spinner("Analyzing your project..."):

                project_context = f"""
                Rainwater Harvesting Analysis

                City: {selected_city}
                Roof Area: {area} sq m
                Annual Rainfall: {rainfall} mm
                Annual Water Collection: {annual_water_collection:.0f} liters
                Annual Savings: Rs {annual_savings:.0f}
                ROI: {roi_percentage:.1f}%
                Payback Period: {payback_text}
                Recommended Tank Size: {recommended_tank} liters

                User Question:
                {user_question}
                """

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "system",
                            "content": """
                            You are an expert rainwater harvesting consultant.
                            Give practical recommendations based on the user's ROI,
                            rainfall, savings, and tank size.
                            Keep answers simple and actionable.
                            """
                        },
                        {
                            "role": "user",
                            "content": project_context
                        }
                    ]
                )

                answer = response.choices[0].message.content

                st.success(answer)
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", size=16)
    pdf.cell(200, 10, txt="AquaSave AI Report", ln=True, align='C')

    pdf.ln(10)

    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"Selected City: {selected_city}", ln=True)
    pdf.cell(200, 10, txt=f"Annual Rainfall: {rainfall} mm", ln=True)
    pdf.cell(200, 10, txt=f"Roof Area: {area} m²", ln=True)
    pdf.cell(200, 10, txt=f"Annual Water Collection: {annual_water_collection:,.0f} L", ln=True)
    pdf.cell(200, 10, txt=f"Annual Savings: Rs{annual_savings:,.0f}", ln=True)
    pdf.cell(200, 10, txt=f"ROI: {roi_percentage:.1f}%", ln=True)
    pdf.cell(200, 10, txt=f"Payback Period: {payback_text}", ln=True)
    pdf.cell(200, 10, txt=f"Recommended Tank: {recommended_tank:,} L", ln=True)

    pdf.output("Rainwater_Report.pdf")

    with open("Rainwater_Report.pdf", "rb") as pdf_file:
        PDFbyte = pdf_file.read()

    st.download_button(
        label="📄 Download PDF Report",
        data=PDFbyte,
        file_name="Rainwater_Report.pdf",
        mime="application/pdf"
    )   
     # Download button
    csv = df_chart.to_csv(index=False)
    st.download_button(
    label=" Download Results as CSV",
    data=csv,
    file_name="rainwater_roi_results.csv",
    mime="text/csv"
    )
with tab2:

        st.header("How It Works")

        st.write("1. Enter roof area and city")
        st.write("2. System calculates rainwater harvesting")
        st.write("3. View savings, ROI and environmental impact")
        
with tab3:

    st.header("Benefits")

    st.write("💧 Save water")
    st.write("💰 Reduce water bills")
    st.write("🌱 Help environment")
    st.write("📈 Long-term ROI")
with tab4:
    st.subheader("About This Project")
    st.write("AquaSave AI: Intelligent Rainwater Harvesting Analytics and Decision Support System")
    st.write("""
        This project helps users estimate the financial and environmental
        benefits of rainwater harvesting systems.

        Features:
        - ROI Calculation
        - Payback Period Analysis
        - Water Savings Estimation
        - Environmental Impact Metrics
        - Live Weather Insights
        - Smart AI Recommendations
        - Interactive Charts

        Technologies Used:
        - Python
        - Streamlit
        - Plotly
        - Pandas 
            """)
    st.subheader("📌 Assumptions Used")

    st.info("""
    - 1 mm rainfall on 1 m² roof area is considered equal to 1 liter of water.
    - Runoff coefficient represents the collection efficiency of the roof.
    - Annual savings are calculated using the water cost entered by the user.
    - Maintenance cost is deducted while calculating net savings.
    - Results are estimated for educational and planning purposes.
    """)

    st.subheader("⚠️ Disclaimer")

    st.warning("""
    The results shown by this calculator are approximate estimates.
    Actual rainwater harvesting performance may vary depending on roof condition,
    rainfall pattern, tank capacity, filter quality, water usage, and local installation cost.
    """)
st.markdown("---")
st.caption("Developed by Manasvi Devghare | AquaSave AI ")