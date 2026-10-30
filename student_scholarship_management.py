"""
Student Scholarship Management System
======================================
Technology : Python 3, Tkinter GUI, File Handling
Storage    : students.txt (JSON Lines record format)
Author     : College Engineering Demonstration Project

Overview:
---------
This desktop application provides a comprehensive, automated platform for student
scholarship registration, eligibility verification, and record management.

Key Features:
  1. Main Home Portal: Intuitive navigation for students and administrators.
  2. Student Registration: Input validation (Name, Age, Marks, Income), unique ID
     generation (e.g., SCH-1001), initial 'Pending' status assignment.
  3. Admin Authentication: Credential verification with password masking.
  4. Eligibility Assessment:
       - Age >= 18
       - Academic Marks >= 60.0%
       - Annual Family Income <= Rs 2,50,000
     Automatically updates status to 'Approved' or 'Rejected' with itemized reasons.
  5. Records Management: Interactive ttk.Treeview table with color-coded status,
     filtering, search, refresh, and confirmed record deletion.
  6. Robust File I/O: Safe JSON Lines format in 'students.txt' with automatic file
     initialization and corruption handling.
"""

import json
import os
import sys
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox


# ==============================================================================
# CONFIGURATION CONSTANTS & COLOR PALETTE
# ==============================================================================

# File storage path (co-located in script directory)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "students.txt")

# Default Demonstration Credentials
# Note: In production systems, credentials must NEVER be hardcoded. They should be
# securely hashed (e.g., using bcrypt/argon2) and loaded from encrypted environment
# variables or a dedicated authentication service.
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Scholarship Eligibility Criteria Thresholds
CRITERIA_MIN_AGE = 18
CRITERIA_MIN_MARKS = 60.0
CRITERIA_MAX_INCOME = 250000.0

# Professional Color Scheme
COLOR_PRIMARY_GREEN = "#2E7D32"   # Green for Registration / Submit
COLOR_HOVER_GREEN   = "#1B5E20"
COLOR_PRIMARY_BLUE  = "#1565C0"   # Blue for Admin Login / Check Eligibility
COLOR_HOVER_BLUE    = "#0D47A1"
COLOR_PRIMARY_RED   = "#C62828"   # Red for Delete Record
COLOR_HOVER_RED     = "#B71C1C"
COLOR_DARK          = "#212121"   # Black / Dark Gray for Exit / Cancel
COLOR_DARK_HOVER    = "#424242"
COLOR_BG            = "#F4F6F9"   # Soft Light Gray / White application background
COLOR_CARD_BG       = "#FFFFFF"   # Pure White for card panels
COLOR_BORDER        = "#CFD8DC"   # Light border line
COLOR_TEXT_MAIN     = "#263238"   # Primary text color
COLOR_TEXT_MUTED    = "#607D8B"   # Secondary descriptive text color

# Status Colors
STATUS_COLOR_APPROVED = "#2E7D32"  # Green
STATUS_COLOR_REJECTED = "#C62828"  # Red
STATUS_COLOR_PENDING  = "#EF6C00"  # Amber / Orange
COLOR_APPROVED = STATUS_COLOR_APPROVED
COLOR_REJECTED = STATUS_COLOR_REJECTED
COLOR_PENDING  = STATUS_COLOR_PENDING


# ==============================================================================
# DATA MANAGER CLASS (FILE HANDLING & BUSINESS LOGIC)
# ==============================================================================

