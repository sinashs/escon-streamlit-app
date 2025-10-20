import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import pandas as pd
import duckdb as db
import plotly.graph_objects as go  # kept if you later want gauges
from datetime import datetime
from io import BytesIO
import warnings, os
import sys


warnings.filterwarnings("ignore")

# ------------------------- Page / Styles -------------------------
st.set_page_config(page_title="Escon Builders Project Dashboard", layout="centered", initial_sidebar_state="expanded")

# Load external CSS (single file, per instructions)
CSS_PATH = "styles.css"
# DEFAULT_CSS = """
# /* Container width for big displays */
# .block-container { padding-top: 1rem; padding-bottom: 1rem; max-width: 2600px; }
# .project-card { background:#fff; padding:12px 14px; border-radius:12px; border:1px solid #ececf1;
#                 box-shadow:0 1px 2px rgba(0,0,0,.04); margin-bottom:10px; }
# .project-card h4 { margin:0; font-size:1.15rem; letter-spacing:-.2px; font-weight:800; text-align:center; }
# .compact { line-height:1.15; }
# .title-center { text-align:center; }
# .pill { color:#fff; padding:10px 12px; border-radius:12px; text-align:center; font-weight:700;
#         box-shadow:0 1px 4px rgba(0,0,0,.12); }
# .pill .label { font-size:12px; opacity:.9; display:block; }
# .pill .value { font-size:18px; }
# .pill-yes { background:#198754; }    /* green */
# .pill-no  { background:#dc3545; }    /* red   */
# .fp-number { font-size:18px; font-weight:500; text-align:center; margin:6px 0 0; }
# .footer { text-align:center; margin-top:8px; font-size:0.9rem; }
# """

def load_css():
    #css_text = DEFAULT_CSS
    if os.path.exists(CSS_PATH):
        try:
            with open(CSS_PATH, "r", encoding="utf-8") as f:
                css_text = f.read()
        except Exception:
            pass
    st.markdown(f"<style>{css_text}</style>", unsafe_allow_html=True)

load_css()

# ------------------------- Title / Footer -------------------------
st.markdown('<div class="title-center">', unsafe_allow_html=True)
#st.title("Escon Builders Project Dashboard", width = 'stretch')
# Smaller title using Markdown and custom HTML
st.markdown("<h4 style='font-size: 5px;'>Escon Builders Project Dashboard</h4>", unsafe_allow_html=True)
#st.markdown('</div>', unsafe_allow_html=True)


# ------------------------- Helpers / Config -------------------------
EXPECTED_COLUMNS = [
    "Project Name", "Project Address", "General Contractor",
    "Contact Person", "Phone Number", "Email Address", "Installation Dates", "Deadline",
    "Fabrication Progress", "Notes",
    # Status fields (Yes/No)
    "Submittal Approved", "Shop Drawings Approved", "Correction Made", "Material Arrived", "Material Ordered"
]

# Abbreviation map + full-name tooltips
STATUS_ABBR = {
    "Submittal Approved": ("SUB", "Submittal Approved"),
    "Shop Drawings Approved": ("SD", "Shop Drawings Approved"),
    "Correction Made": ("C", "Correction Made"),
    "Material Ordered": ("MO", "Material Ordered"),
    "Material Arrived": ("MA", "Material Arrived")
}

def parse_progress(val) -> int:
    """Accepts '75', '75%', None, clamps to [0,100]."""
    if val is None:
        return 0
    s = str(val).strip().replace("%", "")
    try:
        n = int(float(s))
    except Exception:
        return 0
    return max(0, min(100, n))

def pill_html(label_abbr: str, full_label: str, value) -> str:
    is_yes = str(value).strip().lower() == "yes"
    klass = "pill pill-yes" if is_yes else "pill pill-no"
    emoji = "✅" if is_yes else "❌"
    # title attribute provides hover tooltip with full label name
    return (
        f"<div class='{klass}' title='{full_label}'>"
        f"<span class='label'>{label_abbr}</span>"
        f"<span class='value'>{emoji} {'Yes' if is_yes else 'No'}</span>"
        f"</div>"
    )

