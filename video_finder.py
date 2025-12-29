
# Load dependencies
import pandas as pd
from datetime import datetime, timedelta
from apiclient.discovery import build

def get_start_date_string(search_period_days):
    """Returns string for date at start of search period."""
    search_start_date = datetime.today() - timedelta(search_period_days)
    date_string = datetime(year=search_start_date.year,month=search_start_date.month,
                           day=search_start_date.day).strftime('%Y-%m-%dT%H:%M:%SZ')
    return date_string


def search_each_term(search_terms, api_key, uploaded_since,
                        views_threshold=5000, num_to_print=5):
    """Uses search term list to execute API calls and print results."""
    if type(search_terms) == str:
        search_terms = [search_terms]

    list_of_dfs = []
    for index, search_term in enumerate(search_terms):
        df = find_videos(search_terms[index], api_key, views_threshold=views_threshold,
                         uploaded_since = uploaded_since)
        df = df.sort_values(['Custom_Score'], ascending=[0])
        list_of_dfs.append(df)

    # 1 - concatenate them all
    full_df = pd.concat((list_of_dfs),axis=0)
    full_df = full_df.sort_values(['Custom_Score'], ascending=[0])
    print("THE TOP VIDEOS OVERALL ARE:")
    print_top_videos(full_df, num_to_print)
    print("==========================\n")

    # 2 - in total
    for index, search_term in enumerate(search_terms):
        results_df = list_of_dfs[index]
        print("THE TOP VIDEOS FOR SEARCH TERM '{}':".format(search_terms[index]))
        print_top_videos(results_df, num_to_print)

    results_df_dict = dict(zip(search_terms, list_of_dfs))
    results_df_dict['top_videos'] = full_df

    return results_df_dict


def find_videos(search_terms, api_key, views_threshold, uploaded_since):
    """Calls other functions (below) to find results and populate dataframe."""

    # Initialise results dataframe
    dataframe = pd.DataFrame(columns=('Title', 'Video URL', 'Custom_Score',
                            'Views', 'Channel Name','Num_subscribers',
                            'View-Subscriber Ratio','Channel URL'))

    # Run search
    search_results, youtube_api = search_api(search_terms, api_key,
                                                        uploaded_since)

    results_df = populate_dataframe(search_results, youtube_api, dataframe,
                                                        views_threshold)

    return results_df


def search_api(search_terms, api_key, uploaded_since):
    """Executes search through API and returns result."""

    # Initialise API call
    youtube_api = build('youtube', 'v3', developerKey = api_key)

    #Make the search
    results = youtube_api.search().list(q=search_terms, part='snippet',
                                type='video', order='viewCount', maxResults=50,
                                publishedAfter=uploaded_since).execute()

    return results, youtube_api


def populate_dataframe(results, youtube_api, df, views_threshold):
    """Extracts relevant information and puts into dataframe"""
    # Extract IDs to query in batch
    video_ids = [item['id']['videoId'] for item in results['items']]
    
    if not video_ids:
        return df

    # Batch 1: Get Video Statistics and Details
    video_response = youtube_api.videos().list(
        id=','.join(video_ids),
        part='snippet,statistics'
    ).execute()
    
    # Create a map for video details
    videos_map = {v['id']: v for v in video_response['items']}

    # Batch 2: Get Channel Statistics
    channel_ids = list({v['snippet']['channelId'] for v in video_response['items']})
    channel_response = youtube_api.channels().list(
        id=','.join(channel_ids),
        part='snippet,statistics'
    ).execute()

    # Create a map for channel details
    channels_map = {c['id']: c for c in channel_response['items']}

    data_list = []

    for item in results['items']:
        video_id = item['id']['videoId']
        video_data = videos_map.get(video_id)
        
        if not video_data:
            continue

        viewcount = int(video_data['statistics'].get('viewCount', 0))
        
        if viewcount > views_threshold:
            title = video_data['snippet']['title']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            channel_id = video_data['snippet']['channelId']
            channel_data = channels_map.get(channel_id)
            channel_url = f"https://www.youtube.com/channel/{channel_id}"
            
            if channel_data:
                channel_name = channel_data['snippet']['title']
                if channel_data['statistics'].get('hiddenSubscriberCount'):
                    num_subs = 1000000
                else:
                    num_subs = int(channel_data['statistics']['subscriberCount'])
            else:
                channel_name = "Unknown"
                num_subs = 0

            ratio = view_to_sub_ratio(viewcount, num_subs)
            days_since_published = how_old(video_data)
            score = custom_score(viewcount, ratio, days_since_published)
            
            data_list.append({
                'Title': title, 
                'Video URL': video_url, 
                'Custom_Score': score,
                'Views': viewcount, 
                'Channel Name': channel_name,
                'Num_subscribers': num_subs, 
                'View-Subscriber Ratio': ratio, 
                'Channel URL': channel_url
            })

    if data_list:
        return pd.DataFrame(data_list)
    else:
        return df


def print_top_videos(df, num_to_print):
    """Prints top videos to console, with details and link to video."""
    if len(df) < num_to_print:
        num_to_print = len(df)
    if num_to_print == 0:
        print("No video results found")
    else:
        for i in range(num_to_print):
            video = df.iloc[i]
            title = video['Title']
            views = video['Views']
            subs = video['Num_subscribers']
            link = video['Video URL']
            print("Video #{}:\nThe video '{}' has {} views, from a channel \
with {} subscribers and can be viewed here: {}\n"\
                                        .format(i+1, title, views, subs, link))
            print("==========================\n")


## ======================================================================= ##
## ====== SERIES OF FUNCTIONS TO PARSE KEY INFORMATION ABOUT VIDEOS ====== ##
## ======================================================================= ##


def view_to_sub_ratio(viewcount, num_subscribers):
    if num_subscribers == 0:
        return 0
    else:
        ratio = viewcount / num_subscribers
        return ratio

def how_old(item):
    when_published = item['snippet']['publishedAt']
    when_published_datetime_object = datetime.strptime(when_published,
                                                        '%Y-%m-%dT%H:%M:%SZ')
    today_date = datetime.today()
    days_since_published = int((today_date - when_published_datetime_object).days)
    if days_since_published == 0:
        days_since_published = 1
    return days_since_published

def custom_score(viewcount, ratio, days_since_published):
    ratio = min(ratio, 5)
    score = (viewcount * ratio) / days_since_published
    return score
