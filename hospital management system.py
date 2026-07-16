import json
import os
import uuid
from datetime import datetime, date

DATA_DIR = "hms_data"
PATIENTS_FILE = os.path.join(DATA_DIR, "patients.json")
DOCTORS_FILE = os.path.join(DATA_DIR, "doctors.json")
APPOINTMENTS_FILE = os.path.join(DATA_DIR, "appointments.json")
BILLS_FILE = os.path.join(DATA_DIR, "bills.json")
WARDS_FILE = os.path.join(DATA_DIR, "wards.json")

DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M"

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    for file_path in [PATIENTS_FILE, DOCTORS_FILE, APPOINTMENTS_FILE, BILLS_FILE]:
        if not os.path.exists(file_path):
            save_json(file_path, [])

    if not os.path.exists(WARDS_FILE):
        default_wards = [
            {"ward_id": "W1", "ward_name": "General Ward", "total_beds": 10, "occupied_beds": []},
            {"ward_id": "W2", "ward_name": "ICU", "total_beds": 5, "occupied_beds": []},
            {"ward_id": "W3", "ward_name": "Private Ward", "total_beds": 6, "occupied_beds": []},
            {"ward_id": "W4", "ward_name": "Pediatric Ward", "total_beds": 8, "occupied_beds": []},
        ]
        save_json(WARDS_FILE, default_wards)

def load_json(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def generate_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:6].upper()}"