class DataManager:
    """
    Handles all persistent CRUD operations on 'students.txt'.
    Employs JSON Lines format (each line is a valid JSON document), providing
    robustness against delimiter injection while maintaining plain-text transparency.
    """

    @staticmethod
    def ensure_file_exists():
        """Ensure students.txt exists without overwriting existing data."""
        try:
            if not os.path.exists(DATA_FILE):
                with open(DATA_FILE, "w", encoding="utf-8") as f:
                    pass  # Create empty file
        except OSError as e:
            messagebox.showerror("File Error", f"Unable to create storage file: {e}")

    @staticmethod
    def load_all_students():
        """
        Reads and parses all student records from students.txt.
        Returns a list of student dictionaries.
        """
        DataManager.ensure_file_exists()
        students = []
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, start=1):
                    line_str = line.strip()
                    if not line_str:
                        continue
                    try:
                        record = json.loads(line_str)
                        # Ensure baseline keys exist
                        record.setdefault("id", "UNKNOWN")
                        record.setdefault("name", "N/A")
                        record.setdefault("age", 0)
                        record.setdefault("marks", 0.0)
                        record.setdefault("income", 0.0)
                        record.setdefault("status", "Pending")
                        record.setdefault("reason", "Awaiting verification")
                        record.setdefault("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        students.append(record)
                    except json.JSONDecodeError:
                        # Skip corrupt lines without crashing the entire app
                        continue
        except OSError as e:
            messagebox.showerror("I/O Error", f"Failed to read '{DATA_FILE}': {e}")
        return students

    @staticmethod
    def save_all_students(students):
        """
        Rewrites all student records safely into students.txt.
        Returns True on success, False on error.
        """
        try:
            # Write to a temporary file first then replace (atomic approach)
            temp_file = DATA_FILE + ".tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                for student in students:
                    f.write(json.dumps(student, ensure_ascii=False) + "\n")
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            os.rename(temp_file, DATA_FILE)
            return True
        except OSError as e:
            messagebox.showerror("I/O Error", f"Failed to write to '{DATA_FILE}': {e}")
            return False

    @classmethod
    def generate_unique_id(cls):
        """
        Generates the next unique student ID in sequential order (SCH-1001, SCH-1002, etc.).
        Avoids collisions even if names are identical.
        """
        students = cls.load_all_students()
        max_num = 1000
        for s in students:
            sid = str(s.get("id", ""))
            if sid.startswith("SCH-"):
                num_part = sid[4:]
                if num_part.isdigit():
                    val = int(num_part)
                    if val > max_num:
                        max_num = val
        return f"SCH-{max_num + 1}"

    @classmethod
    def add_student(cls, name, age, marks, income):
        """
        Registers a new student and appends the record to students.txt.
        Returns (success_flag, message_or_id, record_dict).
        """
        cls.ensure_file_exists()
        student_id = cls.generate_unique_id()
        record = {
            "id": student_id,
            "name": name.strip(),
            "age": int(age),
            "marks": round(float(marks), 2),
            "income": round(float(income), 2),
            "status": "Pending",
            "reason": "Application registered; pending administrator review.",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        try:
            with open(DATA_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            return True, student_id, record
        except OSError as e:
            return False, f"File write error: {e}", None

    @classmethod
    def get_student_by_id(cls, student_id):
        """Finds and returns a student record by ID (case-insensitive)."""
        target_id = student_id.strip().upper()
        for s in cls.load_all_students():
            if str(s.get("id", "")).strip().upper() == target_id:
                return s
        return None

    @classmethod
    def evaluate_scholarship_eligibility(cls, student_id):
        """
        Evaluates eligibility against defined criteria:
          1. Age >= 18
          2. Marks >= 60.0%
          3. Annual Income <= Rs 2,50,000
        Updates record in students.txt permanently.
        Returns (is_approved, explanation_message, updated_record).
        """
        students = cls.load_all_students()
        target_id = student_id.strip().upper()
        found_index = -1
        target_student = None

        for idx, s in enumerate(students):
            if str(s.get("id", "")).strip().upper() == target_id:
                found_index = idx
                target_student = s
                break

        if found_index == -1 or target_student is None:
            return None, "Student ID not found in database.", None

        age = target_student.get("age", 0)
        marks = target_student.get("marks", 0.0)
        income = target_student.get("income", 0.0)

        # Evaluate criteria
        failed_reasons = []
        if age < CRITERIA_MIN_AGE:
            failed_reasons.append(
                f"Age ({age} yrs) is below minimum requirement of {CRITERIA_MIN_AGE} yrs."
            )
        if marks < CRITERIA_MIN_MARKS:
            failed_reasons.append(
                f"Marks ({marks:.2f}%) is below minimum requirement of {CRITERIA_MIN_MARKS:.1f}%."
            )
        if income > CRITERIA_MAX_INCOME:
            failed_reasons.append(
                f"Annual Family Income (Rs. {income:,.2f}) exceeds maximum threshold of Rs. {CRITERIA_MAX_INCOME:,.2f}."
            )

        if not failed_reasons:
            is_approved = True
            new_status = "Approved"
            remarks = (
                f"Eligible: Meets all criteria (Age >= {CRITERIA_MIN_AGE}, "
                f"Marks >= {CRITERIA_MIN_MARKS:.0f}%, Family Income <= Rs. {CRITERIA_MAX_INCOME:,.0f})."
            )
        else:
            is_approved = False
            new_status = "Rejected"
            remarks = "Ineligible: " + " | ".join(failed_reasons)

        target_student["status"] = new_status
        target_student["reason"] = remarks
        target_student["evaluated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        students[found_index] = target_student
        cls.save_all_students(students)

        return is_approved, remarks, target_student

    @classmethod
    def delete_student(cls, student_id):
        """
        Deletes a student record permanently by ID.
        Returns (success_flag, message).
        """
        students = cls.load_all_students()
        target_id = student_id.strip().upper()
        initial_len = len(students)
        filtered_students = [s for s in students if str(s.get("id", "")).strip().upper() != target_id]

        if len(filtered_students) == initial_len:
            return False, f"Student ID '{student_id}' does not exist in the records."

        if cls.save_all_students(filtered_students):
            return True, f"Student record for ID '{target_id}' has been permanently deleted."
        else:
            return False, "Failed to update storage file during deletion."

    @classmethod
    def get_statistics(cls):
        """Returns statistical counts of applications."""
        students = cls.load_all_students()
        total = len(students)
        approved = sum(1 for s in students if s.get("status") == "Approved")
        rejected = sum(1 for s in students if s.get("status") == "Rejected")
        pending = sum(1 for s in students if s.get("status") == "Pending")
        return {
            "total": total,
            "approved": approved,
            "rejected": rejected,
            "pending": pending
        }


# ==============================================================================
# UI HELPER FUNCTIONS
# ==============================================================================

def center_window(window, width, height):
    """Centers any Tkinter window on the primary display."""
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = max(0, (screen_width - width) // 2)
    y = max(0, (screen_height - height) // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


def create_styled_button(parent, text, command, bg_color, hover_color, fg_color="white", width=None, height=None, font=("Helvetica", 10, "bold")):
    """Creates a custom styled Button with hover animations and flat modern aesthetic."""
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg_color,
        fg=fg_color,
        activebackground=hover_color,
        activeforeground=fg_color,
        relief=tk.FLAT,
        cursor="hand2",
        font=font,
        padx=14,
        pady=7
    )
    if width:
        btn.config(width=width)
    if height:
        btn.config(height=height)

    def on_enter(e):
        btn["background"] = hover_color

    def on_leave(e):
        btn["background"] = bg_color

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn


# ==============================================================================
# WINDOW 1: STUDENT REGISTRATION WINDOW
# ==============================================================================

class RegistrationWindow(tk.Toplevel):
    """
    Separate registration window enabling students to self-register without
    requiring administrator credentials.
    """

    def __init__(self, master=None):
        super().__init__(master)
        self.title("Student Scholarship Registration Portal")
        self.config(bg=COLOR_BG)
        self.resizable(False, False)
        center_window(self, 620, 680)

        # Make window modal
        self.transient(master)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        # Header Banner
        header = tk.Frame(self, bg=COLOR_PRIMARY_GREEN, height=80)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        title_lbl = tk.Label(
            header,
            text="🎓 New Student Registration",
            font=("Helvetica", 16, "bold"),
            bg=COLOR_PRIMARY_GREEN,
            fg="white"
        )
        title_lbl.pack(pady=(15, 2))

        sub_lbl = tk.Label(
            header,
            text="Complete all fields accurately to apply for the Merit-Cum-Means Scholarship",
            font=("Helvetica", 9),
            bg=COLOR_PRIMARY_GREEN,
            fg="#E8F5E9"
        )
        sub_lbl.pack()

        # Main Form Container (Card Style)
        card = tk.Frame(self, bg=COLOR_CARD_BG, bd=1, relief=tk.SOLID, padx=30, pady=25)
        card.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)

        # Form Fields
        lbl_font = ("Helvetica", 10, "bold")
        entry_font = ("Helvetica", 11)

        # Field: Student Name
        tk.Label(card, text="Student Full Name *", font=lbl_font, bg=COLOR_CARD_BG, fg=COLOR_TEXT_MAIN).pack(anchor="w", pady=(0, 4))
        self.name_entry = ttk.Entry(card, font=entry_font)
        self.name_entry.pack(fill=tk.X, pady=(0, 14))
        self.name_entry.focus_set()

        # Field: Age
        tk.Label(card, text="Age (in years) *", font=lbl_font, bg=COLOR_CARD_BG, fg=COLOR_TEXT_MAIN).pack(anchor="w", pady=(0, 4))
        self.age_entry = ttk.Entry(card, font=entry_font)
        self.age_entry.pack(fill=tk.X, pady=(0, 14))

        # Field: Academic Marks (%)
        tk.Label(card, text="Marks Percentage (0.0 to 100.0 %) *", font=lbl_font, bg=COLOR_CARD_BG, fg=COLOR_TEXT_MAIN).pack(anchor="w", pady=(0, 4))
        self.marks_entry = ttk.Entry(card, font=entry_font)
        self.marks_entry.pack(fill=tk.X, pady=(0, 14))

        # Field: Annual Family Income (INR)
        tk.Label(card, text="Annual Family Income (₹ INR) *", font=lbl_font, bg=COLOR_CARD_BG, fg=COLOR_TEXT_MAIN).pack(anchor="w", pady=(0, 4))
        self.income_entry = ttk.Entry(card, font=entry_font)
        self.income_entry.pack(fill=tk.X, pady=(0, 15))

        # Helper Criteria Box
        info_box = tk.Frame(card, bg="#E8F5E9", bd=1, relief=tk.SOLID, padx=12, pady=8)
        info_box.pack(fill=tk.X, pady=(0, 20))

        info_text = (
            "📌 Eligibility Criteria Reminder:\n"
            " • Minimum Age: 18 years old\n"
            " • Academic Score: At least 60.0% marks\n"
            " • Annual Family Income: Maximum ₹2,50,000"
        )
        tk.Label(
            info_box,
            text=info_text,
            font=("Helvetica", 9),
            bg="#E8F5E9",
            fg="#1B5E20",
            justify=tk.LEFT
        ).pack(anchor="w")

        # Action Buttons
        btn_frame = tk.Frame(card, bg=COLOR_CARD_BG)
        btn_frame.pack(fill=tk.X, pady=(5, 0))

        # Submit Button (Green)
        self.submit_btn = create_styled_button(
            btn_frame,
            text="✓ Submit Registration",
            command=self._on_submit,
            bg_color=COLOR_PRIMARY_GREEN,
            hover_color=COLOR_HOVER_GREEN,
            fg_color="white",
            font=("Helvetica", 10, "bold")
        )
        self.submit_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        # Clear Form Button
        self.clear_btn = create_styled_button(
            btn_frame,
            text="⟳ Clear Form",
            command=self._clear_form,
            bg_color="#78909C",
            hover_color="#546E7A",
            fg_color="white",
            font=("Helvetica", 10, "bold")
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        # Back to Home Button
        self.back_btn = create_styled_button(
            btn_frame,
            text="Back to Home",
            command=self.destroy,
            bg_color=COLOR_DARK,
            hover_color=COLOR_DARK_HOVER,
            fg_color="white",
            font=("Helvetica", 10, "bold")
        )
        self.back_btn.pack(side=tk.LEFT, padx=(5, 0))

    def _clear_form(self):
        """Clears all input entries."""
        self.name_entry.delete(0, tk.END)
        self.age_entry.delete(0, tk.END)
        self.marks_entry.delete(0, tk.END)
        self.income_entry.delete(0, tk.END)
        self.name_entry.focus_set()

    def _on_submit(self):
        """Validates input fields and saves new record."""
        raw_name = self.name_entry.get().strip()
        raw_age = self.age_entry.get().strip()
        raw_marks = self.marks_entry.get().strip()
        raw_income = self.income_entry.get().strip()

        # 1. Validation: Non-empty check
        if not raw_name or not raw_age or not raw_marks or not raw_income:
            messagebox.showwarning(
                "Incomplete Form",
                "All fields are mandatory. Please fill in every field before submitting."
            )
            return

        # 2. Validation: Name characters
        if len(raw_name) < 2:
            messagebox.showerror(
                "Invalid Name",
                "Student name must be at least 2 characters long."
            )
            self.name_entry.focus_set()
            return

        # 3. Validation: Age
        try:
            age = int(raw_age)
            if age <= 0:
                raise ValueError("Age must be positive")
            if age > 120:
                raise ValueError("Age must be realistic")
        except ValueError:
            messagebox.showerror(
                "Invalid Age",
                "Please enter a valid positive whole number for Age (e.g., 18, 20)."
            )
            self.age_entry.focus_set()
            return

        # 4. Validation: Marks
        try:
            marks = float(raw_marks)
            if marks < 0.0 or marks > 100.0:
                raise ValueError("Marks out of range")
        except ValueError:
            messagebox.showerror(
                "Invalid Marks",
                "Marks percentage must be a valid number between 0.0 and 100.0%."
            )
            self.marks_entry.focus_set()
            return

        # 5. Validation: Income
        try:
            income = float(raw_income)
            if income < 0.0:
                raise ValueError("Income must be non-negative")
        except ValueError:
            messagebox.showerror(
                "Invalid Income",
                "Annual family income must be a valid number greater than or equal to ₹0."
            )
            self.income_entry.focus_set()
            return

        # Persist record
        success, res, record = DataManager.add_student(
            name=raw_name,
            age=age,
            marks=marks,
            income=income
        )

        if success:
            success_msg = (
                f"🎉 Registration Successful!\n\n"
                f"Student ID : {res}\n"
                f"Name       : {raw_name}\n"
                f"Status     : Pending Review\n\n"
                f"Your application has been stored securely in '{os.path.basename(DATA_FILE)}'.\n"
                f"Please keep your Student ID safe for checking results."
            )
            messagebox.showinfo("Registration Confirmed", success_msg)
            self._clear_form()
            # If parent has refresh capability, notify it
            if hasattr(self.master, "update_stats_display"):
                self.master.update_stats_display()
        else:
            messagebox.showerror("Registration Error", f"Failed to save student record:\n{res}")


# ==============================================================================
# WINDOW 2: ADMIN LOGIN WINDOW
# ==============================================================================

class AdminLoginWindow(tk.Toplevel):
    """
    Separate authentication window for administrator access.
    Validates username and password with hidden character masking.
    """

    def __init__(self, master=None, on_success_callback=None):
        super().__init__(master)
        self.title("Administrator Login")
        self.config(bg=COLOR_BG)
        self.resizable(False, False)
        center_window(self, 480, 480)

        self.on_success_callback = on_success_callback

        self.transient(master)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        # Header Banner (Blue)
        header = tk.Frame(self, bg=COLOR_PRIMARY_BLUE, height=75)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        title_lbl = tk.Label(
            header,
            text="🔒 Administrator Authentication",
            font=("Helvetica", 14, "bold"),
            bg=COLOR_PRIMARY_BLUE,
            fg="white"
        )
        title_lbl.pack(pady=(16, 2))

        sub_lbl = tk.Label(
            header,
            text="Restricted Access — Authorized Personnel Only",
            font=("Helvetica", 8),
            bg=COLOR_PRIMARY_BLUE,
            fg="#BBDEFB"
        )
        sub_lbl.pack()

        # Form Card
        card = tk.Frame(self, bg=COLOR_CARD_BG, bd=1, relief=tk.SOLID, padx=30, pady=25)
        card.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)

        lbl_font = ("Helvetica", 10, "bold")
        entry_font = ("Helvetica", 11)

        # Username
        tk.Label(card, text="Admin Username *", font=lbl_font, bg=COLOR_CARD_BG, fg=COLOR_TEXT_MAIN).pack(anchor="w", pady=(0, 4))
        self.user_entry = ttk.Entry(card, font=entry_font)
        self.user_entry.pack(fill=tk.X, pady=(0, 14))
        self.user_entry.focus_set()

        # Password
        tk.Label(card, text="Password *", font=lbl_font, bg=COLOR_CARD_BG, fg=COLOR_TEXT_MAIN).pack(anchor="w", pady=(0, 4))
        self.pass_entry = ttk.Entry(card, font=entry_font, show="*")
        self.pass_entry.pack(fill=tk.X, pady=(0, 6))

        # Show password toggle
        self.show_pass_var = tk.BooleanVar(value=False)
        show_cb = tk.Checkbutton(
            card,
            text="Show Password",
            variable=self.show_pass_var,
            command=self._toggle_password_visibility,
            bg=COLOR_CARD_BG,
            activebackground=COLOR_CARD_BG,
            font=("Helvetica", 9),
            fg=COLOR_TEXT_MUTED
        )
        show_cb.pack(anchor="w", pady=(0, 15))

        # Bind Enter key to login
        self.user_entry.bind("<Return>", lambda e: self.pass_entry.focus_set())
        self.pass_entry.bind("<Return>", lambda e: self._on_login())

        # Academic Demo Note
        demo_note = tk.Frame(card, bg="#EDE7F6", bd=1, relief=tk.SOLID, padx=10, pady=6)
        demo_note.pack(fill=tk.X, pady=(0, 18))
        demo_text = (
            "🔑 Demo Credentials:\n"
            f"   Username: {ADMIN_USERNAME}\n"
            f"   Password: {ADMIN_PASSWORD}\n"
            "   (Configured for academic evaluation)"
        )
        tk.Label(
            demo_note,
            text=demo_text,
            font=("Helvetica", 8),
            bg="#EDE7F6",
            fg="#4527A0",
            justify=tk.LEFT
        ).pack(anchor="w")

        # Buttons
        btn_frame = tk.Frame(card, bg=COLOR_CARD_BG)
        btn_frame.pack(fill=tk.X)

        self.login_btn = create_styled_button(
            btn_frame,
            text="🔑 Login",
            command=self._on_login,
            bg_color=COLOR_PRIMARY_BLUE,
            hover_color=COLOR_HOVER_BLUE,
            fg_color="white",
            font=("Helvetica", 10, "bold")
        )
        self.login_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        self.cancel_btn = create_styled_button(
            btn_frame,
            text="Cancel / Back",
            command=self.destroy,
            bg_color=COLOR_DARK,
            hover_color=COLOR_DARK_HOVER,
            fg_color="white",
            font=("Helvetica", 10, "bold")
        )
        self.cancel_btn.pack(side=tk.LEFT, padx=(6, 0))

    def _toggle_password_visibility(self):
        """Toggles masking of password entry."""
        if self.show_pass_var.get():
            self.pass_entry.config(show="")
        else:
            self.pass_entry.config(show="*")

    def _on_login(self):
        """Validates credentials against configured credentials."""
        entered_user = self.user_entry.get().strip()
        entered_pass = self.pass_entry.get()

        if not entered_user or not entered_pass:
            messagebox.showwarning("Incomplete Input", "Please enter both username and password.")
            return

        if entered_user == ADMIN_USERNAME and entered_pass == ADMIN_PASSWORD:
            self.destroy()
            if self.on_success_callback:
                self.on_success_callback()
        else:
            messagebox.showerror(
                "Authentication Failed",
                "Invalid admin username or password.\n\nPlease check your credentials and retry."
            )
            self.pass_entry.delete(0, tk.END)
            self.pass_entry.focus_set()


# ==============================================================================
# WINDOW 3: DEDICATED VIEW ALL STUDENTS WINDOW (TREEVIEW TABLE)
# ==============================================================================

class ViewStudentsWindow(tk.Toplevel):
    """
    Dedicated window displaying all registered students using ttk.Treeview
    with status tagging, search filter, and instant refresh.
    """

    def __init__(self, master=None):
        super().__init__(master)
        self.title("All Registered Students — Scholarship Management System")
        self.config(bg=COLOR_BG)
        center_window(self, 960, 580)

        self._build_ui()
        self.refresh_records()

    def _build_ui(self):
        # Header Banner
        header = tk.Frame(self, bg=COLOR_DARK, height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="📋 Registered Scholarship Applicants",
            font=("Helvetica", 14, "bold"),
            bg=COLOR_DARK,
            fg="white"
        ).pack(side=tk.LEFT, padx=20, pady=15)

        # Filter and Control Bar
        filter_bar = tk.Frame(self, bg=COLOR_CARD_BG, bd=1, relief=tk.SOLID, padx=12, pady=10)
        filter_bar.pack(fill=tk.X, padx=15, pady=10)

        tk.Label(filter_bar, text="Filter by Status:", font=("Helvetica", 9, "bold"), bg=COLOR_CARD_BG).pack(side=tk.LEFT, padx=(5, 5))
        self.status_filter_var = tk.StringVar(value="All")
        status_cb = ttk.Combobox(
            filter_bar,
            textvariable=self.status_filter_var,
            values=["All", "Pending", "Approved", "Rejected"],
            state="readonly",
            width=12
        )
        status_cb.pack(side=tk.LEFT, padx=(0, 15))
        status_cb.bind("<<ComboboxSelected>>", lambda e: self.apply_filter())

        tk.Label(filter_bar, text="Search (Name or ID):", font=("Helvetica", 9, "bold"), bg=COLOR_CARD_BG).pack(side=tk.LEFT, padx=(5, 5))
        self.search_entry = ttk.Entry(filter_bar, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self.apply_filter())

        # Refresh button
        create_styled_button(
            filter_bar,
            text="⟳ Refresh",
            command=self.refresh_records,
            bg_color=COLOR_PRIMARY_BLUE,
            hover_color=COLOR_HOVER_BLUE,
            font=("Helvetica", 9, "bold")
        ).pack(side=tk.LEFT, padx=5)

        # Close button
        create_styled_button(
            filter_bar,
            text="✕ Close",
            command=self.destroy,
            bg_color=COLOR_DARK,
            hover_color=COLOR_DARK_HOVER,
            font=("Helvetica", 9, "bold")
        ).pack(side=tk.RIGHT, padx=5)

        # Treeview Table Container
        table_frame = tk.Frame(self, bg=COLOR_CARD_BG, bd=1, relief=tk.SOLID)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        columns = ("id", "name", "age", "marks", "income", "status", "reason")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        # Headings and widths
        self.tree.heading("id", text="Student ID")
        self.tree.heading("name", text="Full Name")
        self.tree.heading("age", text="Age")
        self.tree.heading("marks", text="Marks (%)")
        self.tree.heading("income", text="Annual Income (₹)")
        self.tree.heading("status", text="Status")
        self.tree.heading("reason", text="Evaluation Remarks / Reason")

        self.tree.column("id", width=95, anchor="center")
        self.tree.column("name", width=150, anchor="w")
        self.tree.column("age", width=60, anchor="center")
        self.tree.column("marks", width=85, anchor="center")
        self.tree.column("income", width=130, anchor="e")
        self.tree.column("status", width=95, anchor="center")
        self.tree.column("reason", width=310, anchor="w")

        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Row tag colors
        self.tree.tag_configure("approved", background="#E8F5E9", foreground="#1B5E20")
        self.tree.tag_configure("rejected", background="#FFEBEE", foreground="#B71C1C")
        self.tree.tag_configure("pending", background="#FFF3E0", foreground="#E65100")

    def refresh_records(self):
        """Reloads records from file and populates treeview."""
        self.all_records = DataManager.load_all_students()
        self.apply_filter()

    def apply_filter(self):
        """Filters displayed records based on search text and status dropdown."""
        # Clear existing rows
        for item in self.tree.get_children():
            self.tree.delete(item)

        filter_status = self.status_filter_var.get()
        search_query = self.search_entry.get().strip().lower()

        for student in self.all_records:
            status = student.get("status", "Pending")
            name = str(student.get("name", "")).lower()
            sid = str(student.get("id", "")).lower()

            # Status match
            if filter_status != "All" and status.lower() != filter_status.lower():
                continue

            # Text query match
            if search_query and (search_query not in name and search_query not in sid):
                continue

            tag = status.lower()
            if tag not in ["approved", "rejected", "pending"]:
                tag = "pending"

            income_fmt = f"₹{student.get('income', 0.0):,.2f}"
            marks_fmt = f"{student.get('marks', 0.0):.2f}%"

            self.tree.insert(
                "",
                tk.END,
                values=(
                    student.get("id", ""),
                    student.get("name", ""),
                    student.get("age", ""),
                    marks_fmt,
                    income_fmt,
                    status,
                    student.get("reason", "")
                ),
                tags=(tag,)
            )


# ==============================================================================
# WINDOW 4: ADMIN PANEL / DASHBOARD
# ==============================================================================

class AdminPanelWindow(tk.Toplevel):
    """
    Main Administrator Dashboard featuring:
      - KPI summary metrics (Total, Approved, Rejected, Pending)
      - Check Scholarship Eligibility with criteria breakdown
      - Integrated View All Students Treeview
      - Delete Student with confirmation
      - Exit Admin Panel (safe return to main screen)
    """

    def __init__(self, master=None):
        super().__init__(master)
        self.title("Administrator Dashboard — Student Scholarship Management")
        self.config(bg=COLOR_BG)
        center_window(self, 1020, 720)

        # Protocol for clean window exit
        self.protocol("WM_DELETE_WINDOW", self._on_exit)

        self._build_ui()
        self.refresh_all_data()

    def _build_ui(self):
        # 1. Header Banner
        header = tk.Frame(self, bg=COLOR_PRIMARY_BLUE, height=70)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        title_frame = tk.Frame(header, bg=COLOR_PRIMARY_BLUE)
        title_frame.pack(side=tk.LEFT, padx=20, pady=10)

        tk.Label(
            title_frame,
            text="🛡️ Administrator Management Dashboard",
            font=("Helvetica", 14, "bold"),
            bg=COLOR_PRIMARY_BLUE,
            fg="white"
        ).pack(anchor="w")

        tk.Label(
            title_frame,
            text="Authenticated Session: Full Administrative Privileges",
            font=("Helvetica", 8),
            bg=COLOR_PRIMARY_BLUE,
            fg="#BBDEFB"
        ).pack(anchor="w")

        # Exit Admin Panel button in header
        create_styled_button(
            header,
            text="⏏ Exit Admin Panel",
            command=self._on_exit,
            bg_color=COLOR_DARK,
            hover_color=COLOR_DARK_HOVER,
            fg_color="white",
            font=("Helvetica", 9, "bold")
        ).pack(side=tk.RIGHT, padx=20, pady=16)

        # 2. KPI / Metrics Row
        kpi_frame = tk.Frame(self, bg=COLOR_BG)
        kpi_frame.pack(fill=tk.X, padx=20, pady=(15, 10))

        self.kpi_total_lbl = self._create_kpi_card(kpi_frame, "Total Applications", "0", "#37474F", 0)
        self.kpi_approved_lbl = self._create_kpi_card(kpi_frame, "Approved", "0", COLOR_PRIMARY_GREEN, 1)
        self.kpi_rejected_lbl = self._create_kpi_card(kpi_frame, "Rejected", "0", COLOR_PRIMARY_RED, 2)
        self.kpi_pending_lbl = self._create_kpi_card(kpi_frame, "Pending Review", "0", COLOR_PENDING, 3)

        # 3. Notebook / Tabbed Operations
        notebook_frame = tk.Frame(self, bg=COLOR_BG)
        notebook_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(5, 15))

        style = ttk.Style()
        style.configure("TNotebook.Tab", font=("Helvetica", 10, "bold"), padding=[12, 6])

        self.notebook = ttk.Notebook(notebook_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Check Eligibility
        self.tab_eligibility = tk.Frame(self.notebook, bg=COLOR_BG, padx=15, pady=15)
        self.notebook.add(self.tab_eligibility, text="  ✓ Check Scholarship Eligibility  ")
        self._build_eligibility_tab()

        # Tab 2: View All Students
        self.tab_view_all = tk.Frame(self.notebook, bg=COLOR_BG, padx=15, pady=15)
        self.notebook.add(self.tab_view_all, text="  📋 View All Students (Table)  ")
        self._build_view_tab()

        # Tab 3: Delete Student Record
        self.tab_delete = tk.Frame(self.notebook, bg=COLOR_BG, padx=15, pady=15)
        self.notebook.add(self.tab_delete, text="  🗑 Delete Student Record  ")
        self._build_delete_tab()

    def _create_kpi_card(self, parent, title, initial_val, accent_color, col_idx):
        """Creates a modern statistics metric card."""
        card = tk.Frame(parent, bg=COLOR_CARD_BG, bd=1, relief=tk.SOLID, padx=15, pady=10)
        card.grid(row=0, column=col_idx, padx=6, sticky="nsew")
        parent.grid_columnconfigure(col_idx, weight=1)

        # Accent top bar
        accent = tk.Frame(card, bg=accent_color, height=3)
        accent.pack(fill=tk.X, side=tk.TOP, pady=(0, 6))

        tk.Label(card, text=title, font=("Helvetica", 9), bg=COLOR_CARD_BG, fg=COLOR_TEXT_MUTED).pack(anchor="w")
        val_lbl = tk.Label(card, text=initial_val, font=("Helvetica", 18, "bold"), bg=COLOR_CARD_BG, fg=accent_color)
        val_lbl.pack(anchor="w", pady=(2, 0))
        return val_lbl

    # --------------------------------------------------------------------------
    # TAB 1: CHECK SCHOLARSHIP ELIGIBILITY
    # --------------------------------------------------------------------------

    def _build_eligibility_tab(self):
        container = self.tab_eligibility

        # Search Bar
        search_frame = tk.Frame(container, bg=COLOR_CARD_BG, bd=1, relief=tk.SOLID, padx=15, pady=12)
        search_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            search_frame,
            text="Enter Student ID:",
            font=("Helvetica", 10, "bold"),
            bg=COLOR_CARD_BG,
            fg=COLOR_TEXT_MAIN
        ).pack(side=tk.LEFT, padx=(0, 8))

        self.eligibility_id_entry = ttk.Entry(search_frame, font=("Helvetica", 11), width=18)
        self.eligibility_id_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.eligibility_id_entry.bind("<Return>", lambda e: self._on_search_student_for_eligibility())

        # Search Button (Blue)
        create_styled_button(
            search_frame,
            text="🔍 Find Student",
            command=self._on_search_student_for_eligibility,
            bg_color=COLOR_PRIMARY_BLUE,
            hover_color=COLOR_HOVER_BLUE,
            font=("Helvetica", 9, "bold")
        ).pack(side=tk.LEFT, padx=4)

        # Content Split Layout: Details Card on Left, Evaluation Result on Right
        content_frame = tk.Frame(container, bg=COLOR_BG)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Left: Student Details Card
        self.left_card = tk.Frame(content_frame, bg=COLOR_CARD_BG, bd=1, relief=tk.SOLID, padx=15, pady=15)
        self.left_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        tk.Label(
            self.left_card,
            text="👤 Student Record Details",
            font=("Helvetica", 11, "bold"),
            bg=COLOR_CARD_BG,
            fg=COLOR_TEXT_MAIN
        ).pack(anchor="w", pady=(0, 10))

        self.detail_name_lbl = self._create_detail_row(self.left_card, "Student Name:")
        self.detail_id_lbl = self._create_detail_row(self.left_card, "Student ID:")
        self.detail_age_lbl = self._create_detail_row(self.left_card, "Age:")
        self.detail_marks_lbl = self._create_detail_row(self.left_card, "Marks Percentage:")
        self.detail_income_lbl = self._create_detail_row(self.left_card, "Annual Family Income:")
        self.detail_status_lbl = self._create_detail_row(self.left_card, "Current Status:")

        # Right: Evaluation Rules & Evaluation Button
        right_card = tk.Frame(content_frame, bg=COLOR_CARD_BG, bd=1, relief=tk.SOLID, padx=15, pady=15)
        right_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))

        tk.Label(
            right_card,
            text="⚖️ Scholarship Eligibility Rules",
            font=("Helvetica", 11, "bold"),
            bg=COLOR_CARD_BG,
            fg=COLOR_TEXT_MAIN
        ).pack(anchor="w", pady=(0, 10))

        rules_box = tk.Frame(right_card, bg="#F1F8E9", bd=1, relief=tk.SOLID, padx=10, pady=10)
        rules_box.pack(fill=tk.X, pady=(0, 15))

        rules_desc = (
            "Rule 1: Age must be >= 18 years\n"
            "Rule 2: Academic Marks must be >= 60.0%\n"
            "Rule 3: Annual Family Income must be <= Rs. 2,50,000\n\n"
            "Outcome:\n"
            " * All pass -> Status changes to 'Approved'\n"
            " * Any fail -> Status changes to 'Rejected' with exact reason"
        )
        tk.Label(rules_box, text=rules_desc, font=("Helvetica", 9), bg="#F1F8E9", fg="#2E7D32", justify=tk.LEFT).pack(anchor="w")

        # Evaluate Button (Blue)
        self.eval_btn = create_styled_button(
            right_card,
            text="⚡ Check & Update Eligibility",
            command=self._on_check_eligibility,
            bg_color=COLOR_PRIMARY_BLUE,
            hover_color=COLOR_HOVER_BLUE,
            font=("Helvetica", 11, "bold")
        )
        self.eval_btn.pack(fill=tk.X, pady=(0, 12))

        # Result Banner
        self.result_frame = tk.Frame(right_card, bg="#ECEFF1", bd=1, relief=tk.SOLID, padx=12, pady=10)
        self.result_frame.pack(fill=tk.BOTH, expand=True)

        self.result_title_lbl = tk.Label(
            self.result_frame,
            text="Evaluation Result: Awaiting action",
            font=("Helvetica", 10, "bold"),
            bg="#ECEFF1",
            fg=COLOR_TEXT_MUTED
        )
        self.result_title_lbl.pack(anchor="w", pady=(0, 4))

        self.result_desc_lbl = tk.Label(
            self.result_frame,
            text="Search a student and click 'Check & Update Eligibility' to assess qualification.",
            font=("Helvetica", 9),
            bg="#ECEFF1",
            fg=COLOR_TEXT_MAIN,
            wraplength=380,
            justify=tk.LEFT
        )
        self.result_desc_lbl.pack(anchor="w")

    def _create_detail_row(self, parent, label_text):
        row = tk.Frame(parent, bg=COLOR_CARD_BG)
        row.pack(fill=tk.X, pady=3)
        tk.Label(row, text=label_text, font=("Helvetica", 9, "bold"), bg=COLOR_CARD_BG, fg=COLOR_TEXT_MUTED, width=22, anchor="w").pack(side=tk.LEFT)
        val_lbl = tk.Label(row, text="—", font=("Helvetica", 9), bg=COLOR_CARD_BG, fg=COLOR_TEXT_MAIN, anchor="w")
        val_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)
        return val_lbl

    def _on_search_student_for_eligibility(self):
        student_id = self.eligibility_id_entry.get().strip()
        if not student_id:
            messagebox.showwarning("Empty Input", "Please enter a Student ID to search.")
            return

        student = DataManager.get_student_by_id(student_id)
        if not student:
            messagebox.showerror("Not Found", f"No student found with ID '{student_id}'.")
            self._clear_detail_display()
            return

        # Populate left card
        self.detail_id_lbl.config(text=student.get("id", ""))
        self.detail_name_lbl.config(text=student.get("name", ""))
        self.detail_age_lbl.config(text=f"{student.get('age', '')} years")
        self.detail_marks_lbl.config(text=f"{student.get('marks', 0.0):.2f}%")
        self.detail_income_lbl.config(text=f"₹{student.get('income', 0.0):,.2f}")

        status = student.get("status", "Pending")
        status_color = STATUS_COLOR_PENDING
        if status == "Approved":
            status_color = STATUS_COLOR_APPROVED
        elif status == "Rejected":
            status_color = STATUS_COLOR_REJECTED

        self.detail_status_lbl.config(text=status, fg=status_color, font=("Helvetica", 9, "bold"))

        # Reset result card to neutral preview
        self.result_frame.config(bg="#ECEFF1")
        self.result_title_lbl.config(text=f"Loaded: {student.get('id')} ({status})", fg=COLOR_TEXT_MAIN, bg="#ECEFF1")
        self.result_desc_lbl.config(text=f"Current remarks: {student.get('reason', 'N/A')}", bg="#ECEFF1")

    def _clear_detail_display(self):
        self.detail_id_lbl.config(text="—")
        self.detail_name_lbl.config(text="—")
        self.detail_age_lbl.config(text="—")
        self.detail_marks_lbl.config(text="—")
        self.detail_income_lbl.config(text="—")
        self.detail_status_lbl.config(text="—", fg=COLOR_TEXT_MAIN, font=("Helvetica", 9))
        self.result_frame.config(bg="#ECEFF1")
        self.result_title_lbl.config(text="Evaluation Result: Awaiting action", fg=COLOR_TEXT_MUTED, bg="#ECEFF1")
        self.result_desc_lbl.config(text="Search a student and click 'Check & Update Eligibility'.", bg="#ECEFF1")

    def _on_check_eligibility(self):
        student_id = self.eligibility_id_entry.get().strip()
        if not student_id:
            messagebox.showwarning("Student Required", "Please search and load a student ID first.")
            return

        is_approved, explanation, updated_student = DataManager.evaluate_scholarship_eligibility(student_id)
        if updated_student is None:
            messagebox.showerror("Error", explanation)
            return

        # Update display
        self._on_search_student_for_eligibility()

        if is_approved:
            self.result_frame.config(bg="#E8F5E9")
            self.result_title_lbl.config(
                text=f"✓ STATUS: APPROVED ({updated_student['id']})",
                fg=COLOR_PRIMARY_GREEN,
                bg="#E8F5E9"
            )
            self.result_desc_lbl.config(text=explanation, bg="#E8F5E9", fg="#1B5E20")
            messagebox.showinfo(
                "Scholarship Approved",
                f"Student {updated_student['id']} ({updated_student['name']}) meets all scholarship criteria!\n\n"
                f"Status updated to: Approved\n"
                f"Permanent record saved to students.txt."
            )
        else:
            self.result_frame.config(bg="#FFEBEE")
            self.result_title_lbl.config(
                text=f"✕ STATUS: REJECTED ({updated_student['id']})",
                fg=COLOR_PRIMARY_RED,
                bg="#FFEBEE"
            )
            self.result_desc_lbl.config(text=explanation, bg="#FFEBEE", fg="#B71C1C")
            messagebox.showwarning(
                "Scholarship Rejected",
                f"Student {updated_student['id']} ({updated_student['name']}) is ineligible.\n\n"
                f"Reason(s):\n{explanation}\n\n"
                f"Status updated to: Rejected\n"
                f"Permanent record saved to students.txt."
            )

        self.refresh_all_data()

    # --------------------------------------------------------------------------
    # TAB 2: VIEW ALL STUDENTS
    # --------------------------------------------------------------------------

    def _build_view_tab(self):
        container = self.tab_view_all

        # Action Bar
        top_bar = tk.Frame(container, bg=COLOR_CARD_BG, bd=1, relief=tk.SOLID, padx=12, pady=10)
        top_bar.pack(fill=tk.X, pady=(0, 12))

        tk.Label(top_bar, text="Filter:", font=("Helvetica", 9, "bold"), bg=COLOR_CARD_BG).pack(side=tk.LEFT, padx=(5, 5))
        self.view_tab_filter = tk.StringVar(value="All")
        filter_cb = ttk.Combobox(
            top_bar,
            textvariable=self.view_tab_filter,
            values=["All", "Pending", "Approved", "Rejected"],
            state="readonly",
            width=12
        )
        filter_cb.pack(side=tk.LEFT, padx=(0, 15))
        filter_cb.bind("<<ComboboxSelected>>", lambda e: self._populate_table())

        tk.Label(top_bar, text="Search (ID / Name):", font=("Helvetica", 9, "bold"), bg=COLOR_CARD_BG).pack(side=tk.LEFT, padx=(5, 5))
        self.view_tab_search = ttk.Entry(top_bar, width=20)
        self.view_tab_search.pack(side=tk.LEFT, padx=(0, 15))
        self.view_tab_search.bind("<KeyRelease>", lambda e: self._populate_table())

        # Refresh button
        create_styled_button(
            top_bar,
            text="⟳ Refresh Table",
            command=self.refresh_all_data,
            bg_color=COLOR_PRIMARY_BLUE,
            hover_color=COLOR_HOVER_BLUE,
            font=("Helvetica", 9, "bold")
        ).pack(side=tk.LEFT, padx=4)

        # Open in Dedicated Separate Window button
        create_styled_button(
            top_bar,
            text="⧉ Open in Separate Window",
            command=self._open_separate_view_window,
            bg_color="#546E7A",
            hover_color="#37474F",
            font=("Helvetica", 9, "bold")
        ).pack(side=tk.RIGHT, padx=4)

        # Table Container
        table_frame = tk.Frame(container, bg=COLOR_CARD_BG, bd=1, relief=tk.SOLID)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "name", "age", "marks", "income", "status", "reason")
        self.panel_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        self.panel_tree.heading("id", text="Student ID")
        self.panel_tree.heading("name", text="Full Name")
        self.panel_tree.heading("age", text="Age")
        self.panel_tree.heading("marks", text="Marks (%)")
        self.panel_tree.heading("income", text="Annual Income (₹)")
        self.panel_tree.heading("status", text="Status")
        self.panel_tree.heading("reason", text="Remarks / Reason")

        self.panel_tree.column("id", width=95, anchor="center")
        self.panel_tree.column("name", width=150, anchor="w")
        self.panel_tree.column("age", width=60, anchor="center")
        self.panel_tree.column("marks", width=85, anchor="center")
        self.panel_tree.column("income", width=130, anchor="e")
        self.panel_tree.column("status", width=95, anchor="center")
        self.panel_tree.column("reason", width=310, anchor="w")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.panel_tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.panel_tree.xview)
        self.panel_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.panel_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Tags
        self.panel_tree.tag_configure("approved", background="#E8F5E9", foreground="#1B5E20")
        self.panel_tree.tag_configure("rejected", background="#FFEBEE", foreground="#B71C1C")
        self.panel_tree.tag_configure("pending", background="#FFF3E0", foreground="#E65100")

        # Double click to evaluate student
        self.panel_tree.bind("<Double-1>", self._on_double_click_row)

    def _open_separate_view_window(self):
        ViewStudentsWindow(self)

    def _on_double_click_row(self, event):
        selected = self.panel_tree.selection()
        if not selected:
            return
        item_vals = self.panel_tree.item(selected[0], "values")
        if item_vals:
            sid = item_vals[0]
            self.eligibility_id_entry.delete(0, tk.END)
            self.eligibility_id_entry.insert(0, sid)
            self.notebook.select(self.tab_eligibility)
            self._on_search_student_for_eligibility()

    def _populate_table(self):
        for item in self.panel_tree.get_children():
            self.panel_tree.delete(item)

        filter_status = self.view_tab_filter.get()
        search_query = self.view_tab_search.get().strip().lower()

        students = DataManager.load_all_students()
        for student in students:
            status = student.get("status", "Pending")
            name = str(student.get("name", "")).lower()
            sid = str(student.get("id", "")).lower()

            if filter_status != "All" and status.lower() != filter_status.lower():
                continue
            if search_query and (search_query not in name and search_query not in sid):
                continue

            tag = status.lower()
            if tag not in ["approved", "rejected", "pending"]:
                tag = "pending"

            income_fmt = f"₹{student.get('income', 0.0):,.2f}"
            marks_fmt = f"{student.get('marks', 0.0):.2f}%"

            self.panel_tree.insert(
                "",
                tk.END,
                values=(
                    student.get("id", ""),
                    student.get("name", ""),
                    student.get("age", ""),
                    marks_fmt,
                    income_fmt,
                    status,
                    student.get("reason", "")
                ),
                tags=(tag,)
            )

    # --------------------------------------------------------------------------
    # TAB 3: DELETE STUDENT RECORD
    # --------------------------------------------------------------------------

    def _build_delete_tab(self):
        container = self.tab_delete

        card = tk.Frame(container, bg=COLOR_CARD_BG, bd=1, relief=tk.SOLID, padx=25, pady=20)
        card.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            card,
            text="⚠️ Delete Student Record",
            font=("Helvetica", 12, "bold"),
            bg=COLOR_CARD_BG,
            fg=COLOR_PRIMARY_RED
        ).pack(anchor="w", pady=(0, 6))

        tk.Label(
            card,
            text="Permanently remove a student application from 'students.txt'. This action cannot be undone.",
            font=("Helvetica", 9),
            bg=COLOR_CARD_BG,
            fg=COLOR_TEXT_MUTED
        ).pack(anchor="w", pady=(0, 15))

        # ID Entry row
        input_row = tk.Frame(card, bg=COLOR_CARD_BG)
        input_row.pack(anchor="w", pady=(0, 15))

        tk.Label(
            input_row,
            text="Target Student ID * :",
            font=("Helvetica", 10, "bold"),
            bg=COLOR_CARD_BG,
            fg=COLOR_TEXT_MAIN
        ).pack(side=tk.LEFT, padx=(0, 8))

        self.delete_id_entry = ttk.Entry(input_row, font=("Helvetica", 11), width=18)
        self.delete_id_entry.pack(side=tk.LEFT, padx=(0, 10))

        create_styled_button(
            input_row,
            text="Inspect Record",
            command=self._on_inspect_delete_target,
            bg_color=COLOR_PRIMARY_BLUE,
            hover_color=COLOR_HOVER_BLUE,
            font=("Helvetica", 9, "bold")
        ).pack(side=tk.LEFT)

        # Inspection Preview Card
        self.delete_preview_frame = tk.Frame(card, bg="#FAFAFA", bd=1, relief=tk.SOLID, padx=15, pady=12)
        self.delete_preview_frame.pack(fill=tk.X, pady=(0, 20))

        self.delete_preview_lbl = tk.Label(
            self.delete_preview_frame,
            text="Enter a Student ID and click 'Inspect Record' to view details before deleting.",
            font=("Helvetica", 9),
            bg="#FAFAFA",
            fg=COLOR_TEXT_MUTED,
            justify=tk.LEFT
        )
        self.delete_preview_lbl.pack(anchor="w")

        # Delete Action Button (Red)
        self.delete_btn = create_styled_button(
            card,
            text="🗑 Permanently Delete Student Record",
            command=self._on_delete_student,
            bg_color=COLOR_PRIMARY_RED,
            hover_color=COLOR_HOVER_RED,
            fg_color="white",
            font=("Helvetica", 11, "bold")
        )
        self.delete_btn.pack(anchor="w")

    def _on_inspect_delete_target(self):
        target_id = self.delete_id_entry.get().strip()
        if not target_id:
            messagebox.showwarning("Input Required", "Please enter a Student ID to inspect.")
            return

        student = DataManager.get_student_by_id(target_id)
        if not student:
            self.delete_preview_lbl.config(
                text=f"❌ No student record found matching ID '{target_id}'.",
                fg=COLOR_PRIMARY_RED
            )
            return

        preview_text = (
            f"Target Record Found:\n"
            f" • ID     : {student.get('id')}\n"
            f" • Name   : {student.get('name')}\n"
            f" • Age    : {student.get('age')} years\n"
            f" • Marks  : {student.get('marks'):.2f}%\n"
            f" • Income : ₹{student.get('income'):,.2f}\n"
            f" • Status : {student.get('status')}"
        )
        self.delete_preview_lbl.config(text=preview_text, fg=COLOR_TEXT_MAIN)

    def _on_delete_student(self):
        target_id = self.delete_id_entry.get().strip()
        if not target_id:
            messagebox.showwarning("Input Required", "Please enter a Student ID to delete.")
            return

        student = DataManager.get_student_by_id(target_id)
        if not student:
            messagebox.showerror("Not Found", f"Student ID '{target_id}' does not exist in 'students.txt'.")
            return

        # Explicit Confirmation Dialog
        confirmed = messagebox.askyesno(
            "Confirm Permanent Deletion",
            f"Are you sure you want to permanently delete the following record?\n\n"
            f"Student ID : {student.get('id')}\n"
            f"Full Name  : {student.get('name')}\n"
            f"Status     : {student.get('status')}\n\n"
            f"This action cannot be undone.",
            icon="warning"
        )

        if not confirmed:
            return

        success, msg = DataManager.delete_student(target_id)
        if success:
            messagebox.showinfo("Record Deleted", msg)
            self.delete_id_entry.delete(0, tk.END)
            self.delete_preview_lbl.config(
                text="Record was successfully deleted. Enter another Student ID to inspect.",
                fg=COLOR_PRIMARY_GREEN
            )
            self.refresh_all_data()
            self._clear_detail_display()
        else:
            messagebox.showerror("Deletion Error", msg)

    # --------------------------------------------------------------------------
    # REFRESH & EXIT HELPERS
    # --------------------------------------------------------------------------

    def refresh_all_data(self):
        """Updates KPI counters and treeview records."""
        stats = DataManager.get_statistics()
        self.kpi_total_lbl.config(text=str(stats["total"]))
        self.kpi_approved_lbl.config(text=str(stats["approved"]))
        self.kpi_rejected_lbl.config(text=str(stats["rejected"]))
        self.kpi_pending_lbl.config(text=str(stats["pending"]))
        self._populate_table()

    def _on_exit(self):
        """
        Safely closes the Admin Panel, clears the active admin session,
        and returns user focus to the Main Home Screen without exiting the entire app.
        """
        if messagebox.askyesno("Exit Admin Panel", "Do you wish to log out and close the Admin Panel?"):
            self.destroy()
            if self.master and hasattr(self.master, "deiconify"):
                self.master.deiconify()
                if hasattr(self.master, "update_stats_display"):
                    self.master.update_stats_display()


