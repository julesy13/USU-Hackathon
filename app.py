"""
Supply Chain Visibility Application

Main entry point for the Streamlit application.
"""

import streamlit as st


def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="Supply Chain Visibility",
        page_icon="📦",
        layout="wide"
    )
    
    st.title("Supply Chain Visibility Dashboard")
    st.write("Welcome to the Supply Chain Visibility application")


if __name__ == "__main__":
    main()
