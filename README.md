🏥 Medical Appointment Scheduling AI Agent

An AI-powered scheduling assistant that automates patient bookings, reduces no-shows, and streamlines clinic operations.  

---

Features
- Patient Greeting & Intake: Collects patient details (Name, DOB, Doctor, Location)
- Patient Lookup: Detects new vs. returning patients from a mock database (CSV)
- Smart Scheduling: Assigns 60 min slots for new patients and 30 min slots for returning patients
- Calendar Integration: Reads/writes from a simulated calendar (Excel file)
- Insurance Collection: Captures carrier, member ID, and group number
- Appointment Confirmation: Exports booking details into Excel for admin review
- Form Distribution: Sends patient intake forms after confirmation
- Reminder System: Sends automated email/SMS reminders with follow-ups

---

Tech Stack
- Python 3.10+
- LangChain
- LangGraph
- Ollama (LLM backend, open-source)
- Streamlit
- Pandas
- smtplib (for email notifications)

---

Project Structure
ai_scheduling_agent/
│── app.py                Streamlit chatbot interface  
│── agent.py              Core AI agent logic  
│── patients.csv          Mock patient database (synthetic data)  
│── doctor_schedule.xlsx  Mock doctor availability  
│── requirements.txt      Dependencies  
│── README.md             Project documentation  

---

Setup Instructions

1. Clone the repo
   git clone https://github.com/saisreereddy19/Medical-appointment-scheduling-AI-agent.git
   cd Medical-appointment-scheduling-AI-agent

2. Create a virtual environment
   python -m venv venv  
   source venv/bin/activate   # On Mac/Linux  
   venv\Scripts\activate      # On Windows  

3. Install dependencies
   pip install -r requirements.txt

4. Run the Streamlit app
   streamlit run app.py

---

Example Flow
1. User greets the assistant → provides Name, DOB, Doctor, and Location  
2. Agent checks database → identifies if the patient is new or returning  
3. Agent suggests available slots → books based on doctor schedule  
4. Appointment confirmed → details exported to Excel  
5. Patient intake form + reminders sent via Email/SMS  

---

Author  
Saisree Reddy  
Medical Appointment Scheduling AI Agent