# ==============================================================================
# MAIN HOME APPLICATION WINDOW
# ==============================================================================

class ScholarshipApp(tk.Tk):
    """
    Main Application Window:
      - Title: Student Scholarship Management System
      - Clean branding and project overview
      - Student Registration Button (Green)
      - Admin Login Button (Blue)
      - Exit Application Button (Black)
    """

    def __init__(self):
        super().__init__()
        self.title("Student Scholarship Management System")
        self.config(bg=COLOR_BG)
        center_window(self, 780, 620)
        self.resizable(False, False)

        # Initialize data file
        DataManager.ensure_file_exists()

        self._build_ui()
        self.update_stats_display()

    def _build_ui(self):
        # Header Branding Banner
        header = tk.Frame(self, bg=COLOR_PRIMARY_BLUE, height=100)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        title_lbl = tk.Label(
            header,
            text="🎓 Student Scholarship Management System",
            font=("Helvetica", 18, "bold"),
            bg=COLOR_PRIMARY_BLUE,
            fg="white"
        )
        title_lbl.pack(pady=(20, 4))

        sub_lbl = tk.Label(
            header,
            text="Automated Merit-Cum-Means Scholarship Registration & Verification Portal",
            font=("Helvetica", 10),
            bg=COLOR_PRIMARY_BLUE,
            fg="#E3F2FD"
        )
        sub_lbl.pack()

        # Central Container Card
        center_card = tk.Frame(self, bg=COLOR_CARD_BG, bd=1, relief=tk.SOLID, padx=35, pady=25)
        center_card.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # Welcome message and project description
        welcome_title = tk.Label(
            center_card,
            text="Welcome to the Scholarship Portal",
            font=("Helvetica", 14, "bold"),
            bg=COLOR_CARD_BG,
            fg=COLOR_TEXT_MAIN
        )
        welcome_title.pack(anchor="w", pady=(0, 6))

        desc_text = (
            "This application streamlines scholarship distribution through a transparent, "
            "rules-based verification pipeline. Students can self-register without an admin account, "
            "while authorized administrators evaluate eligibility, maintain student records, "
            "and manage awards permanently using local persistence in 'students.txt'."
        )
        desc_lbl = tk.Label(
            center_card,
            text=desc_text,
            font=("Helvetica", 10),
            bg=COLOR_CARD_BG,
            fg=COLOR_TEXT_MUTED,
            wraplength=640,
            justify=tk.LEFT
        )
        desc_lbl.pack(anchor="w", pady=(0, 20))

        # Navigation Action Cards
        btn_container = tk.Frame(center_card, bg=COLOR_CARD_BG)
        btn_container.pack(fill=tk.X, pady=10)

        # 1. Student Registration Button (Green)
        self.reg_btn = create_styled_button(
            btn_container,
            text="📝  Student Registration",
            command=self._open_registration,
            bg_color=COLOR_PRIMARY_GREEN,
            hover_color=COLOR_HOVER_GREEN,
            fg_color="white",
            font=("Helvetica", 12, "bold"),
            height=2
        )
        self.reg_btn.pack(fill=tk.X, pady=6)

        # 2. Admin Login Button (Blue)
        self.login_btn = create_styled_button(
            btn_container,
            text="🔒  Administrator Login",
            command=self._open_admin_login,
            bg_color=COLOR_PRIMARY_BLUE,
            hover_color=COLOR_HOVER_BLUE,
            fg_color="white",
            font=("Helvetica", 12, "bold"),
            height=2
        )
        self.login_btn.pack(fill=tk.X, pady=6)

        # 3. Exit Application Button (Black)
        self.exit_btn = create_styled_button(
            btn_container,
            text="✕  Exit Application",
            command=self._on_exit_app,
            bg_color=COLOR_DARK,
            hover_color=COLOR_DARK_HOVER,
            fg_color="white",
            font=("Helvetica", 12, "bold"),
            height=2
        )
        self.exit_btn.pack(fill=tk.X, pady=6)

        # Footer Status Bar
        footer = tk.Frame(self, bg="#ECEFF1", height=40)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)

        self.footer_status_lbl = tk.Label(
            footer,
            text="Storage: students.txt | Total Applications: 0",
            font=("Helvetica", 9),
            bg="#ECEFF1",
            fg=COLOR_TEXT_MUTED
        )
        self.footer_status_lbl.pack(side=tk.LEFT, padx=15, pady=8)

        version_lbl = tk.Label(
            footer,
            text="Python Tkinter Desktop Suite",
            font=("Helvetica", 9),
            bg="#ECEFF1",
            fg=COLOR_TEXT_MUTED
        )
        version_lbl.pack(side=tk.RIGHT, padx=15, pady=8)

    def update_stats_display(self):
        """Refreshes total count on footer."""
        stats = DataManager.get_statistics()
        self.footer_status_lbl.config(
            text=f"Storage: {os.path.basename(DATA_FILE)} | "
                 f"Total: {stats['total']} | "
                 f"Approved: {stats['approved']} | "
                 f"Rejected: {stats['rejected']} | "
                 f"Pending: {stats['pending']}"
        )

    def _open_registration(self):
        """Launches the separate Student Registration Window."""
        RegistrationWindow(self)

    def _open_admin_login(self):
        """Launches the separate Admin Login Window."""
        AdminLoginWindow(self, on_success_callback=self._open_admin_panel)

    def _open_admin_panel(self):
        """Opens Admin Dashboard after successful authentication."""
        AdminPanelWindow(self)

    def _on_exit_app(self):
        """Confirms and terminates application safely."""
        if messagebox.askyesno("Exit Application", "Are you sure you want to exit the Student Scholarship Management System?"):
            self.destroy()
            sys.exit(0)


# ==============================================================================
# ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    app = ScholarshipApp()
    app.mainloop()
