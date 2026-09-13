import os
import json
import html
from datetime import datetime

import streamlit as st
from groq import Groq


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Battery-AI | Battery Health Assistant",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>
    /* Main application */
    .stApp {
        background:
            radial-gradient(
                circle at top right,
                rgba(34, 197, 94, 0.08),
                transparent 35%
            ),
            linear-gradient(135deg, #07111f 0%, #0b1628 50%, #101827 100%);
        color: #f8fafc;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Hide Streamlit default elements */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        background: transparent !important;
    }

    /* Hero section */
    .hero {
        padding: 2rem 2.2rem;
        border-radius: 24px;
        margin-bottom: 1.5rem;
        background:
            linear-gradient(
                135deg,
                rgba(15, 23, 42, 0.98),
                rgba(15, 45, 42, 0.95)
            );
        border: 1px solid rgba(74, 222, 128, 0.28);
        box-shadow: 0 15px 45px rgba(0, 0, 0, 0.20);
    }

    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -1.5px;
        margin: 0;
        color: #f8fafc;
    }

    .hero-title span {
        color: #4ade80;
    }

    .hero-subtitle {
        color: #cbd5e1;
        font-size: 1.05rem;
        margin-top: 0.5rem;
        max-width: 850px;
    }

    .hero-badge {
        display: inline-block;
        margin-top: 1rem;
        padding: 0.4rem 0.85rem;
        border-radius: 999px;
        background: rgba(74, 222, 128, 0.13);
        color: #86efac;
        border: 1px solid rgba(74, 222, 128, 0.30);
        font-size: 0.82rem;
        font-weight: 700;
    }

    /* Section cards */
    .section-card {
        background: rgba(15, 23, 42, 0.82);
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 20px;
        padding: 1.25rem 1.35rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 28px rgba(0, 0, 0, 0.12);
    }

    .section-title {
        font-size: 1.15rem;
        font-weight: 750;
        color: #f8fafc;
        margin-bottom: 0.25rem;
    }

    .section-description {
        font-size: 0.86rem;
        color: #94a3b8;
        margin-bottom: 1rem;
    }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(
            145deg,
            rgba(15, 23, 42, 0.95),
            rgba(30, 41, 59, 0.85)
        );
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 18px;
        padding: 1.1rem;
        min-height: 130px;
    }

    .metric-label {
        color: #94a3b8;
        font-size: 0.82rem;
        font-weight: 600;
    }

    .metric-value {
        color: #f8fafc;
        font-size: 2rem;
        font-weight: 800;
        margin-top: 0.35rem;
    }

    .metric-caption {
        color: #cbd5e1;
        font-size: 0.78rem;
        margin-top: 0.2rem;
    }

    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.45rem 0.9rem;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 800;
        margin-top: 0.4rem;
    }

    .status-good {
        background: rgba(34, 197, 94, 0.15);
        color: #86efac;
        border: 1px solid rgba(34, 197, 94, 0.35);
    }

    .status-warning {
        background: rgba(250, 204, 21, 0.13);
        color: #fde047;
        border: 1px solid rgba(250, 204, 21, 0.35);
    }

    .status-danger {
        background: rgba(248, 113, 113, 0.13);
        color: #fca5a5;
        border: 1px solid rgba(248, 113, 113, 0.35);
    }

    .status-neutral {
        background: rgba(148, 163, 184, 0.13);
        color: #cbd5e1;
        border: 1px solid rgba(148, 163, 184, 0.3);
    }

    /* Warning box */
    .warning-box {
        padding: 1rem 1.1rem;
        border-radius: 14px;
        background: rgba(127, 29, 29, 0.22);
        border: 1px solid rgba(248, 113, 113, 0.3);
        color: #fecaca;
        margin-bottom: 0.7rem;
    }

    .info-box {
        padding: 1rem 1.1rem;
        border-radius: 14px;
        background: rgba(30, 64, 175, 0.16);
        border: 1px solid rgba(96, 165, 250, 0.28);
        color: #bfdbfe;
        margin-bottom: 0.7rem;
    }

    /* Buttons */
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        min-height: 3rem;
        font-weight: 750;
        border: 1px solid rgba(74, 222, 128, 0.35);
        background: linear-gradient(135deg, #16a34a, #22c55e);
        color: #052e16;
        transition: all 0.2s ease-in-out;
    }

    .stButton > button:hover {
        border-color: #86efac;
        background: linear-gradient(135deg, #22c55e, #4ade80);
        color: #052e16;
        transform: translateY(-1px);
    }

    .stDownloadButton > button {
        width: 100%;
        border-radius: 12px;
        min-height: 2.8rem;
        font-weight: 700;
    }

    /* Inputs */
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea,
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: rgba(15, 23, 42, 0.85) !important;
        color: #f8fafc !important;
        border-radius: 10px !important;
    }

    label {
        color: #cbd5e1 !important;
        font-weight: 600 !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(30, 41, 59, 0.75);
        border-radius: 10px;
        padding: 0.65rem 1rem;
        color: #cbd5e1;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(34, 197, 94, 0.18);
        color: #86efac;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #08111f, #0f172a);
        border-right: 1px solid rgba(148, 163, 184, 0.15);
    }

    /* Footer disclaimer */
    .footer-note {
        text-align: center;
        color: #64748b;
        font-size: 0.78rem;
        padding-top: 2rem;
    }

    @media (max-width: 800px) {
        .hero-title {
            font-size: 2.1rem;
        }

        .hero {
            padding: 1.4rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SESSION STATE
# =========================================================

if "report" not in st.session_state:
    st.session_state.report = None

if "last_input" not in st.session_state:
    st.session_state.last_input = None


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_api_key():
    """
    Read the Groq API key from Streamlit Secrets first,
    then from environment variables.
    """

    try:
        secret_key = st.secrets.get("GROQ_API_KEY")
        if secret_key:
            return secret_key
    except Exception:
        pass

    return os.getenv("GROQ_API_KEY")


def safe_float(value):
    """
    Convert a value to float safely.
    Empty values return None.
    """
    if value is None or value == "":
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def calculate_capacity_health(rated_capacity, measured_capacity):
    """
    Calculate capacity health percentage.
    """
    if rated_capacity and measured_capacity:
        if rated_capacity > 0 and measured_capacity >= 0:
            return round((measured_capacity / rated_capacity) * 100, 1)

    return None


def capacity_status(health):
    """
    Return a simple status based on capacity health.
    These are approximate indicators, not universal engineering limits.
    """

    if health is None:
        return "Not Available", "neutral"

    if health >= 80:
        return "Good", "good"

    if health >= 60:
        return "Needs Attention", "warning"

    return "Poor", "danger"


def build_rule_warnings(data):
    """
    Generate cautious rule-based warnings.
    These rules are only preliminary indicators.
    """

    warnings = []

    battery_type = str(data.get("battery_type", "")).lower()
    voltage = data.get("voltage")
    charging_voltage = data.get("charging_voltage")
    temperature = data.get("temperature")
    measured_capacity = data.get("measured_capacity")
    rated_capacity = data.get("rated_capacity")
    specific_gravity = data.get("specific_gravity")
    symptom = str(data.get("symptom", "")).lower()
    observations = str(data.get("observations", "")).lower()

    dangerous_words = [
        "swollen",
        "swelling",
        "smoke",
        "leak",
        "leaking",
        "spark",
        "sparking",
        "burning",
        "overheating",
        "explosion",
    ]

    combined_text = f"{symptom} {observations}"

    if any(word in combined_text for word in dangerous_words):
        warnings.append(
            "Potential safety hazard reported. Stop using the battery if it is "
            "swollen, leaking, smoking, sparking, or severely overheating. "
            "Contact a qualified technician."
        )

    if voltage is not None and voltage <= 0:
        warnings.append("Measured battery voltage is invalid or zero.")

    if charging_voltage is not None and charging_voltage <= 0:
        warnings.append("Charging voltage is missing or invalid.")

    if rated_capacity and measured_capacity is not None:
        if measured_capacity > rated_capacity:
            warnings.append(
                "Measured capacity is higher than rated capacity. "
                "Check the test method, units, and measurement conditions."
            )

    if temperature is not None:
        if temperature >= 50:
            warnings.append(
                "High temperature reported. Stop charging or discharging if "
                "the battery is dangerously hot and inspect the system."
            )

    if "lithium" in battery_type and specific_gravity is not None:
        warnings.append(
            "Specific gravity is generally not applicable to lithium-ion batteries. "
            "Remove this value or use the correct battery-specific test."
        )

    if "low backup" in symptom or "short backup" in symptom:
        warnings.append(
            "Low backup time can be caused by reduced capacity, high load, "
            "poor charging, battery aging, loose connections, or temperature."
        )

    if not warnings:
        warnings.append(
            "No major rule-based warning was detected from the entered values. "
            "This does not confirm that the battery is healthy."
        )

    return warnings


def create_ai_prompt(data, calculated_metrics, warnings):
    """
    Create the prompt sent to the Groq model.
    """

    return f"""
You are Battery-AI, a careful battery troubleshooting assistant.

Your task is to produce a preliminary technical assessment.
Do not claim certainty.
Do not invent measurements.
Clearly separate:
1. User-entered measurements
2. Calculated values
3. Possible causes
4. Recommended checks
5. Safety warnings
6. Missing information

Important safety instructions:
- Do not provide dangerous repair instructions.
- Do not advise opening, puncturing, short-circuiting, or modifying a battery.
- If swelling, smoke, leakage, sparks, burning smell, or severe overheating is reported,
  recommend stopping use and contacting a qualified technician.
- Battery behavior depends on chemistry, manufacturer, temperature, test method, and load.
- Do not apply lead-acid-specific tests to lithium-ion batteries.
- State that this is preliminary decision support, not a certified diagnosis.

Battery information:
{json.dumps(data, indent=2)}

Calculated metrics:
{json.dumps(calculated_metrics, indent=2)}

Rule-based warnings:
{json.dumps(warnings, indent=2)}

Return valid JSON with exactly these keys:

{{
  "status": "Healthy / Needs Attention / Poor / Unsafe / Inconclusive",
  "summary": "Short clear summary",
  "entered_data_review": [],
  "calculated_metrics": [],
  "possible_problems": [],
  "possible_causes": [],
  "recommended_checks": [],
  "recommended_actions": [],
  "maintenance_advice": [],
  "safety_warnings": [],
  "missing_information": [],
  "disclaimer": "Preliminary decision-support disclaimer"
}}

Use arrays for all list fields.
Keep the language understandable for technicians and general users.
"""


def generate_ai_report(data, calculated_metrics, warnings):
    """
    Call Groq and return a JSON report.
    """

    api_key = get_api_key()

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY was not found. Add it in Streamlit Secrets "
            "or as an environment variable."
        )

    client = Groq(api_key=api_key)

    model_name = os.getenv(
        "GROQ_MODEL",
        "openai/gpt-oss-120b"
    )

    prompt = create_ai_prompt(
        data=data,
        calculated_metrics=calculated_metrics,
        warnings=warnings,
    )

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a careful battery engineering assistant. "
                    "Return only valid JSON."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.2,
        max_tokens=3000,
    )

    content = response.choices[0].message.content.strip()

    # Remove markdown JSON fences if the model adds them
    if content.startswith("```"):
        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "status": "Inconclusive",
            "summary": content,
            "entered_data_review": [],
            "calculated_metrics": [],
            "possible_problems": [],
            "possible_causes": [],
            "recommended_checks": [],
            "recommended_actions": [],
            "maintenance_advice": [],
            "safety_warnings": [],
            "missing_information": [],
            "disclaimer": (
                "The AI response could not be converted into structured JSON. "
                "Review the text carefully and consult a qualified technician."
            ),
        }


