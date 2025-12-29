import streamlit as st
import video_finder as vf
import pandas as pd
import yaml

# Page Configuration
st.set_page_config(page_title="TubeScout", layout="wide", page_icon="📺")

# --- CSS STYLING ---
st.markdown("""
<style>
    /* --- Sidebar Typography --- */
    [data-testid="stSidebar"] {
        font-size: 20px !important;
    }
    [data-testid="stSidebar"] label {
        font-size: 20px !important;
    }
    [data-testid="stSidebar"] .stTextInput input {
        font-size: 18px !important;
    }
    [data-testid="stSidebar"] .stButton button {
        font-size: 20px !important;
    }
    
    /* --- Main Content Typography --- */
    .big-font {
        font-size: 22px !important;
        font-weight: 400;
        line-height: 1.6;
    }
    
    /* --- User Guide Typography --- */
    .guide-font {
        font-size: 18px !important;
    }
    .guide-font h3 {
        font-size: 24px !important;
        font-weight: 700 !important;
    }
    .guide-font li {
        margin-bottom: 10px;
    }

    /* --- Table/Dataframe Font Size --- */
    [data-testid="stDataFrame"] {
        font-size: 20px !important;
    }
    
    /* Header Sizing */
    h1, h2, h3 {
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
@st.dialog("📘 User Guide")
def show_user_guide():
    st.markdown("""
    <div class="guide-font">
        <h3>How to use TubeScout</h3>
        <ol>
            <li><strong>Get an API Key</strong>: You need a YouTube Data API v3 key from the <a href="https://console.developers.google.com/">Google Cloud Console</a>.</li>
            <li><strong>Enter Key</strong>: Paste it into the sidebar password field. If you have a default key configured, you can leave this blank.</li>
            <li><strong>Search</strong>: Enter topics like <code>Python, AI, Cooking</code>.</li>
            <li><strong>Adjust Period</strong>: Choose how far back to search (e.g., 7 days).</li>
            <li><strong>Analyze</strong>: 
               <ul>
                   <li><strong>Custom Score</strong>: Higher is better. It balances views, subscriber ratio, and recency.</li>
                   <li><strong>Ratio</strong>: High views with low subscribers = <strong>Hidden Gem</strong>.</li>
               </ul>
            </li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

st.title("📺 TubeScout")
st.markdown("""
<div class="big-font">
<strong>TubeScout</strong> helps you discover "hidden gems" on YouTube—videos with high engagement 
relative to their channel size—allowing you to find high-signal content independent of the standard algorithm.
</div>
""", unsafe_allow_html=True)

# Sidebar for Inputs
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key Input
    # Check for default key in config.yaml
    default_api_key = None
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
            if config:
                default_api_key = config.get('api_key')
    except (FileNotFoundError, yaml.YAMLError):
        pass
    
    api_key_input = st.text_input("Enter YouTube API Key", type="password", help="Leave blank to use default key if configured.")
    
    if not api_key_input and default_api_key:
        st.caption("✅ Using default API Key from config.yaml")
        api_key = default_api_key
    else:
        api_key = api_key_input
    
    st.divider()
    
    # Search Parameters
    search_query = st.text_input("Search Terms", placeholder="e.g., machine learning, python")
    
    search_period = st.slider("Search Period (Days)", min_value=1, max_value=365, value=7)
    
    col1, col2 = st.columns(2)
    with col1:
        submit_button = st.button("🔍 Find", type="primary", use_container_width=True)
    with col2:
        if st.button("📘 Guide", use_container_width=True):
            show_user_guide()

# Main Execution Logic
if submit_button:
    if not api_key:
        st.error("⚠️ Please enter a valid YouTube API Key in the sidebar.")
    elif not search_query:
        st.warning("⚠️ Please enter at least one search term.")
    else:
        # Parse search terms
        terms = [term.strip() for term in search_query.split(',') if term.strip()]
        start_date = vf.get_start_date_string(search_period)
        
        # Loading Effect
        results = None
        with st.status(f"Searching for {len(terms)} topics...", expanded=True) as status:
            try:
                status.write("Contacting YouTube API...")
                # Execute search
                results = vf.search_each_term(terms, api_key, start_date)
                status.update(label="Search Complete!", state="complete", expanded=False)
                
            except Exception as e:
                status.update(label="Error occurred", state="error")
                st.error(f"An error occurred: {e}")
                st.error("Please check your API Key and internet connection.")

        if results:
            # Configuration for clickable links
            column_config = {
                "Video URL": st.column_config.LinkColumn("Video URL", display_text="Watch Video"),
                "Channel URL": st.column_config.LinkColumn("Channel URL", display_text="Visit Channel"),
                "Custom_Score": st.column_config.NumberColumn("Score", format="%.2f"),
                "View-Subscriber Ratio": st.column_config.NumberColumn("Ratio", format="%.2f"),
            }

            # Display Overall Top Videos
            st.subheader("🏆 Top Videos Overall")
            if not results['top_videos'].empty:
                st.dataframe(results['top_videos'], use_container_width=True, column_config=column_config)
            else:
                st.info("No videos found matching the criteria.")

            # Display Individual Search Term Results
            if len(terms) > 1:
                st.divider()
                st.subheader("Results by Search Term")
                tabs = st.tabs(terms)
                for i, term in enumerate(terms):
                    with tabs[i]:
                        if term in results and not results[term].empty:
                            st.dataframe(results[term], use_container_width=True, column_config=column_config)
                        else:
                            st.write(f"No results for '{term}'")