import streamlit as st

st.title("SEC 2027 Pathway Eligibility Checker")

# --- 1. DEFINE SYLLABUS CATEGORIES (Based on MOE JAE Guidelines) ---
humanities_subjects = [
    "Literature in English", "History", "Geography", 
    "Humanities (Social Studies, Geography)", "Humanities (Social Studies, History)", 
    "Humanities (Social Studies, Literature in English)", "Economics", "Drama",
    "Literature in Chinese", "Literature in Malay",
    "Humanities (Social Studies, Literature in Chinese)", 
    "Humanities (Social Studies, Literature in Malay)"
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
    "Exercise And Sports Science", "Business"
]

overlapping_subjects = [
    "English Language", "Mathematics", "Additional Mathematics", "Literature in English", 
    "History", "Geography", "Humanities (Social Studies, Geography)", 
    "Humanities (Social Studies, History)", "Humanities (Social Studies, Literature in English)", 
    "Humanities (Social Studies, Literature in Malay)", "Humanities (Social Studies, Literature in Chinese)",
    "Computing", "Science (Physics, Chemistry)", "Science (Physics, Biology)", 
    "Science (Chemistry, Biology)", "Nutrition and Food Science", "Art", 
    "Design & Technology", "Principles of Accounts"
] + mt_subjects

all_selectable_subjects = sorted(list(set(g3_only_subjects + overlapping_subjects)))

# Grade score mapping to integer points
g3_grades = ["A1", "A2", "B3", "B4", "C5", "C6", "D7", "E8", "9"]
g3_points = {"A1": 1, "A2": 2, "B3": 3, "B4": 4, "C5": 5, "C6": 6, "D7": 7, "E8": 8, "9": 9}
g2_grades = ["1", "2", "3", "4", "5", "6"]

