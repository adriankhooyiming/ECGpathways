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

# Helper functions to check passing thresholds
def check_g3_at_least(grade, target):
    if grade not in g3_grades: return False
    return g3_grades.index(grade) <= g3_grades.index(target)

def check_g2_at_least(grade, target_str):
    if grade not in g2_grades: return False
    return int(grade) <= int(target_str)

# --- 2. STEP 1: SUBJECT ENTRY ---
st.write("### Step 1: Select Your Subjects")
selected_subjects = st.multiselect(
    "Choose all the subjects you are currently taking:",
    options=all_selectable_subjects
)

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
            col1, col2, col3 = st.columns([2, 1.2, 1], vertical_alignment="center")
            
            with col1:
                st.markdown(f"**{subject}**")
                
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
    total_g2_g3_count = g3_count + g2_count
    
    st.metric(label="Total G3 Subjects", value=g3_count)
    st.metric(label="Total G2 Subjects", value=g2_count)
    st.metric(label="Total Combined (G2 + G3) Subjects", value=total_g2_g3_count)
    
    pathways = {
        "Junior College": {"open": False, "reason": []},
        "Polytechnic Year 1": {"open": False, "reason": []},
        "Polytechnic Foundation Programme": {"open": False, "reason": []}
    }
    
    # --- JUNIOR COLLEGE LOGIC ---
    jc_passed_rules = True
    jc_reasons = []

    # A. Level-based structural requirements check first
    el_is_g3 = "English Language" in subject_levels and subject_levels["English Language"] == "G3"
    math_is_g3 = ("Mathematics" in subject_levels and subject_levels["Mathematics"] == "G3") or \
                 ("Additional Mathematics" in subject_levels and subject_levels["Additional Mathematics"] == "G3")

    if not el_is_g3:
        jc_passed_rules = False
        jc_reasons.append("English Language must be taken at the G3 level.")
        
    if not math_is_g3:
        jc_passed_rules = False
        jc_reasons.append("Mathematics or Additional Mathematics must be taken at the G3 level.")

    if g3_count < 5:
        jc_passed_rules = False
        jc_reasons.append(f"Requires at least 5 G3 subjects (You have {g3_count}).")

    # B. Grade validations (Only check if their structural level rules pass)
    if el_is_g3:
        el_grade = subject_grades["English Language"]
        if not check_g3_at_least(el_grade, "C6"):
            jc_passed_rules = False
            jc_reasons.append("English Language at the G3 level should have a minimum grade of C6.")

    if math_is_g3:
        math_passed_grade = False
        math_failures = []
        for math_sub in ["Mathematics", "Additional Mathematics"]:
            if math_sub in subject_levels and subject_levels[math_sub] == "G3":
                if check_g3_at_least(subject_grades[math_sub], "D7"):
                    math_passed_grade = True
                    break
                else:
                    math_failures.append(f"{math_sub} at the G3 level should have a minimum grade of D7.")
        if not math_passed_grade:
            jc_passed_rules = False
            jc_reasons.extend(math_failures)

    # Mother Tongue Validation (Always checked assuming MT exists)
    mt_subjects = ["Chinese Language", "Malay Language", "Tamil Language", "Bengali", "Gujarati", "Hindi", "Panjabi", "Urdu"]
    hmt_subjects = ["Higher Chinese", "Higher Malay", "Higher Tamil"]
    has_mt_selected = False
    mt_passed = False
    mt_failures = []

    for hmt in hmt_subjects:
        if hmt in subject_levels:
            has_mt_selected = True
            if subject_levels[hmt] == "G3" and check_g3_at_least(subject_grades[hmt], "E8"):
                mt_passed = True
                break
            else:
                mt_failures.append(f"{hmt} at the G3 level should have a minimum grade of E8.")

    if not mt_passed:
        for mt in mt_subjects:
            if mt in subject_levels:
                has_mt_selected = True
                lvl = subject_levels[mt]
                grade = subject_grades[mt]
                if lvl == "G3" and check_g3_at_least(grade, "D7"):
                    mt_passed = True
                    break
                elif lvl == "G2" and check_g2_at_least(grade, "5"):
                    mt_passed = True
                    break
                else:
                    req_grade = "D7" if lvl == "G3" else "5"
                    mt_failures.append(f"{mt} at the {lvl} level should have a minimum grade of {req_grade}.")

    if not mt_passed:
        jc_passed_rules = False
        if not has_mt_selected:
            jc_reasons.append("A Mother Tongue or Higher Mother Tongue subject must be selected.")
        else:
            jc_reasons.extend(mt_failures)

    # Finalize Junior College Status
    if jc_passed_rules:
        pathways["Junior College"]["open"] = True
    else:
        pathways["Junior College"]["reason"] = jc_reasons

    # --- OTHER PATHWAYS ---
    # 2. Polytechnic Year 1 Logic
    if g3_count >= 4:
        pathways["Polytechnic Year 1"]["open"] = True
    else:
        pathways["Polytechnic Year 1"]["reason"] = [f"Requires at least 4 G3 subjects (You have {g3_count})."]

    # 3. Polytechnic Foundation Programme Logic
    if total_g2_g3_count >= 5:
        pathways["Polytechnic Foundation Programme"]["open"] = True
    else:
        pathways["Polytechnic Foundation Programme"]["reason"] = [f"Requires at least 5 subjects combined at G2 or G3 level (You have {total_g2_g3_count})."]

    # --- 5. DISPLAY PATHWAY STATUSES ---
    st.write("### Pathway Eligibility Status")
    
    for name, info in pathways.items():
        if info["open"]:
            st.success(f"✅ **{name}** is **Available**")
        else:
            reasons_list = "\n".join([f"- {r}" for r in info["reason"]])
            st.error(f"❌ **{name}** is **Not Available** \n\n*Requirements Not Met:*\n{reasons_list}")
else:
    st.info("Please choose your subjects above to calculate your eligibility.")