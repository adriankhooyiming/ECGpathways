import streamlit as st

st.title("SEC Pathway Eligibility Checker")
st.write("For any feedback or questions, please email to adrian_khoo_yi_ming@moe.edu.sg")

# --- 1. DEFINE SYLLABUS CATEGORIES (Based on MOE Guidelines) ---
humanities_subjects = [
    "Literature in English", "History", "Geography", 
    "Humanities (Social Studies, Geography)", "Humanities (Social Studies, History)", 
    "Humanities (Social Studies, Literature in English)", "Economics", "Drama",
    "Literature in Chinese", "Literature in Malay",
    "Humanities (Social Studies, Literature in Chinese)", 
    "Humanities (Social Studies, Literature in Malay)"
]

# Individual and combined sciences
science_subjects = [
    "Physics", "Chemistry", "Biology",
    "Science (Physics, Chemistry)", "Science (Physics, Biology)", "Science (Chemistry, Biology)"
]

math_subjects = ["Mathematics", "Additional Mathematics"]

math_science_subjects = math_subjects + science_subjects + ["Computing", "Electronics", "Biotechnology"]

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
    "Computing", "Nutrition and Food Science", "Art", 
    "Design & Technology", "Principles of Accounts"
] + mt_subjects + science_subjects

all_selectable_subjects = sorted(list(set(g3_only_subjects + overlapping_subjects)))

# Grade score mapping to raw points
g3_grades = ["A1", "A2", "B3", "B4", "C5", "C6", "D7", "E8", "9"]
g3_points = {"A1": 1, "A2": 2, "B3": 3, "B4": 4, "C5": 5, "C6": 6, "D7": 7, "E8": 8, "9": 9}
g2_grades = ["1", "2", "3", "4", "5", "6"]

