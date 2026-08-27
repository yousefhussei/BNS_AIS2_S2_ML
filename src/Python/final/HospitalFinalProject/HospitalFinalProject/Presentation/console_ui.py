from Buissness.ParientManager import PatientManager
from Buissness.DoctorManager import DoctorManager
from Buissness.AppointementManager import AppointmentManager
from Buissness.PharmacyManager import PharmacyManager

class ConsoleUI:
    def __init__(self):
        self.patient_mgr = PatientManager()
        self.doctor_mgr = DoctorManager()
        self.appointment_mgr = AppointmentManager()
        self.pharmacy_mgr = PharmacyManager()

    def run(self):
        while True:
            print("\n=== Hospital Management System ===")
            print("1. Patients Management")
            print("2. Doctors Management")
            print("3. Appointments Management")
            print("4. Pharmacy & Medicines")
            print("0. Exit")
            
            choice = input("Enter your choice: ").strip()
            
            if choice == "1":
                self.patients_menu()
            elif choice == "2":
                self.doctors_menu()
            elif choice == "3":
                self.appointments_menu()
            elif choice == "4":
                self.pharmacy_menu()
            elif choice == "0":
                print("Goodbye!")
                break
            else:
                print("Invalid choice, please try again.")

    def patients_menu(self):
        print("\n--- Patients Management ---")
        print("1. Register New Patient")
        print("2. View All Patients")
        print("3. Delete Patient")
        sub_choice = input("Choose an operation: ").strip()

        if sub_choice == "1":
            pid = input("Patient ID: ")
            name = input("Name: ")
            age = int(input("Age: "))
            address = input("Address: ")
            phone = input("Phone: ")
            history = input("Medical History: ")
            self.patient_mgr.register_patient(name, age, address, phone, pid, history)
            print("Patient registered successfully!")
        elif sub_choice == "2":
            patients = self.patient_mgr.get_all_patients()
            print("\n--- Patients List ---")
            for p in patients:
                print(f"ID: {p.get('patient_id')} | Name: {p.get('name')} | Age: {p.get('age')} | Phone: {p.get('phone')} | History: {p.get('medical_history')}")
        elif sub_choice == "3":
            pid = input("Enter Patient ID to delete: ")
            self.patient_mgr.delete_patient(pid)
            print("Patient deleted successfully.")

    def doctors_menu(self):
        print("\n--- Doctors Management ---")
        print("1. Add New Doctor")
        print("2. View All Doctors")
        sub_choice = input("Choose an operation: ").strip()

        if sub_choice == "1":
            did = input("Doctor ID: ")
            name = input("Name: ")
            age = int(input("Age: "))
            address = input("Address: ")
            phone = input("Phone: ")
            spec = input("Specialization: ")
            dept = input("Department ID: ")
            self.doctor_mgr.add_doctor(name, age, address, phone, did, spec, dept)
            print("Doctor added successfully!")
        elif sub_choice == "2":
            docs = self.doctor_mgr.get_all_doctors()
            print("\n--- Doctors List ---")
            for d in docs:
                print(f"ID: {d.get('doctor_id')} | Name: {d.get('name')} | Spec: {d.get('specialization')} | Phone: {d.get('phone')}")

    def appointments_menu(self):
        print("\n--- Appointments Management ---")
        print("1. Book New Appointment")
        print("2. View Appointments")
        print("3. Cancel Appointment")
        sub_choice = input("Choose an operation: ").strip()

        if sub_choice == "1":
            aid = input("Appointment ID: ")
            pid = input("Patient ID: ")
            did = input("Doctor ID: ")
            dt = input("Date and Time (YYYY-MM-DD HH:MM): ")
            self.appointment_mgr.book_appointment(aid, pid, did, dt)
            print("Appointment booked successfully!")
        elif sub_choice == "2":
            appts = self.appointment_mgr.get_all_appointments()
            print("\n--- Appointments List ---")
            for a in appts:
                print(f"Appt ID: {a.get('appointment_id')} | Patient ID: {a.get('patient_id')} | Doctor ID: {a.get('doctor_id')} | Date: {a.get('date_time')} | Status: {a.get('status')}")
        elif sub_choice == "3":
            aid = input("Enter Appointment ID to cancel: ")
            self.appointment_mgr.cancel_appointment(aid)
            print("Appointment canceled successfully.")

    def pharmacy_menu(self):
        print("\n--- Pharmacy Management ---")
        print("1. Add New Medicine")
        print("2. View All Medicines")
        sub_choice = input("Choose an operation: ").strip()

        if sub_choice == "1":
            mid = input("Medicine ID: ")
            name = input("Medicine Name: ")
            price = float(input("Price: "))
            qty = int(input("Quantity: "))
            self.pharmacy_mgr.add_medicine(mid, name, price, qty)
            print("Medicine added successfully!")
        elif sub_choice == "2":
            meds = self.pharmacy_mgr.get_all_medicines()
            print("\n--- Medicines List ---")
            for m in meds:
                print(f"ID: {m.get('medicine_id')} | Name: {m.get('name')} | Price: {m.get('price')} | Qty: {m.get('quantity')}")