def input_nonempty(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("  This field cannot be empty. Try again.")

def input_int(prompt, min_val=None, max_val=None):
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
            if min_val is not None and value < min_val:
                print(f"  Value must be >= {min_val}.")
                continue
            if max_val is not None and value > max_val:
                print(f"  Value must be <= {max_val}.")
                continue
            return value
        except ValueError:
            print("  Please enter a valid whole number.")

def input_float(prompt, min_val=0):
    while True:
        raw = input(prompt).strip()
        try:
            value = float(raw)
            if value < min_val:
                print(f"  Value must be >= {min_val}.")
                continue
            return value
        except ValueError:
            print("  Please enter a valid number.")

def input_date(prompt):
    while True:
        raw = input(f"{prompt} (YYYY-MM-DD): ").strip()
        try:
            datetime.strptime(raw, DATE_FORMAT)
            return raw
        except ValueError:
            print("  Invalid date format. Example: 2026-07-16")

def press_enter():
    input("\nPress Enter to continue...")

def print_header(title):
    print("\n" + "=" * 60)
    print(title.center(60))
    print("=" * 60)

def print_table(rows, headers):
    if not rows:
        print("  No records found.")
        return
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    def fmt_row(row):
        return " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))

    print(fmt_row(headers))
    print("-+-".join("-" * w for w in col_widths))
    for row in rows:
        print(fmt_row(row))

class PatientManager:
    def __init__(self):
        self.patients = load_json(PATIENTS_FILE)

    def save(self):
        save_json(PATIENTS_FILE, self.patients)

    def add_patient(self):
        print_header("ADD NEW PATIENT")
        patient = {
            "patient_id": generate_id("P"),
            "name": input_nonempty("Full Name: "),
            "age": input_int("Age: ", min_val=0, max_val=130),
            "gender": input_nonempty("Gender (M/F/O): ").upper(),
            "phone": input_nonempty("Phone Number: "),
            "address": input_nonempty("Address: "),
            "blood_group": input_nonempty("Blood Group (e.g. O+): ").upper(),
            "admitted": False,
            "ward_id": None,
            "bed_no": None,
            "registered_on": datetime.now().strftime(DATETIME_FORMAT),
        }
        self.patients.append(patient)
        self.save()
        print(f"\n✔ Patient registered successfully! Patient ID: {patient['patient_id']}")

    def view_all(self):
        print_header("ALL PATIENTS")
        rows = [
            (p["patient_id"], p["name"], p["age"], p["gender"], p["phone"],
             "Admitted" if p["admitted"] else "OPD")
            for p in self.patients
        ]
        print_table(rows, ["ID", "Name", "Age", "Gender", "Phone", "Status"])

    def find_patient(self, patient_id):
        for p in self.patients:
            if p["patient_id"] == patient_id:
                return p
        return None

    def search_patient(self):
        print_header("SEARCH PATIENT")
        term = input_nonempty("Enter Patient ID or Name (partial ok): ").lower()
        results = [
            p for p in self.patients
            if term in p["patient_id"].lower() or term in p["name"].lower()
        ]
        rows = [
            (p["patient_id"], p["name"], p["age"], p["gender"], p["phone"],
             "Admitted" if p["admitted"] else "OPD")
            for p in results
        ]
        print_table(rows, ["ID", "Name", "Age", "Gender", "Phone", "Status"])

    def update_patient(self):
        print_header("UPDATE PATIENT")
        pid = input_nonempty("Enter Patient ID to update: ")
        p = self.find_patient(pid)
        if not p:
            print("✘ Patient not found.")
            return
        print("Leave blank to keep the current value.")
        name = input(f"Name [{p['name']}]: ").strip()
        phone = input(f"Phone [{p['phone']}]: ").strip()
        address = input(f"Address [{p['address']}]: ").strip()
        if name:
            p["name"] = name
        if phone:
            p["phone"] = phone
        if address:
            p["address"] = address
        self.save()
        print("✔ Patient updated successfully.")

    def delete_patient(self):
        print_header("DELETE PATIENT")
        pid = input_nonempty("Enter Patient ID to delete: ")
        p = self.find_patient(pid)
        if not p:
            print("✘ Patient not found.")
            return
        confirm = input(f"Are you sure you want to delete {p['name']}? (y/n): ").lower()
        if confirm == "y":
            self.patients.remove(p)
            self.save()
            print("✔ Patient deleted.")
        else:
            print("Cancelled.")

class DoctorManager:
    def __init__(self):
        self.doctors = load_json(DOCTORS_FILE)

    def save(self):
        save_json(DOCTORS_FILE, self.doctors)

    def add_doctor(self):
        print_header("ADD NEW DOCTOR")
        doctor = {
            "doctor_id": generate_id("D"),
            "name": input_nonempty("Doctor Name: "),
            "specialization": input_nonempty("Specialization (e.g. Cardiology): "),
            "phone": input_nonempty("Phone Number: "),
            "consultation_fee": input_float("Consultation Fee: "),
            "available_days": input_nonempty("Available Days (e.g. Mon-Fri): "),
        }
        self.doctors.append(doctor)
        self.save()
        print(f"\n✔ Doctor added successfully! Doctor ID: {doctor['doctor_id']}")

    def view_all(self):
        print_header("ALL DOCTORS")
        rows = [
            (d["doctor_id"], d["name"], d["specialization"], d["phone"],
             f"₹{d['consultation_fee']:.2f}")
            for d in self.doctors
        ]
        print_table(rows, ["ID", "Name", "Specialization", "Phone", "Fee"])

    def find_doctor(self, doctor_id):
        for d in self.doctors:
            if d["doctor_id"] == doctor_id:
                return d
        return None

    def search_doctor(self):
        print_header("SEARCH DOCTOR")
        term = input_nonempty("Enter Doctor ID, Name, or Specialization: ").lower()
        results = [
            d for d in self.doctors
            if term in d["doctor_id"].lower()
            or term in d["name"].lower()
            or term in d["specialization"].lower()
        ]
        rows = [
            (d["doctor_id"], d["name"], d["specialization"], d["phone"],
             f"₹{d['consultation_fee']:.2f}")
            for d in results
        ]
        print_table(rows, ["ID", "Name", "Specialization", "Phone", "Fee"])

    def update_doctor(self):
        print_header("UPDATE DOCTOR")
        did = input_nonempty("Enter Doctor ID to update: ")
        d = self.find_doctor(did)
        if not d:
            print("✘ Doctor not found.")
            return
        print("Leave blank to keep the current value.")
        name = input(f"Name [{d['name']}]: ").strip()
        phone = input(f"Phone [{d['phone']}]: ").strip()
        fee = input(f"Consultation Fee [{d['consultation_fee']}]: ").strip()
        if name:
            d["name"] = name
        if phone:
            d["phone"] = phone
        if fee:
            try:
                d["consultation_fee"] = float(fee)
            except ValueError:
                print("  Invalid fee, keeping old value.")
        self.save()
        print("✔ Doctor updated successfully.")

    def delete_doctor(self):
        print_header("DELETE DOCTOR")
        did = input_nonempty("Enter Doctor ID to delete: ")
        d = self.find_doctor(did)
        if not d:
            print("✘ Doctor not found.")
            return
        confirm = input(f"Are you sure you want to delete Dr. {d['name']}? (y/n): ").lower()
        if confirm == "y":
            self.doctors.remove(d)
            self.save()
            print("✔ Doctor deleted.")
        else:
            print("Cancelled.")

class WardManager:
    def __init__(self):
        self.wards = load_json(WARDS_FILE)

    def save(self):
        save_json(WARDS_FILE, self.wards)

    def view_all(self):
        print_header("WARD / BED AVAILABILITY")
        rows = []
        for w in self.wards:
            free = w["total_beds"] - len(w["occupied_beds"])
            rows.append((w["ward_id"], w["ward_name"], w["total_beds"], len(w["occupied_beds"]), free))
        print_table(rows, ["Ward ID", "Ward Name", "Total Beds", "Occupied", "Free"])

    def find_ward(self, ward_id):
        for w in self.wards:
            if w["ward_id"] == ward_id:
                return w
        return None

    def assign_bed(self, patient_id):
        self.view_all()
        ward_id = input_nonempty("\nEnter Ward ID to admit patient into: ").upper()
        ward = self.find_ward(ward_id)
        if not ward:
            print("✘ Invalid Ward ID.")
            return None, None
        if len(ward["occupied_beds"]) >= ward["total_beds"]:
            print("✘ No free beds in this ward.")
            return None, None
        bed_no = 1
        occupied_nums = {b["bed_no"] for b in ward["occupied_beds"]}
        while bed_no in occupied_nums:
            bed_no += 1
        ward["occupied_beds"].append({"bed_no": bed_no, "patient_id": patient_id})
        self.save()
        print(f"✔ Assigned Bed #{bed_no} in {ward['ward_name']}.")
        return ward_id, bed_no

    def release_bed(self, ward_id, bed_no):
        ward = self.find_ward(ward_id)
        if not ward:
            return
        ward["occupied_beds"] = [
            b for b in ward["occupied_beds"] if not (b["bed_no"] == bed_no)
        ]
        self.save()

class AdmissionManager:
    def __init__(self, patient_mgr: PatientManager, ward_mgr: WardManager):
        self.patient_mgr = patient_mgr
        self.ward_mgr = ward_mgr

    def admit_patient(self):
        print_header("ADMIT PATIENT")
        pid = input_nonempty("Enter Patient ID: ")
        p = self.patient_mgr.find_patient(pid)
        if not p:
            print("✘ Patient not found.")
            return
        if p["admitted"]:
            print("✘ Patient is already admitted.")
            return
        ward_id, bed_no = self.ward_mgr.assign_bed(pid)
        if ward_id is None:
            return
        p["admitted"] = True
        p["ward_id"] = ward_id
        p["bed_no"] = bed_no
        self.patient_mgr.save()
        print(f"✔ {p['name']} has been admitted.")

    def discharge_patient(self):
        print_header("DISCHARGE PATIENT")
        pid = input_nonempty("Enter Patient ID: ")
        p = self.patient_mgr.find_patient(pid)
        if not p:
            print("✘ Patient not found.")
            return
        if not p["admitted"]:
            print("✘ Patient is not currently admitted.")
            return
        self.ward_mgr.release_bed(p["ward_id"], p["bed_no"])
        p["admitted"] = False
        p["ward_id"] = None
        p["bed_no"] = None
        self.patient_mgr.save()
        print(f"✔ {p['name']} has been discharged.")

class AppointmentManager:
    def __init__(self, patient_mgr: PatientManager, doctor_mgr: DoctorManager):
        self.appointments = load_json(APPOINTMENTS_FILE)
        self.patient_mgr = patient_mgr
        self.doctor_mgr = doctor_mgr

    def save(self):
        save_json(APPOINTMENTS_FILE, self.appointments)

    def book_appointment(self):
        print_header("BOOK APPOINTMENT")
        pid = input_nonempty("Enter Patient ID: ")
        patient = self.patient_mgr.find_patient(pid)
        if not patient:
            print("✘ Patient not found. Please register the patient first.")
            return

        self.doctor_mgr.view_all()
        did = input_nonempty("\nEnter Doctor ID: ")
        doctor = self.doctor_mgr.find_doctor(did)
        if not doctor:
            print("✘ Doctor not found.")
            return

        appt_date = input_date("Appointment Date")
        appt_time = input_nonempty("Appointment Time (e.g. 14:30): ")

        appointment = {
            "appointment_id": generate_id("A"),
            "patient_id": pid,
            "patient_name": patient["name"],
            "doctor_id": did,
            "doctor_name": doctor["name"],
            "date": appt_date,
            "time": appt_time,
            "status": "Scheduled",
        }
        self.appointments.append(appointment)
        self.save()
        print(f"\n✔ Appointment booked! Appointment ID: {appointment['appointment_id']}")

    def view_all(self):
        print_header("ALL APPOINTMENTS")
        rows = [
            (a["appointment_id"], a["patient_name"], a["doctor_name"], a["date"], a["time"], a["status"])
            for a in self.appointments
        ]
        print_table(rows, ["ID", "Patient", "Doctor", "Date", "Time", "Status"])

    def cancel_appointment(self):
        print_header("CANCEL APPOINTMENT")
        aid = input_nonempty("Enter Appointment ID to cancel: ")
        for a in self.appointments:
            if a["appointment_id"] == aid:
                if a["status"] == "Cancelled":
                    print("✘ Appointment is already cancelled.")
                    return
                a["status"] = "Cancelled"
                self.save()
                print("✔ Appointment cancelled.")
                return
        print("✘ Appointment not found.")

    def find_appointment(self, appointment_id):
        for a in self.appointments:
            if a["appointment_id"] == appointment_id:
                return a
        return None

class BillingManager:
    def __init__(self, patient_mgr: PatientManager):
        self.bills = load_json(BILLS_FILE)
        self.patient_mgr = patient_mgr

    def save(self):
        save_json(BILLS_FILE, self.bills)

    def generate_bill(self):
        print_header("GENERATE BILL")
        pid = input_nonempty("Enter Patient ID: ")
        patient = self.patient_mgr.find_patient(pid)
        if not patient:
            print("✘ Patient not found.")
            return

        print("Enter charges below. Type 'done' as item name when finished.\n")
        items = []
        while True:
            name = input("Item / Service name (or 'done'): ").strip()
            if name.lower() == "done":
                break
            if not name:
                continue
            cost = input_float(f"  Cost for '{name}': ")
            items.append({"item": name, "cost": cost})

        if not items:
            print("✘ No items entered. Bill not generated.")
            return

        subtotal = sum(i["cost"] for i in items)
        tax = round(subtotal * 0.05, 2)  # 5% tax
        total = round(subtotal + tax, 2)

        bill = {
            "bill_id": generate_id("B"),
            "patient_id": pid,
            "patient_name": patient["name"],
            "items": items,
            "subtotal": subtotal,
            "tax": tax,
            "total": total,
            "date": datetime.now().strftime(DATETIME_FORMAT),
            "paid": False,
        }
        self.bills.append(bill)
        self.save()
        self.print_invoice(bill)

    def print_invoice(self, bill):
        print("\n" + "-" * 40)
        print(f"INVOICE - {bill['bill_id']}".center(40))
        print("-" * 40)
        print(f"Patient : {bill['patient_name']}")
        print(f"Date    : {bill['date']}")
        print("-" * 40)
        for item in bill["items"]:
            print(f"{item['item']:<28}₹{item['cost']:>8.2f}")
        print("-" * 40)
        print(f"{'Subtotal':<28}₹{bill['subtotal']:>8.2f}")
        print(f"{'Tax (5%)':<28}₹{bill['tax']:>8.2f}")
        print(f"{'TOTAL':<28}₹{bill['total']:>8.2f}")
        print("-" * 40)
        print(f"Status  : {'PAID' if bill['paid'] else 'UNPAID'}")
        print("-" * 40)

    def view_all(self):
        print_header("ALL BILLS")
        rows = [
            (b["bill_id"], b["patient_name"], f"₹{b['total']:.2f}",
             "Paid" if b["paid"] else "Unpaid", b["date"])
            for b in self.bills
        ]
        print_table(rows, ["Bill ID", "Patient", "Total", "Status", "Date"])

    def mark_paid(self):
        print_header("MARK BILL AS PAID")
        bid = input_nonempty("Enter Bill ID: ")
        for b in self.bills:
            if b["bill_id"] == bid:
                if b["paid"]:
                    print("✘ Bill is already marked as paid.")
                    return
                b["paid"] = True
                self.save()
                print("✔ Bill marked as paid.")
                return
        print("✘ Bill not found.")

    def view_invoice(self):
        print_header("VIEW INVOICE")
        bid = input_nonempty("Enter Bill ID: ")
        for b in self.bills:
            if b["bill_id"] == bid:
                self.print_invoice(b)
                return
        print("✘ Bill not found.")

class HospitalManagementSystem:
    def __init__(self):
        ensure_data_dir()
        self.patient_mgr = PatientManager()
        self.doctor_mgr = DoctorManager()
        self.ward_mgr = WardManager()
        self.admission_mgr = AdmissionManager(self.patient_mgr, self.ward_mgr)
        self.appointment_mgr = AppointmentManager(self.patient_mgr, self.doctor_mgr)
        self.billing_mgr = BillingManager(self.patient_mgr)

    def patient_menu(self):
        while True:
            print_header("PATIENT MANAGEMENT")
            print("1. Add New Patient")
            print("2. View All Patients")
            print("3. Search Patient")
            print("4. Update Patient")
            print("5. Delete Patient")
            print("0. Back to Main Menu")
            choice = input("\nEnter your choice: ").strip()

            if choice == "1":
                self.patient_mgr.add_patient()
            elif choice == "2":
                self.patient_mgr.view_all()
            elif choice == "3":
                self.patient_mgr.search_patient()
            elif choice == "4":
                self.patient_mgr.update_patient()
            elif choice == "5":
                self.patient_mgr.delete_patient()
            elif choice == "0":
                return
            else:
                print("✘ Invalid choice.")
            press_enter()

    def doctor_menu(self):
        while True:
            print_header("DOCTOR MANAGEMENT")
            print("1. Add New Doctor")
            print("2. View All Doctors")
            print("3. Search Doctor")
            print("4. Update Doctor")
            print("5. Delete Doctor")
            print("0. Back to Main Menu")
            choice = input("\nEnter your choice: ").strip()

            if choice == "1":
                self.doctor_mgr.add_doctor()
            elif choice == "2":
                self.doctor_mgr.view_all()
            elif choice == "3":
                self.doctor_mgr.search_doctor()
            elif choice == "4":
                self.doctor_mgr.update_doctor()
            elif choice == "5":
                self.doctor_mgr.delete_doctor()
            elif choice == "0":
                return
            else:
                print("✘ Invalid choice.")
            press_enter()

    def appointment_menu(self):
        while True:
            print_header("APPOINTMENT MANAGEMENT")
            print("1. Book Appointment")
            print("2. View All Appointments")
            print("3. Cancel Appointment")
            print("0. Back to Main Menu")
            choice = input("\nEnter your choice: ").strip()

            if choice == "1":
                self.appointment_mgr.book_appointment()
            elif choice == "2":
                self.appointment_mgr.view_all()
            elif choice == "3":
                self.appointment_mgr.cancel_appointment()
            elif choice == "0":
                return
            else:
                print("✘ Invalid choice.")
            press_enter()

    def admission_menu(self):
        while True:
            print_header("ADMISSION / WARD MANAGEMENT")
            print("1. Admit Patient")
            print("2. Discharge Patient")
            print("3. View Ward / Bed Availability")
            print("0. Back to Main Menu")
            choice = input("\nEnter your choice: ").strip()

            if choice == "1":
                self.admission_mgr.admit_patient()
            elif choice == "2":
                self.admission_mgr.discharge_patient()
            elif choice == "3":
                self.ward_mgr.view_all()
            elif choice == "0":
                return
            else:
                print("✘ Invalid choice.")
            press_enter()

    def billing_menu(self):
        while True:
            print_header("BILLING")
            print("1. Generate New Bill")
            print("2. View All Bills")
            print("3. View Specific Invoice")
            print("4. Mark Bill as Paid")
            print("0. Back to Main Menu")
            choice = input("\nEnter your choice: ").strip()

            if choice == "1":
                self.billing_mgr.generate_bill()
            elif choice == "2":
                self.billing_mgr.view_all()
            elif choice == "3":
                self.billing_mgr.view_invoice()
            elif choice == "4":
                self.billing_mgr.mark_paid()
            elif choice == "0":
                return
            else:
                print("✘ Invalid choice.")
            press_enter()

    def dashboard(self):
        print_header("HOSPITAL DASHBOARD")
        total_patients = len(self.patient_mgr.patients)
        admitted = sum(1 for p in self.patient_mgr.patients if p["admitted"])
        total_doctors = len(self.doctor_mgr.doctors)
        upcoming_appts = sum(
            1 for a in self.appointment_mgr.appointments if a["status"] == "Scheduled"
        )
        unpaid_bills = sum(1 for b in self.billing_mgr.bills if not b["paid"])
        total_beds = sum(w["total_beds"] for w in self.ward_mgr.wards)
        occupied_beds = sum(len(w["occupied_beds"]) for w in self.ward_mgr.wards)

        print(f"  Total Registered Patients : {total_patients}")
        print(f"  Currently Admitted        : {admitted}")
        print(f"  Total Doctors             : {total_doctors}")
        print(f"  Scheduled Appointments    : {upcoming_appts}")
        print(f"  Unpaid Bills              : {unpaid_bills}")
        print(f"  Bed Occupancy             : {occupied_beds}/{total_beds}")
        print("=" * 60)

    def main_menu(self):
        while True:
            self.dashboard()
            print("\nMAIN MENU")
            print("1. Patient Management")
            print("2. Doctor Management")
            print("3. Appointment Management")
            print("4. Admission / Ward Management")
            print("5. Billing")
            print("0. Exit")
            choice = input("\nEnter your choice: ").strip()

            if choice == "1":
                self.patient_menu()
            elif choice == "2":
                self.doctor_menu()
            elif choice == "3":
                self.appointment_menu()
            elif choice == "4":
                self.admission_menu()
            elif choice == "5":
                self.billing_menu()
            elif choice == "0":
                print("\nThank you for using the Hospital Management System. Goodbye!\n")
                break
            else:
                print("✘ Invalid choice. Please try again.")
                press_enter()

def main():
    print_header("WELCOME TO THE HOSPITAL MANAGEMENT SYSTEM")
    print("All data is automatically saved to the 'hms_data' folder as JSON files.")
    press_enter()
    app = HospitalManagementSystem()
    app.main_menu()

if __name__ == "__main__":
    main()
    