def report_to_markdown(report):
    """
    Convert the report JSON into a Markdown document.
    """

    if not report:
        return ""

    lines = [
        "# Battery-AI Diagnostic Report",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        f"## Status",
        report.get("status", "Inconclusive"),
        "",
        "## Summary",
        report.get("summary", ""),
        "",
    ]

    sections = [
        ("Entered Data Review", "entered_data_review"),
        ("Calculated Metrics", "calculated_metrics"),
        ("Possible Problems", "possible_problems"),
        ("Possible Causes", "possible_causes"),
        ("Recommended Checks", "recommended_checks"),
        ("Recommended Actions", "recommended_actions"),
        ("Maintenance Advice", "maintenance_advice"),
        ("Safety Warnings", "safety_warnings"),
        ("Missing Information", "missing_information"),
    ]

    for title, key in sections:
        lines.append(f"## {title}")

        values = report.get(key, [])

        if isinstance(values, list):
            for value in values:
                lines.append(f"- {value}")
        else:
            lines.append(str(values))

        lines.append("")

    lines.extend(
        [
            "## Disclaimer",
            report.get("disclaimer", ""),
            "",
            "---",
            "Battery-AI provides preliminary decision support only.",
        ]
    )

    return "\n".join(lines)


def display_list(values):
    """
    Display list items in a clean way.
    """

    if not values:
        st.info("No information available in this section.")
        return

    if isinstance(values, list):
        for item in values:
            st.markdown(f"- {item}")
    else:
        st.write(values)


