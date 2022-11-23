import streamlit as st

st.set_page_config(
    page_title="NYT Project",
    page_icon="📰",
)

def _max_width_():
    max_width_str = "max-width: 1300px;"
    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )

_max_width_()

st.write("# NY Times Data Engineering Project")

st.sidebar.success("Select a page above.")

st.markdown(
    """
    This data engineering project aims at using the New York Times APIs to find data, transform and store it,
    and then display insights about the Covid-19 pandemic, and its coverage by the New York Times.

    This is the final project for the Data Engineering course at [Datascientest](https://datascientest.com/formation-data-engineer).
    ### Tech Stack
    - Python to query the APIs
    - MongoDB to store the articles data
    - PostgreSQL to store the covid cases and death cumulative data
    - Kafka and Spark Streaming for the real-time Wire API
    - Streamlit and Dash for the dashboards
    ### The Team
    - [Aysha Kadaikar](https://github.com/Aysha9)
    - [Guillaume Arp](https://github.com/GuillaumeArp)
    - [Vladimir Blokhin](https://github.com/vovk39)
"""
)