# Strict MOE mapping from G3 grades to G2 equivalent values for B2 calculation
def map_g3_to_g2_points(g3_grade):
    if g3_grade in ["A1", "A2", "B3"]: return 1
    elif g3_grade in ["B4", "C5", "C6"]: return 2
    elif g3_grade == "D7": return 3
    elif g3_grade == "E8": return 4
    return 9 

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

            l1_r4_gross = l1_score + r_score_total
            
            st.markdown("### 📊 Your MOE L1R4 Aggregate Breakdown (G3 Subjects Only)")
            col_l1, col_r = st.columns(2)
            with col_l1:
                st.info(f"**L1 Subject (G3):**\n* {l1_sub} → **Grade {l1_score}**")
            with col_r:
                st.info(f"**Relevant R1–R4 Subjects (G3):**\n" + "\n".join([f"* {s} → **Grade {sc}**" for s, sc in r_subjects_chosen]))
            
            if len(r_subjects_chosen) < 4 or l1_score == 0:
                st.warning(f"⚠️ **Note:** You only have {len(r_subjects_chosen) + (1 if l1_score > 0 else 0)} eligible G3 subjects. A complete L1R4 calculation requires at least 5 G3 level subjects.")
            else:
                st.metric(label="Your Gross L1R4 Score", value=l1_r4_gross)
                
        # --- PATHWAY B: POLYTECHNIC YEAR 1 (ELR2B2 IMPLEMENTATION) ---
        elif chosen_pathway == "Polytechnic Year 1":
            st.success("🚀 You are exploring the **Polytechnic Year 1** pathway option.")
            
            elr2b2_type = st.selectbox(
                "Select your target course cluster (ELR2B2 Type):",
                options=[
                    "ELR2B2-A (Arts & Humanities)", 
                    "ELR2B2-B (Business)", 
                    "ELR2B2-C (ICT & Engineering)", 
                    "ELR2B2-D (Design & Media)"
                ]
            )
            
            g3_subs = {sub: grade for sub, grade in subject_grades.items() if subject_levels[sub] == "G3"}
            g2_subs = {sub: grade for sub, grade in subject_grades.items() if subject_levels[sub] == "G2"}
            
            if "English Language" not in g3_subs:
                st.error("❌ English Language must be taken at G3 level to compute an ELR2B2 score.")
            else:
                el_score = g3_points[g3_subs["English Language"]]
                
                # Setup G3 subject pools (G3 raw Grade 9 cannot be used)
                pool_g3 = {s: g3_points[g3_subs[s]] for s in g3_subs if s != "English Language" and g3_subs[s] != "9"}
                
                # Setup G2 subject pools (G2 Grades 5 and 6 cannot be used)
                pool_g2 = {s: int(g2_subs[s]) for s in g2_subs if g2_subs[s] not in ["5", "6"]}
                
                # Setup JAE subject categories
                g1_subjects = []
                g2_subjects = []

                if "ELR2B2-A" in elr2b2_type:
                    g1_subjects = humanities_subjects + ["Art", "Business", "Music", "Drama"]
                    g2_subjects = humanities_subjects + math_science_subjects + mt_subjects + hmt_subjects + ["Art", "Music", "Drama", "Business", "Design & Technology", "Nutrition and Food Science", "Principles of Accounts"]
                elif "ELR2B2-B" in elr2b2_type:
                    g1_subjects = ["Mathematics", "Additional Mathematics"]
                    g2_subjects = humanities_subjects + ["Art", "Business", "Music", "Drama", "Principles of Accounts"]
                elif "ELR2B2-C" in elr2b2_type:
                    g1_subjects = ["Mathematics", "Additional Mathematics"]
                    g2_subjects = ["Physics", "Chemistry", "Biology", "Science (Physics, Chemistry)", "Science (Physics, Biology)", "Science (Chemistry, Biology)", "Computing", "Electronics", "Biotechnology", "Design & Technology", "Nutrition and Food Science"]
                elif "ELR2B2-D" in elr2b2_type:
                    g1_subjects = ["Mathematics", "Additional Mathematics"]
                    g2_subjects = ["Art", "Higher Art", "Physics", "Chemistry", "Biology", "Science (Physics, Chemistry)", "Science (Physics, Biology)", "Science (Chemistry, Biology)", "Computing", "Electronics", "Biotechnology", "Design & Technology", "Nutrition and Food Science"]

                unmet_reasons = []
                r1_sub, r1_score = None, None
                r2_sub, r2_score = None, None
                b1_sub, b1_score = None, None
                b2_sub, b2_score = None, None
                b2_source_is_g2 = False

                # 1. Evaluate R1 (G3 level required)
                r1_eligible = {s: v for s, v in pool_g3.items() if s in g1_subjects}
                if not r1_eligible:
                    if g3_count == 4:
                        # Find if any of the user's Step 1 selections match the missing R1 criteria but are taken at G2
                        upgradeable_for_r1 = [s for s in selected_subjects if s in g1_subjects and subject_levels.get(s) == "G2"]
                        if upgradeable_for_r1:
                            subjects_str = ", ".join([f"**{s}**" for s in upgradeable_for_r1])
                            unmet_reasons.append(f"Missing an eligible G3 subject for **R1**. Based on your selected subjects, you need to change the level of {subjects_str} from G2 to **G3**.")
                        else:
                            unmet_reasons.append("Missing an eligible G3 subject from the **1st Group of Relevant Subjects (R1)**.")
                    else:
                        unmet_reasons.append("Missing an eligible G3 subject from the **1st Group of Relevant Subjects (R1)**.")
                else:
                    r1_sub = min(r1_eligible, key=r1_eligible.get)
                    r1_score = pool_g3.pop(r1_sub)
                
                # 2. Evaluate R2 (G3 level required)
                r2_eligible = {s: v for s, v in pool_g3.items() if s in g2_subjects}
                if not r2_eligible:
                    if g3_count == 4:
                        # Find if any of the user's Step 1 selections match the missing R2 criteria but are taken at G2
                        upgradeable_for_r2 = [s for s in selected_subjects if s in g2_subjects and subject_levels.get(s) == "G2"]
                        if upgradeable_for_r2:
                            subjects_str = ", ".join([f"**{s}**" for s in upgradeable_for_r2])
                            unmet_reasons.append(f"Missing an eligible G3 subject for **R2**. Based on your selected subjects, you need to change the level of {subjects_str} from G2 to **G3**.")
                        else:
                            unmet_reasons.append("Missing an eligible G3 subject from the **2nd Group of Relevant Subjects (R2)**.")
                    else:
                        unmet_reasons.append("Missing an eligible G3 subject from the **2nd Group of Relevant Subjects (R2)**.")
                else:
                    r2_sub = min(r2_eligible, key=r2_eligible.get)
                    r2_score = pool_g3.pop(r2_sub)

                # Mother Tongue exclusion logic
                hmt_used = (r1_sub in hmt_subjects) or (r2_sub in hmt_subjects) if (r1_sub or r2_sub) else False
                if hmt_used:
                    pool_g3 = {s: v for s, v in pool_g3.items() if s not in mt_subjects}
                    pool_g2 = {s: v for s, v in pool_g2.items() if s not in mt_subjects}
                
                # 3. Evaluate Best 1 (B1) (G3 level required)
                sorted_g3_rem = sorted(pool_g3.items(), key=lambda x: x[1])
                if len(sorted_g3_rem) < 1 and not unmet_reasons:
                    unmet_reasons.append("Insufficient remaining G3 subjects to satisfy the **Best 1 (B1)** requirement (must be a G3 subject).")
                elif len(sorted_g3_rem) >= 1:
                    b1_sub, b1_score = sorted_g3_rem[0]
                    pool_g3.pop(b1_sub)

                # 4. Evaluate Best 2 (B2)
                if not unmet_reasons:
                    # Scenario A: Student takes >= 5 G3 subjects (using the remaining pool_g3)
                    if g3_count >= 5:
                        if len(pool_g3) < 1:
                            unmet_reasons.append("Missing a 5th G3 subject to compute **Best 2 (B2)** via grade mapping.")
                        else:
                            b2_sub = min(pool_g3, key=pool_g3.get)
                            orig_g3_grade = g3_subs[b2_sub]
                            b2_score = map_g3_to_g2_points(orig_g3_grade)
                            b2_source_is_g2 = False

                    # Scenario B: Student takes exactly 4 G3 subjects with at least 1 G2 subject
                    elif g3_count == 4:
                        if len(pool_g2) < 1:
                            unmet_reasons.append("For students offering exactly 4 G3 subjects, you must provide at least 1 eligible G2 subject (grade 1 to 4) for **Best 2 (B2)**.")
                        else:
                            b2_sub = min(pool_g2, key=pool_g2.get)
                            b2_score = pool_g2[b2_sub]  
                            b2_source_is_g2 = True
                    else:
                        unmet_reasons.append("An ELR2B2 score requires a minimum of 4 G3 subjects (EL, R1, R2, B1) and either a 5th G3 subject (mapped) or a G2 subject (as is) for B2.")

                st.markdown(f"### 📊 Your {elr2b2_type.split(' ')[0]} Breakdown")
                
                if unmet_reasons:
                    st.error("❌ **Cannot Calculate ELR2B2 Score due to unmet criteria:**")
                    for reason in unmet_reasons:
                        st.markdown(f"* {reason}")
                else:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"**Core Language & Relevant Subjects:**\n* **EL:** English Language → **{el_score}**\n* **R1 (1st Group):** {r1_sub} → **{r1_score}**\n* **R2 (2nd Group):** {r2_sub} → **{r2_score}**")
                    with col2:
                        b2_label = f"**B2 (G2 Grade as is):** {b2_sub} → **{b2_score}**" if b2_source_is_g2 else f"**B2 (Mapped to G2):** {b2_sub} → **{b2_score}** *(Mapped from G3)*"
                        st.info(f"**Best Subjects Pool:**\n* **B1 (G3 Raw):** {b1_sub} → **{b1_score}**\n* {b2_label}")
                    
                    elr2b2_gross = el_score + r1_score + r2_score + b1_score + b2_score
                    st.metric(label="Calculated Gross ELR2B2 Score", value=elr2b2_gross)

        # --- PATHWAY C: PFP ---
        elif chosen_pathway:
            st.info(f"You have selected **{chosen_pathway}**.")
    else:
        st.warning("You do not currently qualify for any educational pathways based on these grades.")
else:
    st.info("Please choose your subjects above to calculate your eligibility.")