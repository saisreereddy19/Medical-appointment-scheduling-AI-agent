import streamlit as st
import pandas as pd
from faker import Faker
import random
import os
from datetime import datetime

from langchain_ollama import OllamaLLM

PATIENTS_FILE = "patients.csv"
SCHEDULE_FILE = "doctor_schedule.xlsx"
APPT_FILE = "appointments.xlsx"
NEW_PATIENTS_FILE = "new_patients.csv"

# Doctor names list (customized)
doctor_names = ["Dr. Madhavi", "Dr. Krishna", "Dr. Teena", "Dr. Saisree", "Dr. Honey", "Dr. Bharatj"]

def make_patients_csv(filename=PATIENTS_FILE, n=50):
    fake = Faker()
    data = []
    for _ in range(n):
        dob = fake.date_of_birth(minimum_age=18, maximum_age=90).strftime("%Y-%m-%d")
        data.append({
            "name": fake.name(),
            "dob": dob,
            "doctor": random.choice(doctor_names),
            "location": fake.city(),
            "email": fake.email(),
            "phone": fake.phone_number(),
            "insurance_member_id": fake.bothify(text="???####"),
            "insurance_group": fake.bothify(text="G#"),
            "status": random.choice(["returning", "new"])
        })
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)

def make_doctor_schedule_xlsx(filename=SCHEDULE_FILE):
    import datetime
    slots = []
    today = datetime.date.today()
    for doctor in doctor_names:
        for day in range(3):
            date = (today + datetime.timedelta(days=day))
            for hour in range(9, 17):
                for m in [0, 30]:
                    slots.append({
                        "doctor": doctor,
                        "date": date.strftime("%Y-%m-%d"),
                        "time": f"{hour:02}:{m:02}",
                        "available": True
                    })
    df = pd.DataFrame(slots)
    df.to_excel(filename, index=False)

def save_new_patient(name, dob, doctor, location, email, phone, insurance_member_id, insurance_group, status="new"):
    df = pd.DataFrame([{
        "name": name,
        "dob": dob,
        "doctor": doctor,
        "location": location,
        "email": email,
        "phone": phone,
        "insurance_member_id": insurance_member_id,
        "insurance_group": insurance_group,
        "status": status
    }])
    if os.path.exists(NEW_PATIENTS_FILE) and os.path.getsize(NEW_PATIENTS_FILE) > 0:
        try:
            df_existing = pd.read_csv(NEW_PATIENTS_FILE)
            df_all = pd.concat([df_existing, df], ignore_index=True)
        except pd.errors.EmptyDataError:
            df_all = df
    else:
        df_all = df
    df_all.to_csv(NEW_PATIENTS_FILE, index=False)

def load_patients():
    return pd.read_csv(PATIENTS_FILE)

def load_schedule():
    return pd.read_excel(SCHEDULE_FILE)

def check_patient(name, dob, patients_df):
    person = patients_df[(patients_df['name'].str.lower() == name.lower()) & (patients_df['dob'] == dob)]
    return person

def available_slots(doctor, schedule_df):
    return schedule_df[(schedule_df['doctor'] == doctor) & (schedule_df['available'] == True)][['date','time']]

def book_appointment(schedule_df, doctor, patient_name, patient_dob, appt_type, appt_date, appt_time):
    idx = schedule_df[(schedule_df['doctor'] == doctor) &
                      (schedule_df['date'] == appt_date) &
                      (schedule_df['time'] == appt_time) &
                      (schedule_df['available'] == True)].index
    if idx.any():
        schedule_df.at[idx[0], 'available'] = False
        schedule_df.to_excel(SCHEDULE_FILE, index=False)
        appt_info = {
            "name": patient_name,
            "dob": patient_dob,
            "doctor": doctor,
            "appt_type": appt_type,
            "date": appt_date,
            "time": appt_time
        }
        if os.path.exists(APPT_FILE):
            appt_df = pd.read_excel(APPT_FILE)
            appt_df = pd.concat([appt_df, pd.DataFrame([appt_info])], ignore_index=True)
        else:
            appt_df = pd.DataFrame([appt_info])
        appt_df.to_excel(APPT_FILE, index=False)
        return True, appt_info
    return False, None

def send_reminders(email, appt_info):
    for i in range(1, 4):
        st.info(f"Reminder {i} sent to {email}")

def llm_confirmation_message(name, doctor, appt_time, appt_date):
    try:
        llm = OllamaLLM(model="gemma:2b")
        prompt = (
            f"Write a formal appointment confirmation for patient {name} "
            f"with {doctor} at {appt_time} on {appt_date}."
        )
        return llm.invoke(prompt)
    except Exception as e:
        return f"[LLM ERROR]: {str(e)}"

