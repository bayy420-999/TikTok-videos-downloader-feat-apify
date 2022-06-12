import json, time
from apify_tiktok_api import Apify_TikTok_API as api

def get_timestamp(epoch):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch))

def get_vid_id():
    profiles = input('Input profile username without @, if you want to input more than 1 username use " " (space) as separator: ').split()
    hashtags = input('Input hashtag without #, if you want to input more than 1 hashtag use " " (space) as separator: ').split()
    urls = input('Input video url, if you want to input more than 1 video url use " " (space) as separator: ').split()
    max_results = input('How much results you want to scrape/page: ')

    if type(max_results) == str:
        vid_ids = api(profiles, hashtags, urls)
    elif type(max_results) == int:
        vid_ids = api(profiles, hashtags, urls, max_results)
    else:
        print('Input correct answer!!!')
        return

    return [f'https://api.tiktokv.com/aweme/v1/multi/aweme/detail/?aweme_ids=%5B{vid_id}%5D' for vid_id in vid_ids]

def vid_details(json_responses):
    return [
        (
            data["aweme_details"][0]["author"]["nickname"],
            get_timestamp(data["aweme_details"][0]["create_time"]),
            data["aweme_details"][0]["video"]["play_addr"]["url_list"][0],
        )
        for data in json_responses
        if 'aweme_details' in data
    ]