# --- MOE Mapping: G3 to G2 Equivalent Points ---
def map_to_g2_points(level, grade):
    if level == "G2":
        return int(grade)
    else: # G3 Level Mapping
        if grade in ["A1", "A2", "B3"]: return 1
        elif grade in ["B4", "C5", "C6"]: return 2
        elif grade == "D7": return 3
        elif grade == "E8": return 4
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
        "Junior College / MI": {"open": False, "reason": []},
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

    if jc_passed_rules: pathways["Junior College / MI"]["open"] = True
    else: pathways["Junior College / MI"]["reason"] = jc_reasons

    if g3_count >= 4: pathways["Polytechnic Year 1"]["open"] = True
    if total_g2_g3_count >= 5: pathways["Polytechnic Foundation Programme"]["open"] = True

    eligible_options = [name for name, info in pathways.items() if info["open"]]

    # --- 5. STEP 3: PATHWAY BUTTON SELECTION & CALCULATION ---
    st.write("---")
    st.write("### Step 3: Select an Eligible Pathway to Explore")
    
    if eligible_options:
        st.write("This is based on your current subject combination.")
        st.write("Your eligibility depends on the grade-specific requirements.")
        
        chosen_pathway = st.segmented_control(
            label="Select a pathway you are interested in learning:",
            options=eligible_options,
            label_visibility="collapsed",
            key="selected_exploration_pathway"
        )
        
        # --- PATHWAY A: JUNIOR COLLEGE / MILLENNIA INSTITUTE ---
        if chosen_pathway == "Junior College / MI":
            st.success("🎉 You are exploring the **Junior College / Millennia Institute** pathway option.")
            
            # Map G3 grades to numerical points
            g3_scores = {
                sub: g3_points[grade] 
                for sub, grade in subject_grades.items() 
                if subject_levels[sub] == "G3"
            }

            # Determine L1 Candidates (English or Higher Mother Tongues)
            l1_candidates = {}
            if "English Language" in g3_scores:
                l1_candidates["English Language"] = g3_scores["English Language"]
            for hmt in hmt_subjects:
                if hmt in g3_scores:
                    l1_candidates[hmt] = g3_scores[hmt]
            
            best_gross_l1r4 = float('inf')
            best_l1_sub = "None Available"
            best_r_subjects = []
            
            # Evaluate each valid L1 option to construct the best possible L1R4
            for l1_sub, l1_score in l1_candidates.items():
                # Establish the remaining subject pool
                pool = {sub: score for sub, score in g3_scores.items() if sub != l1_sub}
                
                # Apply Double Counting Guardrail: If Higher MTL is L1, standard Mother Tongue cannot be used
                if l1_sub in hmt_subjects:
                    pool = {sub: score for sub, score in pool.items() if sub not in mt_subjects}
                
                # R1: Any 1 best-scoring G3 subject from Humanities
                r1_candidates = {sub: score for sub, score in pool.items() if sub in humanities_subjects}
                if not r1_candidates:
                    continue  # Invalid combination
                r1_sub = min(r1_candidates, key=r1_candidates.get)
                r1_score = pool.pop(r1_sub)
                
                # R2: Any 1 best-scoring G3 subject from Mathematics or Science
                r2_candidates = {sub: score for sub, score in pool.items() if sub in math_science_subjects}
                if not r2_candidates:
                    continue  # Invalid combination
                r2_sub = min(r2_candidates, key=r2_candidates.get)
                r2_score = pool.pop(r2_sub)
                
                # R3: Any 1 best-scoring G3 subject from Humanities, Mathematics, or Science
                r3_candidates = {sub: score for sub, score in pool.items() if sub in humanities_subjects or sub in math_science_subjects}
                if not r3_candidates:
                    continue  # Invalid combination
                r3_sub = min(r3_candidates, key=r3_candidates.get)
                r3_score = pool.pop(r3_sub)
                
                # R4: Any 1 best-scoring remaining G3 subject
                if not pool:
                    continue  # Invalid combination (minimum of 5 subjects needed)
                r4_sub = min(pool, key=pool.get)
                r4_score = pool[r4_sub]
                
                total_gross = l1_score + r1_score + r2_score + r3_score + r4_score
                
                if total_gross < best_gross_l1r4:
                    best_gross_l1r4 = total_gross
                    best_l1_sub = l1_sub
                    best_r_subjects = [
                        (r1_sub, r1_score, "R1 (Humanities)"),
                        (r2_sub, r2_score, "R2 (Math/Science)"),
                        (r3_sub, r3_score, "R3 (Humanities/Math/Science)"),
                        (r4_sub, r4_score, "R4 (Other Best)")
                    ]

            st.markdown("### 📊 Your MOE L1R4 Aggregate Breakdown (G3 Subjects Only)")
            
            if best_gross_l1r4 == float('inf') or len(best_r_subjects) < 4:
                st.warning(f"⚠️ **Note:** You only have {len(g3_scores)} eligible G3 subjects. A complete L1R4 calculation requires at least 5 G3-level subjects containing the appropriate subject distributions (Humanities, Math, and Science).")
            else:
                col_l1, col_r = st.columns(2)
                with col_l1:
                    st.info(f"**L1 Subject (G3):**\n* {best_l1_sub} → **Grade {g3_scores[best_l1_sub]}**")
                with col_r:
                    # Formatted breakdown to match "Category: Subject -> Grade Score" structure
                    st.info(f"**Relevant R1–R4 Subjects (G3):**\n" + "\n".join([f"* {cat}: {s} → **Grade {sc}**" for s, sc, cat in best_r_subjects]))
                
                st.metric(label="Your Gross L1R4 Score", value=best_gross_l1r4)
                
                if best_gross_l1r4 <= 16:
                    st.success("✅ **Eligibility Status:** You are eligible for admission to **both** **Junior College (JC)** and **Millennia Institute (MI)**.")
                elif best_gross_l1r4 <= 20:
                    st.warning("⚠️ **Eligibility Status:** You are eligible for **Millennia Institute (MI)** admission only. (Your score exceeds 16, so you do not qualify for Junior College admission).")
                else:
                    st.error("❌ **Eligibility Status:** Your L1R4 aggregate score exceeds 20. You are **not eligible** for both Junior College and Millennia Institute admission.")
                
        # --- PATHWAY B: POLYTECHNIC YEAR 1 ---
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
                pool_g3 = {s: g3_points[g3_subs[s]] for s in g3_subs if s != "English Language" and g3_subs[s] != "9"}
                pool_g2 = {s: int(g2_subs[s]) for s in g2_subs if g2_subs[s] not in ["5", "6"]}
                
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
                    g2_subjects = science_subjects + ["Computing", "Electronics", "Biotechnology", "Design & Technology", "Nutrition and Food Science"]
                elif "ELR2B2-D" in elr2b2_type:
                    g1_subjects = ["Mathematics", "Additional Mathematics"]
                    g2_subjects = ["Art", "Higher Art"] + science_subjects + ["Computing", "Electronics", "Biotechnology", "Design & Technology", "Nutrition and Food Science"]

                unmet_reasons = []
                r1_sub, r1_score = None, None
                r2_sub, r2_score = None, None
                b1_sub, b1_score = None, None
                b2_sub, b2_score = None, None
                b2_source_is_g2 = False

                # 1. Evaluate R1
                r1_eligible = {s: v for s, v in pool_g3.items() if s in g1_subjects}
                if not r1_eligible:
                    unmet_reasons.append(f"Missing an eligible G3 subject from the **1st Group of Relevant Subjects (R1)** required for {elr2b2_type.split(' ')[0]}.")
                    offered_r1_candidates = [s for s in selected_subjects if s in g1_subjects]
                    if offered_r1_candidates:
                        unmet_reasons.append("The following candidate subjects were offered but failed because they are not at G3 level or lack a valid grade:")
                        for s in offered_r1_candidates:
                            lvl = subject_levels[s]
                            grd = subject_grades[s]
                            unmet_reasons.append(f"  * **{s}** (taken at **{lvl}** level with grade **{grd}**)")
                else:
                    r1_sub = min(r1_eligible, key=r1_eligible.get)
                    r1_score = pool_g3.pop(r1_sub)
                
                # 2. Evaluate R2
                r2_eligible = {s: v for s, v in pool_g3.items() if s in g2_subjects}
                if not r2_eligible:
                    unmet_reasons.append(f"Missing an eligible G3 subject from the **2nd Group of Relevant Subjects (R2)** required for {elr2b2_type.split(' ')[0]}.")
                    offered_r2_candidates = [s for s in selected_subjects if s in g2_subjects]
                    if offered_r2_candidates:
                        unmet_reasons.append("The following candidate subjects were offered but failed because they are not at G3 level or lack a valid grade:")
                        for s in offered_r2_candidates:
                            lvl = subject_levels[s]
                            grd = subject_grades[s]
                            unmet_reasons.append(f"  * **{s}** (taken at **{lvl}** level with grade **{grd}**)")
                else:
                    r2_sub = min(r2_eligible, key=r2_eligible.get)
                    r2_score = pool_g3.pop(r2_sub)

                hmt_used = (r1_sub in hmt_subjects) or (r2_sub in hmt_subjects) if (r1_sub or r2_sub) else False
                if hmt_used:
                    pool_g3 = {s: v for s, v in pool_g3.items() if s not in mt_subjects}
                    pool_g2 = {s: v for s, v in pool_g2.items() if s not in mt_subjects}
                
                # 3. Evaluate Best 1 (B1)
                sorted_g3_rem = sorted(pool_g3.items(), key=lambda x: x[1])
                if len(sorted_g3_rem) < 1 and not unmet_reasons:
                    unmet_reasons.append("Insufficient remaining G3 subjects to satisfy the **Best 1 (B1)** requirement.")
                elif len(sorted_g3_rem) >= 1:
                    b1_sub, b1_score = sorted_g3_rem[0]
                    pool_g3.pop(b1_sub)

                # 4. Evaluate Best 2 (B2)
                if not unmet_reasons:
                    if g3_count >= 5:
                        if len(pool_g3) < 1:
                            unmet_reasons.append("Missing a 5th G3 subject to compute **Best 2 (B2)** via grade mapping.")
                        else:
                            b2_sub = min(pool_g3, key=pool_g3.get)
                            orig_g3_grade = g3_subs[b2_sub]
                            b2_score = map_to_g2_points("G3", orig_g3_grade)
                            b2_source_is_g2 = False
                    elif g3_count == 4:
                        if len(pool_g2) < 1:
                            unmet_reasons.append("For students offering exactly 4 G3 subjects, you must provide at least 1 eligible G2 subject (Grade 1-4) for **Best 2 (B2)**.")
                            offered_g2_candidates = [s for s in selected_subjects if subject_levels[s] == "G2"]
                            if offered_g2_candidates:
                                unmet_reasons.append("The following G2 subjects were offered but their grades do not meet the minimum criteria (Grade 1-4):")
                                for s in offered_g2_candidates:
                                    unmet_reasons.append(f"  * **{s}** (Grade: **{subject_grades[s]}**)")
                        else:
                            b2_sub = min(pool_g2, key=pool_g2.get)
                            b2_score = pool_g2[b2_sub]  
                            b2_source_is_g2 = True

                st.markdown(f"### 📊 Your {elr2b2_type.split(' ')[0]} Breakdown")
                if unmet_reasons:
                    st.error("❌ **Cannot Calculate ELR2B2 Score due to unmet criteria:**")
                    for reason in unmet_reasons:
                        st.markdown(f"{reason}")
                else:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"**Core Language & Relevant Subjects:**\n* **EL:** English Language → **{el_score}**\n* **R1:** {r1_sub} → **{r1_score}**\n* **R2:** {r2_sub} → **{r2_score}**")
                    with col2:
                        b2_label = f"**B2 (G2 Grade as is):** {b2_sub} → **{b2_score}**" if b2_source_is_g2 else f"**B2 (Mapped to G2):** {b2_sub} → **{b2_score}** *(Mapped from G3)*"
                        st.info(f"**Best Subjects Pool:**\n* **B1 (G3 Raw):** {b1_sub} → **{b1_score}**\n* {b2_label}")
                    
                    elr2b2_gross = el_score + r1_score + r2_score + b1_score + b2_score
                    
                    if elr2b2_gross <= 22:
                        st.metric(label="Calculated Gross ELR2B2 Score", value=elr2b2_gross)
                        st.success("🎉 Your score meets the Polytechnic baseline entry requirement of ≤ 22 points!")
                    else:
                        st.metric(label="Calculated Gross ELR2B2 Score", value=elr2b2_gross)
                        st.error(f"❌ Gross aggregate score is {elr2b2_gross}, which exceeds the maximum allowable Polytechnic admission limit of 22. You are not eligible for this pathway.")

        # --- PATHWAY C: POLYTECHNIC FOUNDATION PROGRAMME (PFP ELMAB3 Detailed Validation) ---
        elif chosen_pathway == "Polytechnic Foundation Programme":
            st.success("🎓 You are exploring the **Polytechnic Foundation Programme (PFP)** pathway option.")
            
            pfp_cluster = st.segmented_control(
                label="Select your target PFP course track:",
                options=[
                    "Science, Design, Engineering and Technology Cluster", 
                    "Humanities, Art, Media and Business Cluster"
                ],
                key="selected_pfp_cluster"
            )
            
            if pfp_cluster:
                g2_equivalent_pool = {}
                for sub, grade in subject_grades.items():
                    level = subject_levels[sub]
                    if (level == "G3" and grade == "9") or (level == "G2" and grade in ["5", "6"]):
                        continue
                    g2_equivalent_pool[sub] = map_to_g2_points(level, grade)

                pfp_errors = []
                
                # Combined 'Science' and 'Design, Engineering and Technology' clusters logic
                if pfp_cluster == "Science, Design, Engineering and Technology Cluster":
                    relevant_subject_pool = ["Design & Technology", "Nutrition and Food Science"] + science_subjects
                else: 
                    relevant_subject_pool = [
                        "Art", "Geography", "History", 
                        "Humanities (Social Studies, Geography)", 
                        "Humanities (Social Studies, History)", 
                        "Humanities (Social Studies, Literature in English)", 
                        "Literature in English", "Principles of Accounts"
                    ]

                if "English Language" not in g2_equivalent_pool:
                    pfp_errors.append("English Language is missing or grade does not meet PFP parameters.")
                    el_val = None
                else:
                    el_val = g2_equivalent_pool.pop("English Language")
                    if el_val > 3:
                        pfp_errors.append(f"English Language G2-equivalent grade is {el_val} (Must be ≤ 3).")

                math_candidates = {s: g2_equivalent_pool[s] for s in math_subjects if s in g2_equivalent_pool}
                if not math_candidates:
                    pfp_errors.append("Mathematics or Additional Mathematics is missing or grade does not meet entry requirements.")
                    ma_sub, ma_val = None, None
                else:
                    ma_sub = min(math_candidates, key=math_candidates.get)
                    ma_val = g2_equivalent_pool.pop(ma_sub)
                    if ma_val > 3:
                        pfp_errors.append(f"{ma_sub} G2-equivalent grade is {ma_val} (Must be ≤ 3).")
                    
                    for s in list(math_candidates.keys()):
                        if s in g2_equivalent_pool: 
                            g2_equivalent_pool.pop(s)

                selected_relevant_subs = [s for s in subject_grades if s in relevant_subject_pool]
                available_relevant_subs = {
                    s: g2_equivalent_pool[s] 
                    for s in selected_relevant_subs 
                    if s in g2_equivalent_pool and g2_equivalent_pool[s] <= 3
                }
                
                if not selected_relevant_subs:
                    pfp_errors.append(f"You have not selected any relevant subjects required for the **{pfp_cluster}**.")
                    rel_sub, rel_val = None, None
                elif not available_relevant_subs:
                    pfp_errors.append(f"None of your selected relevant subjects for the **{pfp_cluster}** meet the minimum grade requirement of **3** or better:")
                    for s in selected_relevant_subs:
                        lvl = subject_levels[s]
                        grd = subject_grades[s]
                        equiv_val = map_to_g2_points(lvl, grd)
                        pfp_errors.append(f"  * **{s}** (taken at {lvl} level with grade **{grd}**) maps to a G2-equivalent grade of **{equiv_val}** (Must be ≤ 3).")
                    rel_sub, rel_val = None, None
                else:
                    rel_sub = min(available_relevant_subs, key=available_relevant_subs.get)
                    rel_val = g2_equivalent_pool.pop(rel_sub)

                hmt_present = [s for s in g2_equivalent_pool if s in hmt_subjects]
                if hmt_present:
                    best_hmt = min(hmt_present, key=lambda x: g2_equivalent_pool[x])
                    for s in list(g2_equivalent_pool.keys()):
                        if s in mt_subjects or (s in hmt_subjects and s != best_hmt):
                            g2_equivalent_pool.pop(s)

                sorted_remainder = sorted(g2_equivalent_pool.items(), key=lambda x: x[1])
                b_subjects = []
                
                for s, v in sorted_remainder[:2]:
                    if v > 4:
                        pfp_errors.append(f"Elective subject candidate '{s}' grade is {v} (Must be ≤ 4).")
                    b_subjects.append((s, v))

                if len(b_subjects) < 2 and not pfp_errors:
                    pfp_errors.append(f"Insufficient total subjects to complete the ELMAB3 structure (Offered {len(b_subjects) + 3} valid subjects, requires 5).")

                st.markdown(f"### 📊 PFP {pfp_cluster} ELMAB3 Breakdown")
                if pfp_errors:
                    st.error("❌ **Cannot calculate valid PFP profile due to the following criteria constraints:**")
                    for err in pfp_errors:
                        st.markdown(f"* {err}")
                else:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"**Core Components (Max Grade 3):**\n* **EL:** English Language $\\rightarrow$ **{el_val}**\n* **MA:** {ma_sub} $\\rightarrow$ **{ma_val}**\n* **Relevant Subject:** {rel_sub} $\\rightarrow$ **{rel_val}**")
                    with col2:
                        b_text = "\n".join([f"* **B{i+1}:** {s} $\\rightarrow$ **{v}**" for i, (s, v) in enumerate(b_subjects)])
                        st.info(f"**2 Best Remaining Subjects (Max Grade 4):**\n{b_text}")
                    
                    elmab3_gross = el_val + ma_val + rel_val + sum([v for _, v in b_subjects])
                    
                    if elmab3_gross <= 12:
                        st.metric(label="Your Gross ELMAB3 Score", value=elmab3_gross)
                        st.success("🎉 Your score meets the PFP baseline entry criteria of ≤ 12 points!")
                    else:
                        st.metric(label="Your Gross ELMAB3 Score", value=elmab3_gross)
                        st.error(f"❌ Gross aggregate score is {elmab3_gross}, which exceeds the maximum allowable PFP ceiling of 12.")

    else:
        st.warning("You do not currently qualify for any educational pathways based on these grades.")
else:
    st.info("Please choose your subjects above to calculate your eligibility.")