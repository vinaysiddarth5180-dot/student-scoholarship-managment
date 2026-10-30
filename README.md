# Student Scholarship Management System (Python Tkinter GUI)

A desktop application developed in Python 3 using Tkinter and ttk for automating student scholarship registration, eligibility verification, and record management with transparent file persistence in `students.txt`.

---

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [System Architecture](#system-architecture)
4. [Scholarship Eligibility Criteria](#scholarship-eligibility-criteria)
5. [Default Admin Credentials](#default-admin-credentials)
6. [Data Storage Format (students.txt)](#data-storage-format-studentstxt)
7. [Installation & Setup](#installation--setup)
8. [Running in Visual Studio Code](#running-in-visual-studio-code)
9. [Detailed Workflow Guide](#detailed-workflow-guide)
10. [Comprehensive Test Cases](#comprehensive-test-cases)
11. [Academic Project Demonstration Script](#academic-project-demonstration-script)

---

## 1. Project Overview

The **Student Scholarship Management System** bridges the gap between scholarship applicants and academic administrators:
- **For Students:** Self-registration portal allowing submission without requiring admin credentials. Automatic validation ensures complete and accurate submissions with an auto-generated unique ID (`SCH-1001`, `SCH-1002`, etc.) and initial status `Pending`.
- **For Administrators:** Password-protected dashboard featuring:
  - **Check Eligibility:** Automatic rules engine checking Age, Marks, and Family Income with status transition to `Approved` or `Rejected` and itemized rejection reasons.
  - **View All Records:** Interactive `ttk.Treeview` table with color-coded rows (Green for Approved, Red for Rejected, Amber for Pending), search by Name/ID, and status filtering.
  - **Delete Record:** Permanent record removal with confirmation safeguards.
  - **Persistent Storage:** Safe JSON Lines format in `students.txt`, with automatic file initialization, corruption tolerance, and atomic updates.

---

## 2. Technology Stack

- **Programming Language:** Python 3 (Python 3.8+)
- **GUI Framework:** Python Tkinter (`tkinter`, `tkinter.ttk`, `tkinter.messagebox`)
- **Persistence:** Python native file handling (`open()`, `read()`, `write()`, `json`)
- **Data Format:** JSON Lines (`students.txt`)
- **External Dependencies:** **None** (Built entirely on Python standard library)

---

## 3. System Architecture

```
student_scholarship_management.py
│
├── DataManager (File Handling & Business Logic)
│   ├── ensure_file_exists()          -> Auto-creates students.txt
│   ├── load_all_students()           -> Parses JSON lines gracefully
│   ├── save_all_students()           -> Atomic write via temporary file
│   ├── generate_unique_id()          -> Auto-increments (SCH-1001, SCH-1002)
│   ├── add_student()                 -> Saves new applicant (Status: Pending)
│   ├── get_student_by_id()           -> Case-insensitive ID lookup
│   ├── evaluate_scholarship_eligibility() -> Rules evaluation & updates
│   ├── delete_student()              -> Confirmed record deletion
│   └── get_statistics()              -> Total, Approved, Rejected, Pending counts
│
├── ScholarshipApp (Main Home Window - tk.Tk)
│   ├── Student Registration Button   (Green #2E7D32)
│   ├── Admin Login Button            (Blue #1565C0)
│   └── Exit Application Button       (Black #212121)
│
├── RegistrationWindow (tk.Toplevel)
│   ├── Form validation (Name, Age > 0, Marks 0-100, Income >= 0)
│   ├── Unique ID assignment (SCH-XXXX)
│   └── Clear Form & Back to Home
│
├── AdminLoginWindow (tk.Toplevel)
│   ├── Credential check (admin / admin123)
│   └── Password masking with toggle
│
├── AdminPanelWindow (tk.Toplevel - Dashboard)
│   ├── KPI Metric Cards (Total, Approved, Rejected, Pending)
│   ├── Tab 1: Check Scholarship Eligibility (Blue)
│   ├── Tab 2: View All Students (ttk.Treeview table with filters)
│   ├── Tab 3: Delete Student Record (Red)
│   └── Exit Admin Panel Button (Black)
│
└── ViewStudentsWindow (tk.Toplevel)
    └── Dedicated separate table viewer with live search & filtering
```

---

## 4. Scholarship Eligibility Criteria

All conditions must be satisfied simultaneously for an application to be marked **Approved**:

| # | Parameter | Requirement | Status if Met | Status if Failed |
|---|-----------|-------------|---------------|------------------|
| 1 | **Age** | $\ge 18\text{ years}$ | Pass | Ineligible (Age below 18) |
| 2 | **Academic Marks** | $\ge 60.0\%$ | Pass | Ineligible (Marks below 60%) |
| 3 | **Annual Family Income** | $\le \text{₹}2,50,000$ | Pass | Ineligible (Income exceeds limit) |

> **Evaluation Rule:**
> - If **Rule 1 AND Rule 2 AND Rule 3** are satisfied $\rightarrow$ **Approved**
> - If **ANY Rule** fails $\rightarrow$ **Rejected** with an itemized explanation of all failing conditions.

---

## 5. Default Admin Credentials

> [!NOTE]
> For academic evaluation and demonstration, the administrator credentials are:
> - **Username:** `admin`
> - **Password:** `admin123`

*(In production systems, credentials must never be hardcoded. They should be stored as salted cryptographic hashes like Argon2 or bcrypt, with access controlled via environment variables or a key vault).*

---

## 6. Data Storage Format (`students.txt`)

Data is stored line-by-line using **JSON Lines (JSONL)** format inside `students.txt`:

```json
{"id": "SCH-1001", "name": "Aarav Sharma", "age": 20, "marks": 84.5, "income": 180000.0, "status": "Approved", "reason": "Eligible: Meets all criteria (Age >= 18, Marks >= 60%, Family Income <= Rs. 250,000).", "timestamp": "2026-10-30 10:15:00", "evaluated_at": "2026-10-30 10:30:00"}
{"id": "SCH-1002", "name": "Diya Patel", "age": 19, "marks": 78.0, "income": 220000.0, "status": "Pending", "reason": "Application registered; pending administrator review.", "timestamp": "2026-10-30 10:45:00"}
{"id": "SCH-1003", "name": "Rohan Iyer", "age": 17, "marks": 88.0, "income": 150000.0, "status": "Rejected", "reason": "Ineligible: Age (17 yrs) is below minimum requirement of 18 yrs.", "timestamp": "2026-10-30 11:00:00", "evaluated_at": "2026-10-30 11:15:00"}
```

**Benefits of this format:**
- **Crash Resilience:** Adding a student is an atomic append operation.
- **Delimiter Immunity:** Student names containing commas, hyphens, or spaces do not corrupt columns.
- **Human Readable:** Can be opened and inspected directly in Notepad or VS Code.

---

## 7. Installation & Setup

1. **Verify Python 3 is installed:**
   Open PowerShell or Command Prompt:
   ```powershell
   python --version
   ```
   If Python is not installed, download and install Python 3.10+ from [python.org](https://www.python.org/downloads/) (make sure to check **"Add python.exe to PATH"** during installation).

2. **No external pip packages required:**
   Tkinter and json are part of the standard Python library.

---

## 8. Running in Visual Studio Code

1. Open VS Code.
2. Select **File > Open Folder...** and select `c:\Users\PRANEETH K S\Downloads\scohalarship`.
3. Open `student_scholarship_management.py`.
4. Open the integrated terminal (`Ctrl + ~` or **Terminal > New Terminal**).
5. Run the application:
   ```powershell
   python student_scholarship_management.py
   ```
6. Alternatively, click the **Play / Run Python File** button in the top right corner of VS Code.

---

## 9. Comprehensive Test Cases

| Test Case | Inputs | Expected Result | Verified Status |
|---|---|---|---|
| **1. Eligible Student** | Age: `20`, Marks: `85%`, Income: `₹1,80,000` | Registration: Success (Pending). Admin check: **Approved**. | **PASS** |
| **2. Underage Ineligible** | Age: `17`, Marks: `88%`, Income: `₹1,50,000` | Admin check: **Rejected** ("Age 17 yrs is below 18 yrs"). | **PASS** |
| **3. Low Marks Ineligible** | Age: `21`, Marks: `55%`, Income: `₹1,90,000` | Admin check: **Rejected** ("Marks 55% is below 60%"). | **PASS** |
| **4. High Income Ineligible**| Age: `22`, Marks: `91%`, Income: `₹3,40,000` | Admin check: **Rejected** ("Income exceeds ₹2,50,000"). | **PASS** |
| **5. Multiple Failures** | Age: `16`, Marks: `50%`, Income: `₹4,00,000` | Admin check: **Rejected** (Lists all 3 failures itemized). | **PASS** |
| **6. Duplicate Names** | Name: `Rahul Sharma` registered twice | First gets `SCH-1001`, second gets `SCH-1002`. No collision. | **PASS** |
| **7. Invalid Age Input** | Age: `-5` or `abc` | Pop-up error: "Please enter a valid positive whole number". | **PASS** |
| **8. Invalid Marks Input** | Marks: `105` or `-10` | Pop-up error: "Marks must be between 0.0 and 100.0%". | **PASS** |
| **9. Invalid Income Input** | Income: `-500` or `xyz` | Pop-up error: "Income must be greater than or equal to ₹0". | **PASS** |
| **10. Empty Form** | Any field left blank | Pop-up warning: "All fields are mandatory". | **PASS** |
| **11. Incorrect Admin Login**| Username: `admin`, Password: `wrong` | Pop-up error: "Invalid admin username or password". | **PASS** |
| **12. Non-existent Student**| Search ID: `SCH-9999` | Pop-up error: "No student found with ID 'SCH-9999'". | **PASS** |
| **13. Deletion Safeguard** | Delete student, Cancel confirmation | Record preserved in `students.txt`. | **PASS** |
| **14. Confirmed Deletion** | Delete student, Confirm yes | Record removed; treeview and stats update immediately. | **PASS** |
