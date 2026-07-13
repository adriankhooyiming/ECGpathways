import streamlit as st

st.title("Pathway Eligibility Checker")

# 1. Inputs: G3 and G2 subject counts
with st.form("subject_form"):
    st.write("### Select Number of Subjects")
    
    g3_subjects = st.number_input(
        label="Number of G3 Subjects",
        min_value=0,
        max_value=7,
        value=0,
        step=1
    )
    
    g2_subjects = st.number_input(
        label="Number of G2 Subjects",
        min_value=0,
        max_value=7,
        value=0,
        step=1
    )
    
    submit_btn = st.form_submit_button("Check Eligible Pathways")

# 2. Logic & Conditional Evaluation
if submit_btn:
    # Initialize all options as locked/closed
    jc_open = False
    poly_y1_open = False
    pfp_open = False
    
    # Rule 1: 5 or more G3 subjects
    if g3_subjects >= 5:
        jc_open = True
        poly_y1_open = True
        pfp_open = True
        
    # Rule 2: Exactly 4 G3 subjects AND at least 1 G2 subject
    elif g3_subjects == 4 and g2_subjects >= 1:
        poly_y1_open = True
        pfp_open = True
        
    # Rule 3: 3 or fewer G3 subjects AND at least 5 G2 subjects
    elif g3_subjects <= 3 and g2_subjects >= 5:
        pfp_open = True

    # 3. Displaying the results to the user
    st.write("---")
    st.write("### Available Options:")
    
    # Collect open pathways into a list
    available_pathways = []
    if jc_open:
        available_pathways.append("Junior College")
    if poly_y1_open:
        available_pathways.append("Polytechnic Year 1")
    if pfp_open:
        available_pathways.append("Polytechnic Foundation Programme")
        
    # Display results or a fallback message if no pathways open
    if available_pathways:
        for pathway in available_pathways:
            st.success(f"✅ **{pathway}** is open.")
    else:
        st.warning("Based on the current subject counts, no specific pathways are open.")