if not os.path.exists(PATIENTS_FILE):
    make_patients_csv()
if not os.path.exists(SCHEDULE_FILE):
    make_doctor_schedule_xlsx()

if "patient_looked_up" not in st.session_state:
    st.session_state.patient_looked_up = False
if "patient_rec" not in st.session_state:
    st.session_state.patient_rec = None
if "appt_type" not in st.session_state:
    st.session_state.appt_type = None
if "email" not in st.session_state:
    st.session_state.email = ""
if "location" not in st.session_state:
    st.session_state.location = ""
if "phone" not in st.session_state:
    st.session_state.phone = ""
if "insurance_member_id" not in st.session_state:
    st.session_state.insurance_member_id = ""
if "insurance_group" not in st.session_state:
    st.session_state.insurance_group = ""
if "slot_booked" not in st.session_state:
    st.session_state.slot_booked = False

st.title("MediCare AI Appointment Scheduler (LLM-powered)")

patients_df = load_patients()
schedule_df = load_schedule()

st.header("Book an Appointment")

name = st.text_input("Patient Name", key="name_input")
dob = st.text_input("Date of Birth (YYYY-MM-DD)", key="dob_input")

lookup_clicked = st.button("Lookup Patient")
if lookup_clicked:
    patient_rec = check_patient(name, dob, patients_df)
    st.session_state.patient_rec = patient_rec
    st.session_state.patient_looked_up = True
    if not patient_rec.empty:
        st.session_state.appt_type = "returning"
        st.session_state.email = patient_rec.iloc[0]["email"]
    else:
        st.session_state.appt_type = "new"
        st.session_state.email = ""
        st.session_state.location = ""
        st.session_state.phone = ""
        st.session_state.insurance_member_id = ""
        st.session_state.insurance_group = ""
    st.session_state.slot_booked = False

if st.session_state.patient_looked_up:
    if not st.session_state.patient_rec.empty:
        st.success("Returning Patient Detected")
        email = st.session_state.email
    else:
        st.success("New Patient - Intake Required")
        email = st.text_input("Enter your email address (for new patients)", key="email_input", value=st.session_state.email)
        location = st.text_input("City/Location", key="location_input", value=st.session_state.location)
        phone = st.text_input("Phone Number", key="phone_input", value=st.session_state.phone)
        insurance_member_id = st.text_input("Insurance Member ID", key="insurance_member_id_input", value=st.session_state.insurance_member_id)
        insurance_group = st.text_input("Insurance Group", key="insurance_group_input", value=st.session_state.insurance_group)
        st.session_state.email = email
        st.session_state.location = location
        st.session_state.phone = phone
        st.session_state.insurance_member_id = insurance_member_id
        st.session_state.insurance_group = insurance_group

    # Show appointment duration based on patient type
    if st.session_state.appt_type == "returning":
        duration = 30
    else:
        duration = 60
    st.info(f"Appointment Duration: {duration} minutes")

    doctor = st.selectbox("Choose Doctor", schedule_df['doctor'].unique(), key="doctor_select")
    slots = available_slots(doctor, schedule_df)
    if not slots.empty:
        slot_vals = [f"{d} {t}" for d, t in slots.values]
        slot_choice = st.selectbox("Available Slots", slot_vals, key="slot_select")
        if st.button("Book Selected Slot"):
            appt_date, appt_time = slot_choice.split()
            appt_type = st.session_state.appt_type
            booked, info = book_appointment(schedule_df, doctor, name, dob, appt_type, appt_date, appt_time)
            if booked:
                st.session_state.slot_booked = True
                st.success("Slot Booked!")
                st.success(f"Appointment Booked: {info}")
                st.info("Intake form (simulated) sent to your email.")
                send_reminders(st.session_state.email, info)
                if appt_type == "new":
                    save_new_patient(
                        name, dob, doctor,
                        st.session_state.location,
                        st.session_state.email,
                        st.session_state.phone,
                        st.session_state.insurance_member_id,
                        st.session_state.insurance_group)
                    st.info(f"New patient details recorded in {NEW_PATIENTS_FILE}")
                with st.spinner("Generating AI-powered confirmation..."):
                    conf_msg = llm_confirmation_message(name, doctor, appt_time, appt_date)
                    st.write("**LLM-Generated Confirmation:**")
                    st.write(conf_msg)
            else:
                st.error("Slot booking failed, please select another slot.")
    else:
        st.error("No slots available for selected doctor.")

elif not st.session_state.patient_looked_up:
    st.warning("Enter patient name and DOB and click 'Lookup Patient'.")

st.markdown("---")
st.caption("Powered by Streamlit, pandas, Faker, LangChain, Ollama.")
