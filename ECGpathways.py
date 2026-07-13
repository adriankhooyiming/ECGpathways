import streamlit as st

st.title("SEC 2027 Pathway Eligibility Checker")

# --- 1. DEFINE SYLLABUS LISTS (Based on SEAB 2027 Guidelines) ---
# Subjects available only at G3 level
g3_only_subjects = [
    "Arabic as a 3rd Language", "Bahasa Indonesia as a 3rd Language", "Economics", 
    "Drama", "Spanish", "French", "German", "Japanese", "Physics", "Chemistry", 
    "Biology", "Electronics", "Music", "Higher Music", "Higher Art", "Biotechnology", 
    "Design Studies", "Higher Chinese", "Chinese (Special Programme)", "Literature in Chinese",
    "Higher Malay", "Malay (Special Programme)", "Literature in Malay", "Higher Tamil", 
    "Literature in Tamil", "Exercise And Sports Science"
]

# Subjects available at both G3 and G2 levels
overlapping_subjects = [
    "English Language", "Mathematics", "Additional Mathematics", "Literature in English", 
    "History", "Geography", "Humanities (Social Studies, Geography)", 
    "Humanities (Social Studies, History)", "Humanities (Social Studies, Literature in English)", 
    "Computing", "Science (Physics, Chemistry)", "Science (Physics, Biology)", 
    "Science (Chemistry, Biology)", "Nutrition and Food Science", "Art", 
    "Design & Technology", "Principles of Accounts", "Chinese Language", 
    "Malay Language", "Tamil Language", "Bengali", "Gujarati", "Hindi", "Panjabi", "Urdu"
]

# Combine lists alphabetically for the dropdown selection
all_selectable_subjects = sorted(g3_only_subjects + overlapping_subjects)

# --- 2. STEP 1: SUBJECT ENTRY VIA DROPDOWN ---
st.write("### Step 1: Select Your Subjects")
selected_subjects = st.multiselect(
    "Choose all the subjects you are currently taking:",
    options=all_selectable_subjects
)

# A dictionary to log the final level (G2 or G3) of each chosen subject
subject_levels = {}

# --- 3. STEP 2: LEVEL RESOLUTION (EITHER / OR) ---
if selected_subjects:
    st.write("---")
    st.write("### Step 2: Assign Subject Levels")
    st.info("For subjects offered at both levels, please select either G3 or G2.")
    
    # Generate toggles dynamically for each selected subject
    for subject in selected_subjects:
        if subject in overlapping_subjects:
            # Render a single-choice radio layout (Either/Or button layout)
            chosen_level = st.radio(
                label=f"Level for **{subject}**:",
                options=["G3", "G2"],
                horizontal=True,
                key=f"level_{subject}"
            )
            subject_levels[subject] = chosen_level
        else:
            # Automatically assign G3 if it's a G3-only subject
            st.markdown(f"📖 **{subject}** is uniquely a **G3** level subject.")
            subject_levels[subject] = "G3"

    # --- 4. STEP 3: DYNAMIC COUNTING & EVALUATION ---
    st.write("---")
    
    # Tally up the final counts dynamically
    g3_count = sum(1 for lvl in subject_levels.values() if lvl == "G3")
    g2_count = sum(1 for lvl in subject_levels.values() if lvl == "G2")
    
    # Display the current counts to the user
    st.metric(label="Total G3 Subjects", value=g3_count)
    st.metric(label="Total G2 Subjects", value=g2_count)
    
    # Pathway Logic Evaluation
    jc_open = False
    poly_y1_open = False
    pfp_open = False
    
    # Condition 1: 5 or more G3 subjects
    if g3_count >= 5:
        jc_open = True
        poly_y1_open = True
        pfp_open = True
        
    # Condition 2: Exactly 4 G3 subjects AND at least 1 G2 subject
    elif g3_count == 4 and g2_count >= 1:
        poly_y1_open = True
        pfp_open = True
        
    # Condition 3: 3 or fewer G3 subjects AND at least 5 G2 subjects
    elif g3_count <= 3 and g2_count >= 5:
        pfp_open = True

    # Render results
    st.write("### Eligible Pathways")
    available_pathways = []
    if jc_open:
        available_pathways.append("Junior College")
    if poly_y1_open:
        available_pathways.append("Polytechnic Year 1")
    if pfp_open:
        available_pathways.append("Polytechnic Foundation Programme")
        
    if available_pathways:
        for pathway in available_pathways:
            st.success(f"✅ **{pathway}** is open to you.")
    else:
        st.warning("Based on the current subject counts, no specific pathways are open.")
else:
    st.info("Please choose your subjects above to calculate your eligibility.")