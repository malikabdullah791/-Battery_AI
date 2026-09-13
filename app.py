import os, json
import streamlit as st
from groq import Groq

APP_TITLE = 'Battery-AI: Intelligent Battery Health & Diagnostic Assistant'
MODEL = os.getenv('GROQ_MODEL', 'openai/gpt-oss-120b')


def get_key():
    try:
        key = st.secrets.get('GROQ_API_KEY')
    except Exception:
        key = None
    return key or os.getenv('GROQ_API_KEY')


def validate(data):
    errors = []
    for key in ['rated_voltage', 'rated_capacity']:
        if data[key] <= 0:
            errors.append(f'{key.replace("_", " ").title()} must be greater than zero.')
    for key in ['measured_voltage', 'measured_capacity', 'charging_voltage', 'charging_current', 'load_current', 'resistance', 'age']:
        if data[key] < 0:
            errors.append(f'{key.replace("_", " ").title()} cannot be negative.')
    if data['specific_gravity'] is not None and data['specific_gravity'] <= 0:
        errors.append('Specific gravity must be greater than zero when provided.')
    return errors


def calculate(data):
    health = round(data['measured_capacity'] / data['rated_capacity'] * 100, 1)
    status = 'Acceptable capacity' if health >= 80 else 'Reduced capacity' if health >= 60 else 'Poor capacity'
    return {'capacity_health_percent': health, 'capacity_status': status,
            'voltage_difference': round(data['measured_voltage'] - data['rated_voltage'], 2)}


def rules(data, metrics):
    warnings = []
    if metrics['capacity_health_percent'] < 80:
        warnings.append('Measured capacity is below 80% of rated capacity.')
    if data['measured_voltage'] < data['rated_voltage'] * 0.90:
        warnings.append('Measured voltage is notably below the entered rated voltage; state of charge and test conditions may affect this.')
    if data['resistance'] > 0:
        warnings.append("Compare internal resistance with the manufacturer's specification and the same test method.")
    if data['battery_type'] in ['Lead-acid', 'Tubular', 'AGM', 'Gel', 'VRLA'] and data['specific_gravity'] is None:
        warnings.append('Specific gravity was not provided; use it only when appropriate for the battery design.')
    if data['battery_type'] == 'Lithium-ion':
        warnings.append('Use manufacturer/BMS-specific checks for lithium-ion batteries; do not apply lead-acid procedures.')
    if data['symptom'] in ['Swelling', 'Overheating']:
        warnings.append('Serious safety symptom reported: stop use if unsafe and contact a qualified technician.')
    return warnings or ['No immediate rule-based warning was generated.']


def prompt(data, metrics, warnings):
    return f'''You are a careful battery-domain expert. Create a preliminary battery health and troubleshooting report.
This is decision support, not a guaranteed diagnosis. Do not invent measurements. Use simple English. Do not give dangerous instructions. For swelling, leakage, smoke, sparks, or overheating, recommend stopping use and contacting a qualified technician. Do not apply lead-acid procedures to lithium-ion batteries. Return valid JSON only.

DATA:\n{json.dumps(data, indent=2)}\nMETRICS:\n{json.dumps(metrics, indent=2)}\nRULE WARNINGS:\n{json.dumps(warnings, indent=2)}

Return exactly these fields: overall_status, health_summary, calculated_health, observed_problems, possible_causes, technical_explanation, recommended_tests, corrective_actions, maintenance_suggestions, risk_warnings, missing_information, final_summary, disclaimer. Lists must be JSON arrays.'''


def ai_report(data, metrics, warnings):
    key = get_key()
    if not key:
        raise ValueError('GROQ_API_KEY is missing. Add it to Streamlit Secrets or your environment.')
    client = Groq(api_key=key)
    result = client.chat.completions.create(
        model=MODEL,
        messages=[{'role': 'system', 'content': 'Return only valid JSON.'}, {'role': 'user', 'content': prompt(data, metrics, warnings)}],
        temperature=0.2,
        max_completion_tokens=5000,
    )
    text = (result.choices[0].message.content or '').strip().replace('```json', '').replace('```', '').strip()
    return json.loads(text)


def show_list(title, value):
    st.subheader(title)
    if isinstance(value, list):
        for item in value:
            st.markdown(f'- {item}')
    else:
        st.write(value or 'Not available')


