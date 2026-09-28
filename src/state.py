import streamlit as st


def keep_valid(key, options):
    """Drop a stored selection that's no longer in the options.

    Happens when a filter removes the selected patient or a new file is loaded.
    Must be called before the widget with that key is created.
    """
    if key in st.session_state and st.session_state[key] not in options:
        del st.session_state[key]
