import asyncio, aiohttp, aiofiles, json
from utils import get_vid_id, vid_details
from os.path import abspath as abspath, join as join, exists as exists
from os import mkdir as mkdir
from time import perf_counter

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
    for result in results:
        filename = f'{result[0]} ({result[1]}).mp4'
        path = join(abspath('results'), result[0])

        if not exists(path):
            mkdir(path)

        if not exists(join(path, filename)):
            async with aiohttp.ClientSession() as session:
                async with session.get(result[2]) as response:
                    print(f'Getting {filename} content...')
                    content = await response.content.read()

            async with aiofiles.open(join(path, filename), mode = 'wb') as outfile:
                await outfile.write(content)
                print(f'{filename} successfully downloaded...')

if __name__ == '__main__':
    while True:
        start = perf_counter()
        
        urls = get_vid_id()
        json_responses = asyncio.run(make_session(urls))
        asyncio.run(download(vid_details(json_responses)))
        
        end = perf_counter()
        print(f'Total time consumed: {end - start}')

        if ['no', 'No', 'NO'] in input('Do you want to use this program again? (Y/n): '):
            exit()