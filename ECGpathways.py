import streamlit as st

st.title("SEC 2027 Pathway Eligibility Checker")

# --- 1. DEFINE SYLLABUS LISTS ---
g3_only_subjects = [
    "Arabic as a 3rd Language", "Bahasa Indonesia as a 3rd Language", "Economics", 
    "Drama", "Spanish", "French", "German", "Japanese", "Physics", "Chemistry", 
    "Biology", "Electronics", "Music", "Higher Music", "Higher Art", "Biotechnology", 
    "Design Studies", "Higher Chinese", "Chinese (Special Programme)", "Literature in Chinese",
    "Higher Malay", "Malay (Special Programme)", "Literature in Malay", "Higher Tamil", 
    "Literature in Tamil", "Exercise And Sports Science", "Business"
]

overlapping_subjects = [
    "English Language", "Mathematics", "Additional Mathematics", "Literature in English", 
    "History", "Geography", "Humanities (Social Studies, Geography)", 
    "Humanities (Social Studies, History)", "Humanities (Social Studies, Literature in English)", 
    "Computing", "Science (Physics, Chemistry)", "Science (Physics, Biology)", 
    "Science (Chemistry, Biology)", "Nutrition and Food Science", "Art", 
    "Design & Technology", "Principles of Accounts", "Chinese Language", 
    "Malay Language", "Tamil Language", "Bengali", "Gujarati", "Hindi", "Panjabi", "Urdu"
]

all_selectable_subjects = sorted(g3_only_subjects + overlapping_subjects)

# Grade scale definitions
g3_grades = ["A1", "A2", "B3", "B4", "C5", "C6", "D7", "E8", "9"]
g2_grades = ["1", "2", "3", "4", "5", "6"]

# --- 2. STEP 1: SUBJECT ENTRY ---
st.write("### Step 1: Select Your Subjects")
selected_subjects = st.multiselect(
    "Choose all the subjects you are currently taking:",
    options=all_selectable_subjects
)

# Dictionaries to track final validated levels and grades
subject_levels = {}
subject_grades = {}

# --- 3. STEP 2: LEVEL & GRADE RESOLUTION ---
if selected_subjects:
    st.write("---")
    st.write("### Step 2: Assign Subject Levels and Grades")
    
    st.markdown("""
        <style>
        .subject-row {
            padding: 12px 20px;
            border: 1px solid #e6e9ef;
            border-radius: 12px;
            margin-bottom: 10px;
            background-color: #ffffff;
        }
        </style>
    """, unsafe_allow_html=True)

    for subject in selected_subjects:
        with st.container():
            # col1 for Subject Name, col2 for Level buttons, col3 for Grade Dropdown
            col1, col2, col3 = st.columns([2, 1.2, 1], vertical_alignment="center")
            
            with col1:
                st.markdown(f"**{subject}**")
                
            # Determine Level Selection
            with col2:
                if subject in overlapping_subjects:
                    chosen_level = st.segmented_control(
                        label=f"Level for {subject}",
                        options=["G2", "G3"],
                        default="G3",
                        label_visibility="collapsed",
                        key=f"level_{subject}"
                    )
                    subject_levels[subject] = chosen_level if chosen_level else "G3"
                else:
                    st.segmented_control(
                        label=f"Level for {subject}",
                        options=["G3"],
                        default="G3",
                        disabled=True,
                        label_visibility="collapsed",
                        key=f"level_{subject}"
                    )
                    subject_levels[subject] = "G3"
            
            # Determine Grade Selection based on chosen level
            with col3:
                current_level = subject_levels[subject]
                available_grades = g3_grades if current_level == "G3" else g2_grades
                
                chosen_grade = st.selectbox(
                    label=f"Grade for {subject}",
                    options=available_grades,
                    label_visibility="collapsed",
                    key=f"grade_{subject}"
                )
                subject_grades[subject] = chosen_grade

    # --- 4. STEP 3: DYNAMIC COUNTING & EVALUATION ---
    st.write("---")
    
    g3_count = sum(1 for lvl in subject_levels.values() if lvl == "G3")
    g2_count = sum(1 for lvl in subject_levels.values() if lvl == "G2")
    
    st.metric(label="Total G3 Subjects", value=g3_count)
    st.metric(label="Total G2 Subjects", value=g2_count)
    
    # Pathway status tracking
    pathways = {
        "Junior College": {"open": False, "reason": ""},
        "Polytechnic Year 1": {"open": False, "reason": ""},
        "Polytechnic Foundation Programme": {"open": False, "reason": ""}
    }
    
    # 1. Junior College Logic
    if g3_count >= 5:
        pathways["Junior College"]["open"] = True
    else:
        pathways["Junior College"]["reason"] = f"Requires at least 5 G3 subjects (You have {g3_count})."

    # 2. Polytechnic Year 1 Logic
    if g3_count >= 5 or (g3_count == 4 and g2_count >= 1):
        pathways["Polytechnic Year 1"]["open"] = True
    else:
        if g3_count == 4:
            pathways["Polytechnic Year 1"]["reason"] = f"You have 4 G3 subjects, but require at least 1 G2 subject (You have {g2_count})."
        else:
            pathways["Polytechnic Year 1"]["reason"] = f"Requires 5+ G3 subjects, OR exactly 4 G3 subjects with at least 1 G2 subject (You have {g3_count} G3)."

    # 3. Polytechnic Foundation Programme Logic
    if g3_count >= 5 or (g3_count == 4 and g2_count >= 1) or (g3_count <= 3 and g2_count >= 5):
        pathways["Polytechnic Foundation Programme"]["open"] = True
    else:
        pathways["Polytechnic Foundation Programme"]["reason"] = f"Requires at least 5 G2 subjects when taking 3 or fewer G3 subjects (You have {g3_count} G3 and {g2_count} G2)."

    # --- 5. DISPLAY PATHWAY STATUSES ---
    st.write("### Pathway Eligibility Status")
    
    for name, info in pathways.items():
        if info["open"]:
            st.success(f"✅ **{name}** is **Available**")
        else:
            st.error(f"❌ **{name}** is **Not Available** \n*Reason: {info['reason']}*")
else:
    st.info("Please choose your subjects above to calculate your eligibility.")