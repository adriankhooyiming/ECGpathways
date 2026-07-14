import streamlit as st

st.title("SEC 2027 Pathway Eligibility Checker")

# --- 1. DEFINE SYLLABUS CATEGORIES (For L1R4 structural filtering) ---
humanities_subjects = [
    "Literature in English", "History", "Geography", 
    "Humanities (Social Studies, Geography)", "Humanities (Social Studies, History)", 
    "Humanities (Social Studies, Literature in English)", "Economics", "Drama",
    "Literature in Chinese", "Literature in Malay", "Literature in Tamil",
    "Humanities (Social Studies, Literature in Chinese)", 
    "Humanities (Social Studies, Literature in Malay)", 
    "Humanities (Social Studies, Literature in Tamil)"
]

math_science_subjects = [
    "Mathematics", "Additional Mathematics", "Computing", "Physics", "Chemistry", 
    "Biology", "Electronics", "Science (Physics, Chemistry)", 
    "Science (Physics, Biology)", "Science (Chemistry, Biology)", "Biotechnology"
]

mt_subjects = ["Chinese Language", "Malay Language", "Tamil Language", "Bengali", "Gujarati", "Hindi", "Panjabi", "Urdu"]
hmt_subjects = ["Higher Chinese", "Higher Malay", "Higher Tamil"]

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
    "Humanities (Social Studies, Literature in Malay)", "Humanities (Social Studies, Literature in Chinese)",
    "Humanities (Social Studies, Literature in Tamil)",
    "Computing", "Science (Physics, Chemistry)", "Science (Physics, Biology)", 
    "Science (Chemistry, Biology)", "Nutrition and Food Science", "Art", 
    "Design & Technology", "Principles of Accounts"
] + mt_subjects

all_selectable_subjects = sorted(list(set(g3_only_subjects + overlapping_subjects)))

# Grade score mapping to integer points
g3_grades = ["A1", "A2", "B3", "B4", "C5", "C6", "D7", "E8", "9"]
g3_points = {"A1": 1, "A2": 2, "B3": 3, "B4": 4, "C5": 5, "C6": 6, "D7": 7, "E8": 8, "9": 9}
g2_grades = ["1", "2", "3", "4", "5", "6"]

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

    # --- 4. DATA PROCESSING & EVALUATION ---
    g3_count = sum(1 for lvl in subject_levels.values() if lvl == "G3")
    g2_count = sum(1 for lvl in subject_levels.values() if lvl == "G2")
    total_g2_g3_count = g3_count + g2_count
    
    pathways = {
        "Junior College": {"open": False, "reason": []},
        "Polytechnic Year 1": {"open": False, "reason": []},
        "Polytechnic Foundation Programme": {"open": False, "reason": []}
    }
    
    # --- JUNIOR COLLEGE ELIGIBILITY CHECK ---
    jc_passed_rules = True
    jc_reasons = []

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

    if el_is_g3:
        if not check_g3_at_least(subject_grades["English Language"], "C6"):
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

    if jc_passed_rules: pathways["Junior College"]["open"] = True
    else: pathways["Junior College"]["reason"] = jc_reasons

    # Other pathways rules
    if g3_count >= 4: pathways["Polytechnic Year 1"]["open"] = True
    if total_g2_g3_count >= 5: pathways["Polytechnic Foundation Programme"]["open"] = True

    eligible_options = [name for name, info in pathways.items() if info["open"]]

    # --- 5. STEP 3: PATHWAY BUTTON SELECTION & CALCULATION ---
    st.write("---")
    st.write("### Step 3: Select an Eligible Pathway to Explore")
    
    if eligible_options:
        chosen_pathway = st.segmented_control(
            label="Select a pathway you are interested in learning:",
            options=eligible_options,
            key="selected_exploration_pathway"
        )
        
        # --- PATHWAY A: JUNIOR COLLEGE ---
        if chosen_pathway == "Junior College":
            st.success("🎉 You are exploring the **Junior College / Millennia Institute** pathway option.")
            
            # L1R4 CALCULATION ALGORITHM (STRICTLY G3 ONLY)
            g3_scores = {
                sub: g3_points[grade] 
                for sub, grade in subject_grades.items() 
                if subject_levels[sub] == "G3"
            }

            l1_candidates = {}
            if "English Language" in g3_scores:
                l1_candidates["English Language"] = g3_scores["English Language"]
            for hmt in hmt_subjects:
                if hmt in g3_scores:
                    l1_candidates[hmt] = g3_scores[hmt]
            
            if l1_candidates:
                l1_sub = min(l1_candidates, key=l1_candidates.get)
                l1_score = l1_candidates[l1_sub]
            else:
                l1_sub = "None Available"
                l1_score = 0
            
            remaining_pool = {sub: score for sub, score in g3_scores.items() if sub != l1_sub}
            
            if l1_sub in hmt_subjects:
                remaining_pool = {sub: score for sub, score in remaining_pool.items() if sub not in mt_subjects}

            r1_r2_pool = {sub: score for sub, score in remaining_pool.items() if sub in humanities_subjects or sub in math_science_subjects}
            sorted_r1_r2 = sorted(r1_r2_pool.items(), key=lambda x: x[1])
            
            r_subjects_chosen = []
            r_score_total = 0
            
            for sub, score in sorted_r1_r2[:2]:
                r_subjects_chosen.append((sub, score))
                r_score_total += score
                remaining_pool.pop(sub)

            sorted_r3_r4 = sorted(remaining_pool.items(), key=lambda x: x[1])
            for sub, score in sorted_r3_r4[:2]:
                r_subjects_chosen.append((sub, score))
                r_score_total += score

            l1r4_gross = l1_score + r_score_total
            
            st.markdown("### 📊 Your MOE L1R4 Aggregate Breakdown (G3 Subjects Only)")
            col_l1, col_r = st.columns(2)
            with col_l1:
                st.info(f"**L1 Subject (G3):**\n* {l1_sub} → **Grade {l1_score}**")
            with col_r:
                st.info(f"**Relevant R1–R4 Subjects (G3):**\n" + "\n".join([f"* {s} → **Grade {sc}**" for s, sc in r_subjects_chosen]))
            
            if len(r_subjects_chosen) < 4 or l1_score == 0:
                st.warning(f"⚠️ **Note:** You only have {len(r_subjects_chosen) + (1 if l1_score > 0 else 0)} eligible G3 subjects. A complete L1R4 calculation requires at least 5 G3 level subjects.")
            else:
                st.metric(label="Your Gross L1R4 Score", value=l1r4_gross)
                
        # --- PATHWAY B: POLYTECHNIC YEAR 1 ---
        elif chosen_pathway == "Polytechnic Year 1":
            st.success("🚀 You are exploring the **Polytechnic Year 1** pathway option.")
            st.info("The configuration setup for Polytechnic Year 1 has been initialized. Calculation logic will be added next.")

        # --- PATHWAY C: PFP ---
        elif chosen_pathway:
            st.info(f"You have selected **{chosen_pathway}**.")
    else:
        st.warning("You do not currently qualify for any educational pathways based on these grades.")
else:
    st.info("Please choose your subjects above to calculate your eligibility.")