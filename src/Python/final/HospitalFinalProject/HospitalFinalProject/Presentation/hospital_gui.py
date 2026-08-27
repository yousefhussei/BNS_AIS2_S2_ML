import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from tkinter import messagebox
from Buissness.ParientManager import PatientManager
from Buissness.DoctorManager import DoctorManager
from Buissness.AppointementManager import AppointmentManager
from Buissness.PharmacyManager import PharmacyManager

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class HospitalGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🏥 Hospital Management System - Professional GUI")
        self.geometry("1050x650")
        self.resizable(False, False)

        # Managers
        self.patient_mgr = PatientManager()
        self.doctor_mgr = DoctorManager()
        self.appointment_mgr = AppointmentManager()
        self.pharmacy_mgr = PharmacyManager()

        self.setup_sidebar()
        self.setup_main_container()
        
        # Start with Patients Frame
        self.show_patients()

    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        self.logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="🏥 Hospital\nManagement", 
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.logo_label.pack(padx=20, pady=30)

        # Sidebar Buttons
        self.btn_patients = ctk.CTkButton(self.sidebar, text="👥 إدارة المرضى", command=self.show_patients)
        self.btn_patients.pack(padx=20, pady=10, fill="x")

        self.btn_doctors = ctk.CTkButton(self.sidebar, text="👨‍⚕️ إدارة الأطباء", command=self.show_doctors)
        self.btn_doctors.pack(padx=20, pady=10, fill="x")

        self.btn_appointments = ctk.CTkButton(self.sidebar, text="📅 إدارة المواعيد", command=self.show_appointments)
        self.btn_appointments.pack(padx=20, pady=10, fill="x")

        self.btn_pharmacy = ctk.CTkButton(self.sidebar, text="💊 قسم الصيدلية", command=self.show_pharmacy)
        self.btn_pharmacy.pack(padx=20, pady=10, fill="x")

    def setup_main_container(self):
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        # Frames
        self.patients_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.doctors_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.appointments_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.pharmacy_frame = ctk.CTkFrame(self.container, fg_color="transparent")

        self.build_patients_ui(self.patients_frame)
        self.build_doctors_ui(self.doctors_frame)
        self.build_appointments_ui(self.appointments_frame)
        self.build_pharmacy_ui(self.pharmacy_frame)

    def hide_all_frames(self):
        self.patients_frame.pack_forget()
        self.doctors_frame.pack_forget()
        self.appointments_frame.pack_forget()
        self.pharmacy_frame.pack_forget()

    def show_patients(self):
        self.hide_all_frames()
        self.patients_frame.pack(fill="both", expand=True)
        self.load_patients()

    def show_doctors(self):
        self.hide_all_frames()
        self.doctors_frame.pack(fill="both", expand=True)
        self.load_doctors()

    def show_appointments(self):
        self.hide_all_frames()
        self.appointments_frame.pack(fill="both", expand=True)
        self.load_appointments()

    def show_pharmacy(self):
        self.hide_all_frames()
        self.pharmacy_frame.pack(fill="both", expand=True)
        self.load_medicines()

    # ================= 1. المرضى =================
    def build_patients_ui(self, parent):
        title = ctk.CTkLabel(parent, text="إدارة سجلات المرضى", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(anchor="w", pady=10)

        self.patients_box = ctk.CTkTextbox(parent, width=750, height=330, font=("Consolas", 13))
        self.patients_box.pack(pady=10, fill="both", expand=True)

        form_frame = ctk.CTkFrame(parent, fg_color="transparent")
        form_frame.pack(fill="x", pady=10)

        self.p_id = ctk.CTkEntry(form_frame, placeholder_text="ID", width=80)
        self.p_id.grid(row=0, column=0, padx=5)
        self.p_name = ctk.CTkEntry(form_frame, placeholder_text="الاسم", width=130)
        self.p_name.grid(row=0, column=1, padx=5)
        self.p_age = ctk.CTkEntry(form_frame, placeholder_text="العمر", width=70)
        self.p_age.grid(row=0, column=2, padx=5)
        self.p_phone = ctk.CTkEntry(form_frame, placeholder_text="الهاتف", width=120)
        self.p_phone.grid(row=0, column=3, padx=5)
        self.p_history = ctk.CTkEntry(form_frame, placeholder_text="السجل الطبي", width=140)
        self.p_history.grid(row=0, column=4, padx=5)

        btn_add = ctk.CTkButton(form_frame, text="تسجيل مريض", fg_color="green", width=100, command=self.add_patient)
        btn_add.grid(row=0, column=5, padx=5)

    def load_patients(self):
        self.patients_box.delete("0.0", "end")
        patients = self.patient_mgr.get_all_patients()
        header = f"{'ID':<8} | {'Name':<20} | {'Age':<6} | {'Phone':<15} | {'Medical History':<25}\n"
        header += "-" * 85 + "\n"
        self.patients_box.insert("end", header)
        for p in patients:
            row = f"{str(p.get('patient_id')):<8} | {str(p.get('name')):<20} | {str(p.get('age')):<6} | {str(p.get('phone')):<15} | {str(p.get('medical_history')):<25}\n"
            self.patients_box.insert("end", row)

    def add_patient(self):
        pid = self.p_id.get().strip()
        name = self.p_name.get().strip()
        age_str = self.p_age.get().strip()
        phone = self.p_phone.get().strip()
        history = self.p_history.get().strip()
        
        if not pid or not name or not age_str:
            messagebox.showerror("خطأ", "برجاء إدخال ID والاسم والعمر على الأقل!")
            return
            
        try:
            age = int(age_str)
            self.patient_mgr.register_patient(name, age, "N/A", phone, pid, history)
            messagebox.showinfo("نجاح", "تم تسجيل المريض بنجاح!")
            self.load_patients()
            self.p_id.delete(0, 'end')
            self.p_name.delete(0, 'end')
            self.p_age.delete(0, 'end')
            self.p_phone.delete(0, 'end')
            self.p_history.delete(0, 'end')
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ: {e}")

    # ================= 2. الأطباء =================
    def build_doctors_ui(self, parent):
        title = ctk.CTkLabel(parent, text="إدارة طاقم الأطباء", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(anchor="w", pady=10)

        self.doctors_box = ctk.CTkTextbox(parent, width=750, height=330, font=("Consolas", 13))
        self.doctors_box.pack(pady=10, fill="both", expand=True)

        form_frame = ctk.CTkFrame(parent, fg_color="transparent")
        form_frame.pack(fill="x", pady=10)

        self.d_id = ctk.CTkEntry(form_frame, placeholder_text="ID", width=80)
        self.d_id.grid(row=0, column=0, padx=5)
        self.d_name = ctk.CTkEntry(form_frame, placeholder_text="الاسم", width=130)
        self.d_name.grid(row=0, column=1, padx=5)
        self.d_spec = ctk.CTkEntry(form_frame, placeholder_text="التخصص", width=130)
        self.d_spec.grid(row=0, column=2, padx=5)
        self.d_phone = ctk.CTkEntry(form_frame, placeholder_text="الهاتف", width=120)
        self.d_phone.grid(row=0, column=3, padx=5)
        self.d_dept = ctk.CTkEntry(form_frame, placeholder_text="رقم القسم", width=90)
        self.d_dept.grid(row=0, column=4, padx=5)

        btn_add = ctk.CTkButton(form_frame, text="إضافة طبيب", fg_color="green", width=100, command=self.add_doctor)
        btn_add.grid(row=0, column=5, padx=5)

    def load_doctors(self):
        self.doctors_box.delete("0.0", "end")
        docs = self.doctor_mgr.get_all_doctors()
        header = f"{'ID':<8} | {'Name':<22} | {'Specialization':<20} | {'Phone':<15}\n"
        header += "-" * 75 + "\n"
        self.doctors_box.insert("end", header)
        for d in docs:
            row = f"{str(d.get('doctor_id')):<8} | {str(d.get('name')):<22} | {str(d.get('specialization')):<20} | {str(d.get('phone')):<15}\n"
            self.doctors_box.insert("end", row)

    def add_doctor(self):
        did = self.d_id.get().strip()
        name = self.d_name.get().strip()
        spec = self.d_spec.get().strip()
        phone = self.d_phone.get().strip()
        dept = self.d_dept.get().strip()

        if not did or not name:
            messagebox.showerror("خطأ", "برجاء إدخال ID والاسم على الأقل!")
            return

        try:
            self.doctor_mgr.add_doctor(name, 35, "N/A", phone, did, spec, dept)
            messagebox.showinfo("نجاح", "تم إضافة الطبيب بنجاح!")
            self.load_doctors()
            self.d_id.delete(0, 'end')
            self.d_name.delete(0, 'end')
            self.d_spec.delete(0, 'end')
            self.d_phone.delete(0, 'end')
            self.d_dept.delete(0, 'end')
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ: {e}")

    # ================= 3. المواعيد =================
    def build_appointments_ui(self, parent):
        title = ctk.CTkLabel(parent, text="إدارة مواعيد الكشف", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(anchor="w", pady=10)

        self.appts_box = ctk.CTkTextbox(parent, width=750, height=330, font=("Consolas", 13))
        self.appts_box.pack(pady=10, fill="both", expand=True)

        form_frame = ctk.CTkFrame(parent, fg_color="transparent")
        form_frame.pack(fill="x", pady=10)

        self.a_id = ctk.CTkEntry(form_frame, placeholder_text="رقم الموعد", width=90)
        self.a_id.grid(row=0, column=0, padx=5)
        self.a_pid = ctk.CTkEntry(form_frame, placeholder_text="رقم المريض", width=90)
        self.a_pid.grid(row=0, column=1, padx=5)
        self.a_did = ctk.CTkEntry(form_frame, placeholder_text="رقم الطبيب", width=90)
        self.a_did.grid(row=0, column=2, padx=5)
        self.a_dt = ctk.CTkEntry(form_frame, placeholder_text="YYYY-MM-DD HH:MM", width=160)
        self.a_dt.grid(row=0, column=3, padx=5)

        btn_add = ctk.CTkButton(form_frame, text="حجز موعد", fg_color="green", width=110, command=self.add_appointment)
        btn_add.grid(row=0, column=4, padx=5)

    def load_appointments(self):
        self.appts_box.delete("0.0", "end")
        appts = self.appointment_mgr.get_all_appointments()
        header = f"{'Appt ID':<10} | {'Patient ID':<12} | {'Doctor ID':<12} | {'Date & Time':<20} | {'Status':<10}\n"
        header += "-" * 75 + "\n"
        self.appts_box.insert("end", header)
        for a in appts:
            row = f"{str(a.get('appointment_id')):<10} | {str(a.get('patient_id')):<12} | {str(a.get('doctor_id')):<12} | {str(a.get('date_time')):<20} | {str(a.get('status')):<10}\n"
            self.appts_box.insert("end", row)

    def add_appointment(self):
        aid = self.a_id.get().strip()
        pid = self.a_pid.get().strip()
        did = self.a_did.get().strip()
        dt = self.a_dt.get().strip()

        if not aid or not pid or not did:
            messagebox.showerror("خطأ", "برجاء ملء جميع الحقول المطلوبة للحجز!")
            return

        try:
            self.appointment_mgr.book_appointment(aid, pid, did, dt)
            messagebox.showinfo("نجاح", "تم حجز الموعد بنجاح!")
            self.load_appointments()
            self.a_id.delete(0, 'end')
            self.a_pid.delete(0, 'end')
            self.a_did.delete(0, 'end')
            self.a_dt.delete(0, 'end')
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ: {e}")

    # ================= 4. الصيدلية =================
    def build_pharmacy_ui(self, parent):
        title = ctk.CTkLabel(parent, text="إدارة مخزن صيدلية المستشفى", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(anchor="w", pady=10)

        self.meds_box = ctk.CTkTextbox(parent, width=750, height=330, font=("Consolas", 13))
        self.meds_box.pack(pady=10, fill="both", expand=True)

        form_frame = ctk.CTkFrame(parent, fg_color="transparent")
        form_frame.pack(fill="x", pady=10)

        self.m_id = ctk.CTkEntry(form_frame, placeholder_text="رقم الدواء", width=90)
        self.m_id.grid(row=0, column=0, padx=5)
        self.m_name = ctk.CTkEntry(form_frame, placeholder_text="اسم الدواء", width=150)
        self.m_name.grid(row=0, column=1, padx=5)
        self.m_price = ctk.CTkEntry(form_frame, placeholder_text="السعر", width=90)
        self.m_price.grid(row=0, column=2, padx=5)
        self.m_qty = ctk.CTkEntry(form_frame, placeholder_text="الكمية", width=90)
        self.m_qty.grid(row=0, column=3, padx=5)

        btn_add = ctk.CTkButton(form_frame, text="إضافة دواء", fg_color="green", width=110, command=self.add_medicine)
        btn_add.grid(row=0, column=4, padx=5)

    def load_medicines(self):
        self.meds_box.delete("0.0", "end")
        meds = self.pharmacy_mgr.get_all_medicines()
        header = f"{'ID':<10} | {'Medicine Name':<25} | {'Price':<12} | {'Quantity':<10}\n"
        header += "-" * 65 + "\n"
        self.meds_box.insert("end", header)
        for m in meds:
            row = f"{str(m.get('medicine_id')):<10} | {str(m.get('name')):<25} | {str(m.get('price')):<12} | {str(m.get('quantity')):<10}\n"
            self.meds_box.insert("end", row)

    def add_medicine(self):
        mid = self.m_id.get().strip()
        name = self.m_name.get().strip()
        price_str = self.m_price.get().strip()
        qty_str = self.m_qty.get().strip()

        if not mid or not name or not price_str or not qty_str:
            messagebox.showerror("خطأ", "برجاء ملء جميع الحقول المطلوبة للإضافة!")
            return

        try:
            price = float(price_str)
            qty = int(qty_str)
            self.pharmacy_mgr.add_medicine(mid, name, price, qty)
            messagebox.showinfo("نجاح", "تم إضافة الدواء للمخزن بنجاح!")
            self.load_medicines()
            self.m_id.delete(0, 'end')
            self.m_name.delete(0, 'end')
            self.m_price.delete(0, 'end')
            self.m_qty.delete(0, 'end')
        except ValueError:
            messagebox.showerror("خطأ", "تأكد من إدخال أرقام صحيحة للسعر والكمية!")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ: {e}")

if __name__ == "__main__":
    app = HospitalGUI()
    app.mainloop()