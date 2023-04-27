import os
import requests
import time
import pandas as pd
from collections import defaultdict


API_KEY = os.getenv('MAL_API_KEY')
if not API_KEY:
    raise ValueError('MAL_API_KEY environment variable must be set')
SEASONAL_URL = 'https://api.myanimelist.net/v2/anime/season/{year}/{season}'
ID_URL = 'https://api.myanimelist.net/v2/anime/{id}'
HEADERS = {
    'X-MAL-CLIENT-ID': API_KEY,
    'Content-Type': 'application/json'
}
START_YEAR = 1990
STOP_YEAR = 2022


def get_anime(year):
    anime_data = []
    for season in ['winter', 'spring', 'summer', 'fall']:
        page = 1
        while True:
            response = get_seasonal_anime(year, season, page)
            if not response or not response['data']:
                break

            for entry in response['data']:
                node = entry['node']
                # some MAL entries lack a source, so we'll just set it to unknown
                source = node.get('source', 'unknown')
                anime_data.append({
                    'title': node['title'],
                    'year': year,
                    'source': source,
                    'season': season,
                })
            
            page += 1
            # wait a quarter of a second to avoid rate limiting
            time.sleep(0.25)
    return anime_data

def get_seasonal_anime(year, season, page=1):
    params = {
        'limit': 100,
        'offset': (page - 1) * 100,
        'fields': 'title,year,source'
    }

    formatted_url = SEASONAL_URL.format(year=year, season=season)
    response = requests.get(formatted_url, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error getting anime for {season} {year}, page {page}: {response.status_code}')
        return None


def count_light_novel_sources(anime_data):
    source_counts = defaultdict(int)
    anime_counts = defaultdict(int)
    
    for anime in anime_data:
        if anime['source'] == 'light_novel':
            source_counts[anime['year']] += 1
        anime_counts[anime['year']] += 1
    
    return [{'year': year, 'light_novel_count': count, 'total_anime_count': anime_counts[year]} for year, count in source_counts.items()]


def main():
    anime_data = []

    for year in range(START_YEAR, STOP_YEAR + 1):
        anime_data += get_anime(year)
        if year % 5 == 0:
            print(f'Collected anime data through {year} ({len(anime_data)} anime total)')

    anime_df = pd.DataFrame(anime_data)
    anime_df.to_csv('anime_data.csv', index=False)
    print('Anime data saved to anime_data.csv')

    light_novel_counts = count_light_novel_sources(anime_data)
    light_novel_counts_df = pd.DataFrame(light_novel_counts)
    light_novel_counts_df['light_novel_percentage'] = (light_novel_counts_df['light_novel_count'] / light_novel_counts_df['total_anime_count']) * 100
    light_novel_counts_df.drop(columns='total_anime_count', inplace=True)
    light_novel_counts_df.to_csv('light_novel_counts.csv', index=False)
    print('Light novel counts with percentages saved to light_novel_counts.csv')


if __name__ == '__main__':
    main()
