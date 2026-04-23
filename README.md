# 🏗️ Project Tracking Dashboard
*A Streamlit-based Business Intelligence tool for construction project tracking.*

---

## 📘 Overview
The **Project Tracking Dashboard** is an interactive web application built with **Python + Streamlit**, designed to help construction managers, engineers, and executives visualize and monitor multiple projects in one unified view.

It reads data directly from **Excel or CSV** files and automatically transforms them into **beautiful, data-rich project cards** showing status indicators, fabrication progress, deadlines, and notes — all within an intuitive and responsive dashboard interface.

## Live Dashboard
[View the Streamlit Dashboard](https://escon-builder.streamlit.app/)

---

## ✨ Key Features

### 🔹 Smart Data Handling
- Upload project data in `.csv` or `.xlsx` format.
- Automatically validates column names and identifies missing or empty fields.
- Generates detailed upload warnings for incomplete records.

### 🔹 Dynamic Project Cards
Each card presents:
- **Project Name** (uppercase, bold, and prominent)
- **Installation Dates**
- **Collapsible “Project Details”** (Address, Contractor, Contact, Phone, Email, Deadline)
- **Status Pills** — five visual indicators (SUB, SD, C, MA, MO) with tooltips:
  - ✅ Green for *Yes*
  - ❌ Red for *No*
  - ➖ Gray for *None* (missing data)
- **Fabrication Progress (FP)** displayed as a percentage.
- **Notes** section that automatically displays the full project note text.

### 🔹 Clean Visual Design
- Minimalist white card design with shadows and hover effects.
- Bordered containers for progress and notes.
- Responsive three-column layout that adapts to ultra-wide monitors.
- Subtle color scheme based on client’s branding.

### 🔹 Interactive UX
- Expandable “Project Details” section for each project.
- Sidebar file uploader for quick data refresh.
- Automatic validation alerts and collapsible warning panel.

### 🔹 Built-in Styling System
- External `styles.css` file handles all layout, fonts, and hover effects.
- Fallback `DEFAULT_CSS` ensures consistent design even if no external stylesheet is present.

---

## 🧠 Technical Architecture

| Component | Description |
|------------|-------------|
| **Frontend** | Streamlit framework with HTML + CSS customization |
| **Backend Logic** | Python (Pandas + DuckDB) for file parsing and in-memory querying |
| **Visualization** | Custom HTML components + Streamlit UI containers |
| **Styling** | External CSS (`styles.css`) for cards, pills, typography, and layout |
| **Data Input** | Excel/CSV files uploaded through Streamlit’s sidebar |
| **Data Fields** | Project Name, Address, Contractor, Contact, Phone, Email, Dates, FP, Notes, and 5 Status flags |

---

## 🧩 File Structure

```
project-dashboard/
│
├── app.py                     # Main Streamlit app
├── styles.css                 # External styling (cards, layout, fonts)
├── project_data.csv           # Sample project dataset
└── README.md                  # Documentation file
```
## Data Model
The app expects these columns (case-sensitive):

| Column                    | Type    | Description                                         |
|---------------------------|---------|-----------------------------------------------------|
| `Project Name`            | string  | Display title (rendered uppercase)                  |
| `Project Address`         | string  | Address                                             |
| `General Contractor`      | string  | GC / Company name                                   |
| `Contact Person`          | string  | Primary contact                                     |
| `Phone Number`            | string  | Contact phone                                       |
| `Email Address`           | string  | Contact email                                       |
| `Installation Dates`      | string  | Free-form date range                                |
| `Deadline`                | date/str| Deadline (parsed & shown as `Month DD, YYYY`)       |
| `Fabrication Progress`    | number  | 0–100 (supports `%` suffix)                         |
| `Notes`                   | string  | Free-form notes                                     |
| `Submittal Approved`      | yes/no  | Status pill                                         |
| `Shop Drawings Approved`  | yes/no  | Status pill                                         |
| `Correction Made`         | yes/no  | Status pill                                         |
| `Material Arrived`        | yes/no  | Status pill                                         |
| `Material Ordered`        | yes/no  | Status pill                                         |

> Missing data is tolerated; pills show **Blank** when a field is absent.
---

## ⚙️ How It Works

1. **Upload File:**  
   Choose an Excel or CSV file via the sidebar.

2. **Validation:**  
   The app checks that all required columns exist and flags missing data.

3. **Display:**  
   Each project is rendered as an interactive card with collapsible sections.

4. **Insight:**  
   Users can instantly see project health, status, deadlines, and notes — no manual formatting required.

---

## 💻 Requirements

- Python ≥ 3.9
- Streamlit
- Pandas
- DuckDB
- Plotly (optional, reserved for future gauges or charts)

### Install Dependencies
```bash
pip install streamlit pandas duckdb plotly
```

### Run the App
```bash
streamlit run app.py
```

---

## 🧱 Design Highlights

- Consistent **card-based layout** for clarity and focus.
- **Color-coded status pills** simplify visual scanning.
- Optimized for **large display screens** (up to 2600 px width).
- Modular functions for easy future expansion (e.g., charts, KPIs, project timelines).

---
## Quick Start
### 1) Install dependencies
```bash
pip install -U streamlit pandas duckdb plotly
```

### 2) Run locally
```bash
streamlit run app.py
```

### 3) Upload data
Use the sidebar uploader to select a `.csv` or `.xlsx` file. The app renders three cards per row by default.

---

## Usage
- **Upload Warnings**: Expand the “Upload Warnings” panel to review missing fields.
- **Project Details**: Use the expander per card for Address, Contractor, Contact, Phone, Email, and Deadline.
- **Notes**: Full notes are displayed in a bordered box; use it for field updates and decisions.
- **Fabrication Progress**: Parsed from `0–100` or strings like `75%`, clamped safely.


## 🧮 Future Enhancements

- Add interactive charts for fabrication progress trends.
- Enable filtering and sorting by contractor, region, or project phase.
- Integrate auto-refresh from Google Sheets or SQL database.
- Support PDF/Excel export of dashboard views.

---

## 👤 Author

**Sina Shariati**  
📍 Business Intelligence Analyst  
🔗 [LinkedIn Profile](https://www.linkedin.com/in/sina-shariati-5a26227a/)

---

## 🪶 Portfolio Summary

**Project:**  Project Tracking Dashboard  
**Role:** Developer & Designer  
**Tech Stack:** Python, Streamlit, Pandas, DuckDB, CSS  
**Purpose:** To streamline project monitoring and improve visibility across construction operations.  
**Impact:** Delivered an automated, interactive BI tool that replaced static spreadsheets with a live visual dashboard accessible to project managers and executives.
