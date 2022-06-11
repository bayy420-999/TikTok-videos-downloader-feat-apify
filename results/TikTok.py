import asyncio, aiohttp, aiofiles, requests, json, time, re
from os.path import abspath as abspath, join as join, exists as exists
from os import mkdir as mkdir
from apify_client import ApifyClient

def get_timestamp(epoch):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch))

async def get_json(url, session):
    async with session.get(url) as response:
        return await response.json()

async def tasker(urls, session):
    tasks = [get_json(url, session) for url in urls]
    return await asyncio.gather(*tasks)
    
async def make_session(urls):
    async with aiohttp.ClientSession() as session:
        return await tasker(urls, session)

async def download(results):
    status = []
    for result in results:
        filename = f'{result[0]} ({result[1]}).mp4'
        path = join(abspath('results'), result[0])

        if not exists(path):
            mkdir(path)

        if not exists(join(path, filename)):
            async with aiohttp.ClientSession() as session:
                async with session.get(result[2]) as response:
                    content = await response.content.read()

            async with aiofiles.open(join(path, filename), mode = 'wb') as outfile:
                await outfile.write(content)
        status.append(join(path, filename))
        return status
def get_vid_id(**kwargs):
    client = ApifyClient('apify_api_hOM38Vs0gzwaaPZAmV9NWwIby9YDT52IYbp1')
    run_input = {
        "resultsPerPage": kwargs.get('max_results'),
        "proxyConfiguration": {
            "useApifyProxy": True
            },
        "profiles": kwargs.get('profiles'),
        "hashtags": kwargs.get('hashtags'),
        "maxRequestRetries": 10,
        "maxConcurrency": 20,
        "commentsPerPost": 0
        }
    
    run = client.actor('sauermar/tiktok-scraper').call(run_input=run_input)
    return [f'https://api.tiktokv.com/aweme/v1/multi/aweme/detail/?aweme_ids=%5B{item["id"]}%5D' for item in client.dataset(run['defaultDatasetId']).iterate_items()]

def get_vid_details(json_responses):
    results = []
    for data in json_responses:
        if 'aweme_details' in data:
            results.append((data["aweme_details"][0]["author"]["nickname"],
            get_timestamp(data["aweme_details"][0]["create_time"]),
            data["aweme_details"][0]["video"]["play_addr"]["url_list"][0]))
    return results

def TikTok(**kwargs):
    urls = []
    pattern = r'video\/([0-9]+)\?'
    if kwargs.get('urls'):
        for raw_urls in kwargs.get('urls'):
            if 'vt.tiktok.com' in raw_urls:
                urls.append(f'https://api.tiktokv.com/aweme/v1/multi/aweme/detail/?aweme_ids=%5B{re.search(pattern, requests.get(raw_urls, allow_redirects = False).headers["Location"])[1]}%5D')
            else:
                urls.append(f'https://api.tiktokv.com/aweme/v1/multi/aweme/detail/?aweme_ids=%5B{re.search(pattern, raw_urls)[1]}%5D')
    else:
        profiles = kwargs.get('profiles') if kwargs.get('profiles') != None else []
        hashtags = kwargs.get('hashtags') if kwargs.get('hashtags') != None else []
        max_results = kwargs.get('max_results') if kwargs.get('max_results') != None and type(kwargs.get('max_results')) == int else 10000
        urls = get_vid_id(profiles = profiles, hashtags = hashtags, max_results = max_results)

    json_responses = asyncio.run(make_session(urls))
    vid_details = get_vid_details(json_responses)
    asyncio.run(download(vid_details))