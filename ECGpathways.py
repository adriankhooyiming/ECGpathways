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

# --- 2. STEP 1: SUBJECT ENTRY ---
st.write("### Step 1: Select Your Subjects")
selected_subjects = st.multiselect(
    "Choose all the subjects you are currently taking:",
    options=all_selectable_subjects
)

subject_levels = {}

# --- 3. STEP 2: PILL-BUTTON LEVEL RESOLUTION ---
if selected_subjects:
    st.write("---")
    st.write("### Step 2: Assign Subject Levels")
    
    # Custom CSS to mimic the light card layout borders seen in your image
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
    """, unsafe_unsafe_with_style=True)

    for subject in selected_subjects:
        # Create a container row to separate each subject clearly
        with st.container():
            # Create a 2-column layout (Left for text, Right for the buttons)
            col1, col2 = st.columns([2, 1], vertical_alignment="center")
            
            with col1:
                st.markdown(f"**{subject}**")
                
            with col2:
                if subject in overlapping_subjects:
                    # Renders as selectable side-by-side pill buttons
                    chosen_level = st.segmented_control(
                        label=f"Level for {subject}",
                        options=["G2", "G3"],
                        default="G3",
                        label_visibility="collapsed", # Hides label to match your image format
                        key=f"level_{subject}"
                    )
                    subject_levels[subject] = chosen_level if chosen_level else "G3"
                else:
                    # For G3-only subjects, render a disabled single pill block
                    st.segmented_control(
                        label=f"Level for {subject}",
                        options=["G3"],
                        default="G3",
                        disabled=True,
                        label_visibility="collapsed",
                        key=f"level_{subject}"
                    )
                    subject_levels[subject] = "G3"

    # --- 4. STEP 3: DYNAMIC COUNTING & EVALUATION ---
    st.write("---")
    
    g3_count = sum(1 for lvl in subject_levels.values() if lvl == "G3")
    g2_count = sum(1 for lvl in subject_levels.values() if lvl == "G2")
    
    st.metric(label="Total G3 Subjects", value=g3_count)
    st.metric(label="Total G2 Subjects", value=g2_count)
    
    jc_open = False
    poly_y1_open = False
    pfp_open = False
    
    if g3_count >= 5:
        jc_open = True
        poly_y1_open = True
        pfp_open = True
    elif g3_count == 4 and g2_count >= 1:
        poly_y1_open = True
        pfp_open = True
    elif g3_count <= 3 and g2_count >= 5:
        pfp_open = True

    st.write("### Eligible Pathways")
    available_pathways = []
    if jc_open: available_pathways.append("Junior College")
    if poly_y1_open: available_pathways.append("Polytechnic Year 1")
    if pfp_open: available_pathways.append("Polytechnic Foundation Programme")
        
    if available_pathways:
        for pathway in available_pathways:
            st.success(f"✅ **{pathway}** is open to you.")
    else:
        st.warning("Based on the current subject counts, no specific pathways are open.")
else:
    st.info("Please choose your subjects above to calculate your eligibility.")