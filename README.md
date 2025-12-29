# TubeScout

## About
**TubeScout** is a recommendation engine designed to help you escape the YouTube echo chamber.

The standard YouTube algorithm often prioritizes watch time, click-through rates, and established channels, creating a "rich get richer" feedback loop. This makes it difficult to find high-quality content from smaller creators.

**Why TubeScout is different:**
Instead of relying on opaque personalization, TubeScout identifies **"hidden gems"** by calculating a **View-to-Subscriber Ratio**. If a video has a high number of views relative to the channel's subscriber count, it indicates that the content is valuable enough to travel outside the channel's existing audience base organically.

This tool puts you back in control of your feed, allowing you to find high-signal content based on your specific interests, not what an algorithm thinks you want to watch.

## Features
- **Algorithm-Free Discovery**: Search based on keywords and recency, not watch history.
- **Custom Scoring**: Ranks videos using a weighted score of Views, Subscriber Ratio, and Recency.
- **Web Interface**: A user-friendly Streamlit web app with mobile support.
- **Command Line Interface**: For quick, scriptable searches.

## Installation & Local Build

If you want to run this application locally on your machine:

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/TubeScout.git
cd TubeScout
```

### 2. Install Dependencies
Ensure you have Python 3.9+ installed. Then run:
```bash
pip install -r requirements.txt
```

### YouTube-API-Key
You will need to acquire a YouTube v3 API key, which you can do so easily [here](https://console.developers.google.com/cloud-resource-manager). A helpful video outlining the process can be found [here](https://www.youtube.com/watch?v=-QMg39gK624).

Rename `config_template.yaml` to `config.yaml` and enter your API key there.

**Note:** `config.yaml` is ignored by git to prevent accidental sharing of your credentials.

## Usage

### Option 1: Streamlit Web App (Recommended)
For an interactive, visual interface:

```bash
streamlit run streamlit_app.py
```
This will open the app in your browser. You can enter your API key in the sidebar or let it load from `config.yaml`.

### Option 2: Command Line Interface (CLI)
For terminal-based usage:

```bash
python3 yt_search_engine.py 'search term 1' 'search term 2' --search-period 10
```
