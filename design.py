import streamlit as st
import time

st.set_page_config(page_title='Epileptic seizures detector/predictor', page_icon='😊')
st.image(r'BioMedTechnionLogoEngColorW2-NEW.png', width=500)
st.title("Epileptic seizures detector/predictor")

#hide the menu button

st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

#condense the layout - remove the padding between components of website

padding = 0
st.markdown(f""" <style>
    .reportview-container .main .block-container{{
        padding-top: {padding}rem;
        padding-right: {padding}rem;
        padding-left: {padding}rem;
        padding-bottom: {padding}rem;
    }} </style> """, unsafe_allow_html=True)

# Using object notation
add_selectbox = st.sidebar.selectbox(
    "Who would you like to contact in case of an emergency?",
    ("Contact1", "Contact2", "Contact3")
)

col1, col2 = st.columns((4, 1))

col1.header("Live Data")
col1.image("eegsignals.png", width=400)

col2.header("Result")
col2.image("result.jpg", width=100)


# Using "with" notation
with st.sidebar:
    add_radio = st.radio(
        "are you wearing the deivce?",
        ("YES", "NO")
    )

    loading_placeholder = st.empty()

    with loading_placeholder:
        while True:
            with st.spinner("Calculating"):
                time.sleep(3)
                st.success("Ready")
                time.sleep(2)

