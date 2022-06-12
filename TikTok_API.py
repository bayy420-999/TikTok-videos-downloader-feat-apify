import asyncio, aiohttp, aiofiles, requests, json, time, re, os
from apify_client import ApifyClient

class TikTok:
    def __init__(self, **kwargs):
        self.urls = kwargs.get('urls')
        self.profiles = kwargs.get('profiles')
        self.hashtags = kwargs.get('hashtags')
        self.max_results = kwargs.get('max_results')
        
    def get_timestamp(self, epoch):
        return time.strftime('%Y-%m-%d %H:%M:%S',
                              time.localtime(epoch))

    def get_tiktok_urls(self, profiles, hashtags, max_results):
        client = ApifyClient('apify_api_hOM38Vs0gzwaaPZAmV9NWwIby9YDT52IYbp1')
 
        run_input = {
            "resultsPerPage": max_results,
            "proxyConfiguration": {
                "useApifyProxy": True
                },
            "profiles": profiles,
            "hashtags": hashtags,
            "maxRequestRetries": 10,
            "maxConcurrency": 20,
            "commentsPerPost": 0
            }
        
        run = client.actor('sauermar/tiktok-scraper').call(run_input=run_input)
        return [f'https://api.tiktokv.com/aweme/v1/multi/aweme/detail/?aweme_ids=%5B{item["id"]}%5D'
                for item in client.dataset(run['defaultDatasetId']).iterate_items()]


    def get_video_details(self, json_responses):
        return [(data["aweme_details"][0]["author"]["nickname"],
                self.get_timestamp(data["aweme_details"][0]["create_time"]),
                data["aweme_details"][0]["video"]["play_addr"]["url_list"][0])
                for data in json_responses if 'aweme_details' in data]

    async def get_json(self, url, session):
        async with session.get(url) as response:
            return await response.json()
    
    async def tasker(self, urls, session):
        tasks = [self.get_json(url, session) for url in urls]
        return await asyncio.gather(*tasks)
        
    async def make_session(self, urls):
        async with aiohttp.ClientSession() as session:
            return await self.tasker(urls, session)

    async def download(self, results):
        list_of_fullpath = []
        for result in results:
            filename = f'{result[0]} ({result[1]}).mp4'
            path = os.path.join(os.path.abspath('results'), result[0])
            fullpath = os.path.join(path, filename)
            list_of_fullpath.append(fullpath)
            
            if not os.path.exists(path):
                os.mkdir(path)
    
            if not os.path.exists(fullpath):
                async with aiohttp.ClientSession() as session:
                    async with session.get(result[2]) as response:
                        content = await response.content.read()
    
                async with aiofiles.open(fullpath, mode = 'wb') as outfile:
                    await outfile.write(content)
        return list_of_fullpath

    def url_download(self, urls):
        new_urls = []
        pattern = r'video\/([0-9]+)\?'
        for url in urls:
            if 'vt.tiktok.com' in url:
                vid_id = re.search(pattern, requests.get(url, allow_redirects = False).headers['Location'])[1]
            else:
                vid_id = re.search(pattern, url)[1]
            new_urls.append(f'https://api.tiktokv.com/aweme/v1/multi/aweme/detail/?aweme_ids=%5B{vid_id}%5D')
        
        json_responses = asyncio.run(self.make_session(new_urls))
        video_details = self.get_video_details(json_responses)
        return asyncio.run(self.download(video_details))

    def bulk_download(self, profiles = [], hashtags = [], max_results = None):
        urls = self.get_tiktok_urls(profiles, hashtags, max_results)
        json_responses = asyncio.run(self.make_session(urls))
        video_details = self.get_video_details(json_responses)
        return asyncio.run(self.download(video_details))