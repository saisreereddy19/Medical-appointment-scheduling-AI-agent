# data_setup.py
import pandas as pd
from faker import Faker
import random

def make_patients_csv(filename="patients.csv", n=50):
    fake = Faker()
    data = []
    for _ in range(n):
        dob = fake.date_of_birth(minimum_age=18, maximum_age=90).strftime("%Y-%m-%d")
        data.append({
            "name": fake.name(),
            "dob": dob,
            "doctor": random.choice(["Dr. Gray", "Dr. Brown", "Dr. Black"]),
            "location": fake.city(),
            "email": fake.email(),
            "phone": fake.phone_number(),
            "insurance_member_id": fake.bothify(text="???####"),
            "insurance_group": fake.bothify(text="G#"),
            "status": random.choice(["returning", "new"])
        })
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Fake patient data written to {filename}")

def make_doctor_schedule_xlsx(filename="doctor_schedule.xlsx"):
    import datetime
    slots = []
    doctors = ["Dr. Gray", "Dr. Brown", "Dr. Black"]
    today = datetime.date.today()
    for doctor in doctors:
        for day in range(3):  # 3 days
            date = (today + datetime.timedelta(days=day))
            for hour in range(9, 17):  # 9am to 4pm
                for m in [0,30]:
                    slot_time = f"{hour:02}:{m:02}"
                    slots.append({
                        "doctor": doctor,
                        "date": date.strftime("%Y-%m-%d"),
                        "time": slot_time,
                        "available": True
                    })
    df = pd.DataFrame(slots)
    df.to_excel(filename, index=False)
    print(f"Fake schedule written to {filename}")

make_patients_csv()
make_doctor_schedule_xlsx()