def main():
    st.set_page_config(page_title='Battery-AI', page_icon='🔋', layout='wide')
    st.title('🔋 Battery-AI')
    st.caption('Intelligent Battery Health & Diagnostic Assistant — preliminary decision support.')

    with st.sidebar:
        st.header('Battery Information')
        battery_type = st.selectbox('Battery Type', ['Lead-acid', 'Tubular', 'AGM', 'Gel', 'VRLA', 'Lithium-ion', 'Other'])
        brand_choice = st.selectbox('Company / Brand', ['Volta', 'Osaka', 'Exide', 'Phoenix', 'AGS', 'Atlas', 'Narada', 'Other'])
        brand = st.text_input('Custom Company / Brand') if brand_choice == 'Other' else brand_choice
        application = st.selectbox('Application', ['Motorcycle', 'Car', 'UPS', 'Solar system', 'Industrial', 'EV', 'Other'])
        symptom_choice = st.selectbox('Main Symptom', ['Low backup time', 'Slow cranking', 'Not charging', 'Overheating', 'Swelling', 'Voltage dropping', 'Self-discharge', 'Other / custom'])
        symptom = st.text_input('Custom Symptom') if symptom_choice == 'Other / custom' else symptom_choice
        rated_voltage = st.number_input('Rated Voltage (V)', min_value=0.0, value=12.0, step=0.1)
        measured_voltage = st.number_input('Measured Voltage (V)', min_value=0.0, value=12.0, step=0.1)
        rated_capacity = st.number_input('Rated Capacity (Ah)', min_value=0.0, value=100.0, step=1.0)
        measured_capacity = st.number_input('Measured Capacity (Ah)', min_value=0.0, value=80.0, step=1.0)
        charging_voltage = st.number_input('Charging Voltage (V)', min_value=0.0, value=14.0, step=0.1)
        charging_current = st.number_input('Charging Current (A)', min_value=0.0, value=5.0, step=0.1)
        load_current = st.number_input('Load Current (A)', min_value=0.0, value=5.0, step=0.1)
        resistance = st.number_input('Internal Resistance (mΩ, optional)', min_value=0.0, value=0.0, step=0.1)
        age = st.number_input('Battery Age (years)', min_value=0.0, value=1.0, step=0.5)
        sg = st.number_input('Specific Gravity (optional)', min_value=0.0, value=0.0, step=0.001, format='%.3f')
        observations = st.text_area('Additional Observations')
        generate = st.button('🚀 Generate Battery Report', type='primary', use_container_width=True)

    if generate:
        data = {'battery_type': battery_type, 'company': brand or 'Not provided', 'application': application, 'symptom': symptom or 'Not provided', 'rated_voltage': rated_voltage, 'measured_voltage': measured_voltage, 'rated_capacity': rated_capacity, 'measured_capacity': measured_capacity, 'charging_voltage': charging_voltage, 'charging_current': charging_current, 'load_current': load_current, 'resistance': resistance, 'age': age, 'specific_gravity': None if sg == 0 else sg, 'observations': observations or 'Not provided'}
        errors = validate(data)
        if errors:
            for error in errors: st.error(error)
            return
        metrics = calculate(data)
        warnings = rules(data, metrics)
        st.header('Calculated Metrics')
        c1, c2, c3 = st.columns(3)
        c1.metric('Capacity Health', f"{metrics['capacity_health_percent']}%")
        c2.metric('Capacity Status', metrics['capacity_status'])
        c3.metric('Voltage Difference', f"{metrics['voltage_difference']} V")
        st.subheader('Rule-Based Warnings')
        for warning in warnings: st.warning(warning)
        with st.spinner('Generating report with Groq AI...'):
            try:
                report = ai_report(data, metrics, warnings)
                st.header('AI Diagnostic Report')
                for key, title in [('health_summary','Health Summary'), ('observed_problems','Observed Problems'), ('possible_causes','Possible Causes'), ('technical_explanation','Technical Explanation'), ('recommended_tests','Recommended Tests'), ('corrective_actions','Corrective Actions'), ('maintenance_suggestions','Maintenance Suggestions'), ('risk_warnings','Risk Warnings'), ('missing_information','Missing Information'), ('final_summary','Final Summary')]: show_list(title, report.get(key))
                st.warning(report.get('disclaimer', 'Preliminary assessment only; consult a qualified technician.'))
                st.download_button('⬇️ Download JSON Report', json.dumps({'data': data, 'metrics': metrics, 'warnings': warnings, 'report': report}, indent=2), 'battery_ai_report.json', 'application/json')
            except Exception as error:
                st.error(f'Unable to generate report: {error}')

    st.divider()
    st.caption('Safety: Do not use, puncture, short-circuit, or charge a swollen, leaking, smoking, or overheating battery. Contact a qualified technician.')


if __name__ == '__main__':
    main()