def show_status_badge(status):
    """
    Display a colored status badge.
    """

    status_lower = str(status).lower()

    if "healthy" in status_lower or "good" in status_lower:
        css_class = "status-good"
    elif "unsafe" in status_lower or "poor" in status_lower:
        css_class = "status-danger"
    elif "attention" in status_lower:
        css_class = "status-warning"
    else:
        css_class = "status-neutral"

    safe_status = html.escape(str(status))

    st.markdown(
        f'<span class="status-badge {css_class}">{safe_status}</span>',
        unsafe_allow_html=True,
    )


# =========================================================
# HERO HEADER
# =========================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">🔋 Battery-<span>AI</span></div>
        <div class="hero-subtitle">
            Intelligent Battery Health & Diagnostic Assistant
            <br>
            Analyze battery measurements, identify possible problems,
            and generate an understandable preliminary technical report.
        </div>
        <div class="hero-badge">
            ⚡ Python Rules + Groq AI &nbsp; | &nbsp; Preliminary Decision Support
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown("## 🔋 Battery-AI")
    st.caption("Your intelligent battery troubleshooting companion.")

    st.markdown("---")

    st.markdown("### Quick Demo")

    if st.button("Load Demo Battery Data"):
        st.session_state.demo_loaded = True
        st.rerun()

    if st.button("Clear Report"):
        st.session_state.report = None
        st.session_state.last_input = None
        st.rerun()

    st.markdown("---")

    st.markdown("### Safety Reminder")
    st.warning(
        "This application provides preliminary decision support only. "
        "For swelling, smoke, leakage, sparks, or severe overheating, "
        "stop using the battery and contact a qualified technician."
    )

    st.markdown("---")
    st.caption("Developed by Abdullah Awan")


