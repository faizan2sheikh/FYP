import streamlit as st
from streamlit_option_menu import option_menu

# Import your page functions
from page1 import page1
from page2 import page2

# Create a sidebar menu
with st.sidebar:
    selected = option_menu(
        "Inferface",
        ["Live Input", "Query"],
        icons=["camera", "search"],
        menu_icon="cast",
        default_index=0,
    )

# Display the selected page
if selected == "Live Input":
    page1()
elif selected == "Query":
    page2()