def render_project_card(proj: pd.Series, idx: int):
    # --- Card Header: Project Title (uppercase & larger) ---
    
    
    project_name = (proj.get('Project Name', '') or '').upper()  # force uppercase
    st.markdown(
        f"""
        <div class='project-title-section'>
            <div class='project-title'>
                {project_name}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown('<div class="small-space"></div>', unsafe_allow_html=True)  # space between title and rest
    
    # --- Installation Dates (smaller text below) ---
    st.markdown(
        f"""
        <div class='install-dates-section'>
            <div class='install-dates'>
                <b>Installation Dates:</b> {proj.get('Installation Dates','')}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    # --- Details Section (collapsible) ---
    # Collapsible details
    with st.expander("Project Details", expanded=False):
        

        # Row 1 (center-aligned Address and Contractor)
        c1, c2 = st.columns(2)

        with c1:
            st.markdown(
                f"""
                <div class='project-details compact center-text'>
                    <b>Address:</b><br>
                    {proj.get('Project Address','')}
                </div>
                """,
                unsafe_allow_html=True
            )

        with c2:
            st.markdown(
                f"""
                <div class='project-details compact center-text'>
                    <b>Contractor:</b><br>
                    {proj.get('General Contractor','')}
                </div>
                """,
                unsafe_allow_html=True
            )

        # Row 2
        st.write(
            f"<div class='project-details compact'><b> Contact:</b> {proj.get('Contact Person','')}</div>",
            unsafe_allow_html=True
        )
        # Row 3
        st.write(
            f"<div class='project-details compact'><b> Phone:</b> {proj.get('Phone Number','')}</div>",
            unsafe_allow_html=True
        )
        # Row 4
        st.write(
            f"<div class='project-details compact'><b> Email:</b> {proj.get('Email Address','')}</div>",
            unsafe_allow_html=True
        )
        #Row 5
        # Row 5 - formatted Deadline
        deadline_raw = proj.get("Deadline", "")
        formatted_deadline = deadline_raw  # fallback if not a valid date

        if pd.notna(deadline_raw) and str(deadline_raw).strip():
            try:
                # Try to parse common date formats
                deadline_date = pd.to_datetime(deadline_raw)
                formatted_deadline = deadline_date.strftime("%B %d, %Y")  # Example: September 15, 2025
            except Exception:
                formatted_deadline = str(deadline_raw)  # if parsing fails, show as-is

        st.markdown(
            f"<div class='project-details compact'><b>Deadline:</b> {formatted_deadline}</div>",
            unsafe_allow_html=True
        )
            
    #status_pill_col = st.columns(1)[0]

    # with status_pill_col:

    #     # Status pills row (SUB, SD, C, MO, MA) with abbreviations + hover tooltips
    #    #st.markdown("<div class='status-section'>", unsafe_allow_html=True)
    #     s_cols = st.columns(5)
    #     for i, field in enumerate(STATUS_ABBR.keys()):
    #         abbr, full = STATUS_ABBR[field]
    #         # Get field value safely
    #         value = proj.get(field, "")
    #         # If value missing, show "None"
    #         if pd.isna(value) or str(value).strip() == "":
    #             value = "None"
    #         else: 
    #             with s_cols[i]:
    #                 st.markdown(pill_html(abbr, full, value), unsafe_allow_html=True)
    #     st.markdown("</div>", unsafe_allow_html=True)
    

    status_pill_col = st.container()

    with status_pill_col:
        # Inject global CSS ONCE to force black text in the control and in the dropdown menu (BaseWeb portal)
        st.markdown(
            """
            <style>
            /* Control text & placeholder */
            div[data-baseweb="select"] div,
            div[data-baseweb="select"] span {
                color: black !important;
            }
            /* Dropdown menu items (BaseWeb renders the menu in a portal) */
            ul[role="listbox"] li,
            div[data-baseweb="menu"] *,
            div[role="listbox"] * {
                color: black !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        with st.container(border=True):
            s_cols = st.columns(5)

            for i, field in enumerate(STATUS_ABBR.keys()):
                full = STATUS_ABBR[field][1]
                abrr = STATUS_ABBR[field][0]
                safe_field = field.replace(" ", "_").replace("/", "_")
                key_name = f"status_{idx}_{safe_field}"

                options = ["Yes", "No"]
                current = st.session_state.get(key_name, "")
                index = options.index(current) if current in options else 0

                # Color the container based on current value
                sv = (current or "").strip().lower()
                if sv == "yes":
                    bg, bd, fg = "#b6e7a5", "#2e7d32", "#1b5e20"   # green theme
                elif sv == "no":
                    bg, bd, fg = "#f4b4b4", "#b71c1c", "#5d0000"   # red theme
                else:
                    bg, bd, fg = "#ffffff", "#d3d3d3", "#000000"   # neutral (fallback)

                with s_cols[i]:
                    # NOTE: stylable_container uses 'css', not 'css_styles'
                    with stylable_container(
                        key=f"statuswrap-{idx}-{i}",
                        css_styles=f"""
                        {{
                            background-color: {bg};
                            border: 2px solid {bd};
                            border-radius: 8px;
                            padding: 1px 1px;
                            margin-top: 1px;
                        }}
                        """
                    ):
                        selected_value = st.selectbox(
                            label=abrr,                # keep your abbreviation label
                            options=options,
                            index=index,
                            key=key_name,
                            label_visibility="visible",
                            help = full  # full label as tooltip
                        )

        
    fp_notes_col = st.container()
    with fp_notes_col:

        # Progress (.25) next to Notes (.75)
        left, right = st.columns([1, 3])
        with left:
            fp = parse_progress(proj.get("Fabrication Progress"))
            #st.metric(label="FP", value=f"{fp}%")
            
            st.markdown("<div class='project-details compact center-text'><b>FP: </b></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='project-details compact fp-number'>{fp}%</div>", unsafe_allow_html=True)

        with right:
            # --- Notes section (always show full text) ---
            note_text = (proj.get("Notes", "") or "").strip()

            st.markdown(
                f"""
                <div class='notes-box'>
                    <b>Notes:</b><br>
                    {note_text if note_text else "No notes available."}
                </div>
                """,
                unsafe_allow_html=True
            )


# ------------------------- File Input -------------------------
st.sidebar.header("Upload Your Project Data file")
uploaded = st.sidebar.file_uploader("Upload Project Data (CSV or Excel)", type=["csv", "xlsx", "xls"])

# Fallback: load sample if nothing uploaded but sample exists
df_excel = None
source_label = None

def read_any_file(uploaded_file):
    """Read CSV/XLSX from Streamlit uploader or path-like buffer."""
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    else:
        return pd.read_excel(uploaded_file)

if uploaded is not None:
    df_excel = read_any_file(uploaded)
    source_label = f"Loaded: {uploaded.name}"


if df_excel is None or df_excel.empty:
    st.warning("Please upload a CSV or Excel file to proceed.")
    st.stop()

if source_label:
    st.caption(source_label)

# ------------------------- DuckDB passthrough -------------------------
df = db.query("SELECT * FROM df_excel").to_df()

# ------------------------- Schema Checks / Warnings -------------------------
missing_cols = [c for c in EXPECTED_COLUMNS if c not in df.columns]
if missing_cols:
    st.error(
        "The file is missing expected columns: " + ", ".join(missing_cols) +
        ". The app will still try to render cards, but some fields will be blank."
    )

# Per-row warnings (missing expected fields)
row_warnings = []
for idx, row in df.iterrows():
    missing_in_row = [c for c in EXPECTED_COLUMNS if c in df.columns and pd.isna(row.get(c))]
    if missing_in_row:
        proj_name = row.get("Project Name")
        if pd.isna(proj_name) or str(proj_name).strip() == "":
            row_warnings.append(f"Row {idx + 2}: Missing Project Name.")  # +2 to match Excel-like line numbers
        # For each missing field, warn including the project name if available
        pname = proj_name if (not pd.isna(proj_name) and str(proj_name).strip() != "") else f"Row {idx + 2}"
        for col in missing_in_row:
            row_warnings.append(f"{pname}: missing '{col}'.")

if row_warnings:
    with st.expander("Upload Warnings", expanded=True):
        for w in row_warnings[:200]:  # cap display
            st.warning(w)

# ------------------------- Render Cards (3 per row) -------------------------
n = len(df)

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
for i in range(0, n, 3):
    c1, c2, c3 = st.columns(3)

    # --- Column 1 : GREEN ---
    with c1:
        if i < n:
            with stylable_container(
                    key=f"sc_green_{i}",
                    css_styles="""
                        {
                            width: 100%;
                            box-sizing: border-box;

                            /* Make it bigger */
                            padding: 10px 10px;     /* more inner space */
                            min-height: 260px;      /* taller container */
                            margin: 1px 1px;       /* more outer space */

                            /* keep your look */
                            background-color: #e8f5e9;
                            border-radius: 12px;
                            border: 1px solid #a5d6a7;
                        }
                    """
                ):
                render_project_card(df.iloc[i], i)

    # --- Column 2 : YELLOW ---
    with c2:
        if i + 1 < n:
            with stylable_container(
                    key=f"sc_yellow_{i+1}",
                    css_styles="""
                        {
                            width: 100%;
                            box-sizing: border-box;

                            padding: 10px 10px;
                            min-height: 260px;
                            margin: 1px 1px;

                            background-color: #fffde7;
                            border-radius: 12px;
                            border: 1px solid #ffe082;
                        }
                    """
                ):
                render_project_card(df.iloc[i + 1], i + 1)

    # --- Column 3 : BLUE ---
    with c3:
            if i + 2 < n:
                with stylable_container(
                key=f"sc_blue_{i+2}",
                css_styles="""
                    {
                        width: 100%;
                        box-sizing: border-box;

                        padding: 10px 10px;
                        min-height: 260px;
                        margin: 1px 1px;

                        background-color: #e3f2fd;
                        border-radius: 12px;
                        border: 1px solid #90caf9;
                    }
                """
                                        ):
                    render_project_card(df.iloc[i + 2], i + 2)


    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)


# ------------------------- Footer -------------------------   
cols = st.columns(1)[0]
with cols:
    st.markdown(
    """
    <div class="footer" style="text-align:center; line-height:1.6;">
        <div>Created by: <b>Sina Shariati</b>
        | Contact: <a href="https://www.linkedin.com/in/sina-shariati-5a26227a/" target="_blank">LinkedIn</a></div>
        <div>Business Intelligence Analyst @ Escon Builders</div>
        <div>Copyright © 2025 | All rights reserved.</div>
    </div>
    """,
    unsafe_allow_html=True
)