# =========================================================
# DEFAULT / DEMO VALUES
# =========================================================

demo_loaded = st.session_state.get("demo_loaded", False)

if demo_loaded:
    default_battery_type = "Tubular Lead-Acid"
    default_brand = "Volta"
    default_application = "UPS / Solar Backup"
    default_voltage = 12.1
    default_rated_capacity = 100.0
    default_measured_capacity = 65.0
    default_charging_voltage = 14.2
    default_charging_current = 8.0
    default_load_current = 10.0
    default_internal_resistance = 12.0
    default_age = 2.0
    default_temperature = 32.0
    default_specific_gravity = 1.20
    default_symptom = "Low backup time"
    default_observations = (
        "Battery backup has reduced compared with previous performance. "
        "Charging appears normal but backup time is short."
    )
else:
    default_battery_type = "Tubular Lead-Acid"
    default_brand = ""
    default_application = "UPS / Solar Backup"
    default_voltage = 12.0
    default_rated_capacity = 100.0
    default_measured_capacity = 0.0
    default_charging_voltage = 14.2
    default_charging_current = 0.0
    default_load_current = 0.0
    default_internal_resistance = 0.0
    default_age = 0.0
    default_temperature = 25.0
    default_specific_gravity = 0.0
    default_symptom = "Select symptom"
    default_observations = ""


# =========================================================
# INPUT FORM
# =========================================================

