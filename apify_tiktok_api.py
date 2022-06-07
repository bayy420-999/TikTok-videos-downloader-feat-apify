from apify_client import ApifyClient

def Apify_TikTok_API(profiles, hashtags, urls, max_results = 10000):
    client = ApifyClient(input('Input API_TOKEN from apify: '))
    
    run_input = {
        "resultsPerPage": max_results,
        "proxyConfiguration": {
            "useApifyProxy": True
            },
        "profiles": profiles,
        "hashtags": hashtags,
        "postURLs": urls,
        "maxRequestRetries": 10,
        "maxConcurrency": 20,
        "commentsPerPost": 0
        }
    
    run = client.actor('sauermar/tiktok-scraper').call(run_input=run_input)
    
    return [item['id'] for item in client.dataset(run['defaultDatasetId']).iterate_items()]