st.markdown(
    """
    <div class="section-card">
        <div class="section-title">🧪 Battery Assessment Workspace</div>
        <div class="section-description">
            Enter the available battery information and measured values.
            Leave unknown values at zero or blank.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


with st.form("battery_assessment_form"):

    left_col, right_col = st.columns([1, 1], gap="large")

    # -----------------------------------------------------
    # LEFT COLUMN
    # -----------------------------------------------------

    with left_col:

        st.markdown(
            """
            <div class="section-card">
                <div class="section-title">🔋 Battery Identity</div>
                <div class="section-description">
                    Basic information about the battery.
                </div>
            """,
            unsafe_allow_html=True,
        )

        battery_type = st.selectbox(
            "Battery Type",
            [
                "Tubular Lead-Acid",
                "Flooded Lead-Acid",
                "AGM Lead-Acid",
                "Gel Lead-Acid",
                "Lithium-Ion",
                "LiFePO4",
                "VRLA",
                "Motorcycle Battery",
                "Automotive Battery",
                "Other",
            ],
            index=[
                "Tubular Lead-Acid",
                "Flooded Lead-Acid",
                "AGM Lead-Acid",
                "Gel Lead-Acid",
                "Lithium-Ion",
                "LiFePO4",
                "VRLA",
                "Motorcycle Battery",
                "Automotive Battery",
                "Other",
            ].index(default_battery_type)
            if default_battery_type in [
                "Tubular Lead-Acid",
                "Flooded Lead-Acid",
                "AGM Lead-Acid",
                "Gel Lead-Acid",
                "Lithium-Ion",
                "LiFePO4",
                "VRLA",
                "Motorcycle Battery",
                "Automotive Battery",
                "Other",
            ]
            else 0,
        )

        brand = st.text_input(
            "Brand / Model",
            value=default_brand,
            placeholder="Example: Volta 12V 100Ah",
        )

        application = st.selectbox(
            "Application",
            [
                "UPS / Solar Backup",
                "Automotive",
                "Motorcycle",
                "Telecom",
                "Industrial",
                "Inverter",
                "Electric Vehicle",
                "Energy Storage",
                "Other",
            ],
            index=0,
        )

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            """
            <div class="section-card">
                <div class="section-title">📏 Electrical Measurements</div>
                <div class="section-description">
                    Enter values from your multimeter, tester, or battery analyzer.
                </div>
            """,
            unsafe_allow_html=True,
        )

        voltage = st.number_input(
            "Battery Voltage (V)",
            min_value=0.0,
            max_value=1000.0,
            value=float(default_voltage),
            step=0.1,
        )

        rated_capacity = st.number_input(
            "Rated Capacity (Ah)",
            min_value=0.0,
            max_value=100000.0,
            value=float(default_rated_capacity),
            step=1.0,
        )

        measured_capacity = st.number_input(
            "Measured Capacity (Ah)",
            min_value=0.0,
            max_value=100000.0,
            value=float(default_measured_capacity),
            step=1.0,
        )

        charging_voltage = st.number_input(
            "Charging Voltage (V)",
            min_value=0.0,
            max_value=1000.0,
            value=float(default_charging_voltage),
            step=0.1,
        )

        charging_current = st.number_input(
            "Charging Current (A)",
            min_value=0.0,
            max_value=100000.0,
            value=float(default_charging_current),
            step=0.5,
        )

        load_current = st.number_input(
            "Load Current (A)",
            min_value=0.0,
            max_value=100000.0,
            value=float(default_load_current),
            step=0.5,
        )

        internal_resistance = st.number_input(
            "Internal Resistance (mΩ)",
            min_value=0.0,
            max_value=100000.0,
            value=float(default_internal_resistance),
            step=0.1,
            help=(
                "Enter the value only if measured with a suitable battery tester. "
                "Do not use universal resistance limits for every battery type."
            ),
        )

        st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------------------------------------
    # RIGHT COLUMN
    # -----------------------------------------------------

    with right_col:

        st.markdown(
            """
            <div class="section-card">
                <div class="section-title">🌡️ Battery Condition</div>
                <div class="section-description">
                    Age, temperature, and optional chemistry-specific readings.
                </div>
            """,
            unsafe_allow_html=True,
        )

        age = st.number_input(
            "Battery Age (Years)",
            min_value=0.0,
            max_value=100.0,
            value=float(default_age),
            step=0.5,
        )

        temperature = st.number_input(
            "Battery Temperature (°C)",
            min_value=-50.0,
            max_value=150.0,
            value=float(default_temperature),
            step=1.0,
        )

        specific_gravity = st.number_input(
            "Specific Gravity - Optional",
            min_value=0.0,
            max_value=2.0,
            value=float(default_specific_gravity),
            step=0.001,
            format="%.3f",
            help="Generally relevant only for suitable flooded lead-acid batteries.",
        )

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            """
            <div class="section-card">
                <div class="section-title">🩺 Symptoms & Observations</div>
                <div class="section-description">
                    Describe the actual problem noticed by the user or technician.
                </div>
            """,
            unsafe_allow_html=True,
        )

        symptom_options = [
            "Select symptom",
            "Low backup time",
            "Battery not charging",
            "Battery discharges quickly",
            "Low voltage",
            "High temperature",
            "Swelling or leakage",
            "Frequent replacement",
            "Starting problem",
            "Unequal cell voltage",
            "Other",
            "No obvious symptom",
        ]

        symptom = st.selectbox(
            "Main Symptom",
            symptom_options,
            index=(
                symptom_options.index(default_symptom)
                if default_symptom in symptom_options
                else 0
            ),
        )

        observations = st.text_area(
            "Additional Observations",
            value=default_observations,
            height=180,
            placeholder=(
                "Example: Battery backup reduced, terminals are slightly corroded, "
                "charging current fluctuates..."
            ),
        )

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("")

    submitted = st.form_submit_button(
        "⚡ Generate Intelligent Battery Report",
        use_container_width=True,
    )


# =========================================================
# PROCESS INPUT
# =========================================================

if submitted:

    input_data = {
        "battery_type": battery_type,
        "brand": brand,
        "application": application,
        "voltage": voltage,
        "rated_capacity": rated_capacity,
        "measured_capacity": measured_capacity,
        "charging_voltage": charging_voltage,
        "charging_current": charging_current,
        "load_current": load_current,
        "internal_resistance_mohm": internal_resistance,
        "age_years": age,
        "temperature_c": temperature,
        "specific_gravity": specific_gravity,
        "symptom": symptom,
        "observations": observations,
    }

    # Basic validation
    validation_errors = []

    if voltage <= 0:
        validation_errors.append("Battery voltage must be greater than zero.")

    if rated_capacity <= 0:
        validation_errors.append("Rated capacity must be greater than zero.")

    if measured_capacity < 0:
        validation_errors.append("Measured capacity cannot be negative.")

    if age < 0:
        validation_errors.append("Battery age cannot be negative.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)

    else:

        calculated_health = calculate_capacity_health(
            rated_capacity,
            measured_capacity,
        )

        status_text, status_type = capacity_status(calculated_health)

        calculated_metrics = {
            "capacity_health_percent": calculated_health,
            "capacity_status": status_text,
            "voltage_difference_from_12V": round(voltage - 12.0, 2),
        }

        warnings = build_rule_warnings(input_data)

        st.session_state.last_input = input_data

        # -------------------------------------------------
        # SUMMARY METRICS
        # -------------------------------------------------

        st.markdown("## 📊 Preliminary Assessment")

        metric_1, metric_2, metric_3, metric_4 = st.columns(4)

        with metric_1:
            health_display = (
                f"{calculated_health}%"
                if calculated_health is not None
                else "N/A"
            )

            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Capacity Health</div>
                    <div class="metric-value">{health_display}</div>
                    <div class="metric-caption">Rated vs measured capacity</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with metric_2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Battery Voltage</div>
                    <div class="metric-value">{voltage:.1f} V</div>
                    <div class="metric-caption">Entered measured voltage</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with metric_3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Battery Age</div>
                    <div class="metric-value">{age:g}</div>
                    <div class="metric-caption">Years in service</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with metric_4:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Initial Status</div>
                    <div class="metric-value" style="font-size:1.35rem;">
                        {html.escape(status_text)}
                    </div>
                    <div class="metric-caption">Preliminary rule-based result</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("")

        if calculated_health is not None:
            st.markdown("### Capacity Health Indicator")
            st.progress(
                min(max(calculated_health / 100, 0.0), 1.0),
                text=f"Capacity health: {calculated_health}%",
            )

        # -------------------------------------------------
        # RULE WARNINGS
        # -------------------------------------------------

        st.markdown("### ⚠️ Preliminary Warnings")

        for warning in warnings:
            st.markdown(
                f"""
                <div class="warning-box">
                    ⚠️ {html.escape(warning)}
                </div>
                """,
                unsafe_allow_html=True,
            )

        # -------------------------------------------------
        # AI REPORT
        # -------------------------------------------------

        with st.spinner("Battery-AI is analyzing the entered information..."):

            try:
                report = generate_ai_report(
                    data=input_data,
                    calculated_metrics=calculated_metrics,
                    warnings=warnings,
                )

                st.session_state.report = report

                st.success("Your preliminary battery report has been generated.")

            except Exception as error:
                st.error(f"Unable to generate AI report: {error}")


# =========================================================
# DISPLAY SAVED REPORT
# =========================================================

if st.session_state.report:

    report = st.session_state.report

    st.markdown("---")
    st.markdown("## 🤖 Battery-AI Technical Report")

    report_status = report.get("status", "Inconclusive")

    status_col, summary_col = st.columns([1, 3], gap="large")

    with status_col:
        st.markdown(
            """
            <div class="section-card">
                <div class="section-title">Assessment Status</div>
            """,
            unsafe_allow_html=True,
        )

        show_status_badge(report_status)

        st.markdown("</div>", unsafe_allow_html=True)

    with summary_col:
        st.markdown(
            """
            <div class="section-card">
                <div class="section-title">Executive Summary</div>
            """,
            unsafe_allow_html=True,
        )

        st.write(report.get("summary", "No summary available."))

        st.markdown("</div>", unsafe_allow_html=True)

    tabs = st.tabs(
        [
            "📋 Data Review",
            "📐 Calculations",
            "🔎 Problems",
            "🧠 Causes",
            "🧪 Checks",
            "🛠️ Actions",
            "🔧 Maintenance",
            "⚠️ Safety",
            "❓ Missing Data",
        ]
    )

    with tabs[0]:
        st.markdown("### Entered Data Review")
        display_list(report.get("entered_data_review", []))

    with tabs[1]:
        st.markdown("### Calculated Metrics")
        display_list(report.get("calculated_metrics", []))

    with tabs[2]:
        st.markdown("### Possible Problems")
        display_list(report.get("possible_problems", []))

    with tabs[3]:
        st.markdown("### Possible Causes")
        display_list(report.get("possible_causes", []))

    with tabs[4]:
        st.markdown("### Recommended Checks")
        display_list(report.get("recommended_checks", []))

    with tabs[5]:
        st.markdown("### Recommended Actions")
        display_list(report.get("recommended_actions", []))

    with tabs[6]:
        st.markdown("### Maintenance Advice")
        display_list(report.get("maintenance_advice", []))

    with tabs[7]:
        st.markdown("### Safety Warnings")

        safety_items = report.get("safety_warnings", [])

        if safety_items:
            for item in safety_items:
                st.markdown(
                    f"""
                    <div class="warning-box">
                        ⚠️ {html.escape(str(item))}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No additional AI safety warning was returned.")

    with tabs[8]:
        st.markdown("### Missing Information")
        display_list(report.get("missing_information", []))

    st.markdown("---")

    st.markdown("### 📥 Export Report")

    report_json = json.dumps(report, indent=2, ensure_ascii=False)
    report_markdown = report_to_markdown(report)

    download_col_1, download_col_2 = st.columns(2)

    with download_col_1:
        st.download_button(
            label="Download JSON Report",
            data=report_json,
            file_name="battery_ai_report.json",
            mime="application/json",
            use_container_width=True,
        )

    with download_col_2:
        st.download_button(
            label="Download Markdown Report",
            data=report_markdown,
            file_name="battery_ai_report.md",
            mime="text/markdown",
            use_container_width=True,
        )

    st.markdown(
        f"""
        <div class="info-box">
            ℹ️ <strong>Disclaimer:</strong>
            {html.escape(str(report.get("disclaimer", "This is preliminary decision support only.")))}
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer-note">
        Battery-AI provides preliminary decision support only.
        Always follow manufacturer instructions and consult a qualified technician.
        <br>
        Built with Python • Streamlit • Groq AI
    </div>
    """,
    unsafe_allow_html=True,
)
