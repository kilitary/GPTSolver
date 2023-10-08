from bs4 import BeautifulSoup
import json
import os
import numpy as np
import requests
import re
import urllib
from requests.models import MissingSchema
import spacy
import trafilatura
import time
import threading
import warnings
import binascii

warnings.filterwarnings("ignore", category=DeprecationWarning)  # %%

# %%
urls = []
done = []
done_urls = []


def beautifulsoup_extract_text_fallback(response_content):
    '''
    This is a fallback function, so that we can always return a value for text content.
    Even for when both Trafilatura and BeautifulSoup are unable to extract the text from a
    single URL.
    '''

    # Create the beautifulsoup object:
    soup = BeautifulSoup(response_content, 'html.parser')

    # Finding the text:
    elements = soup.find_all(text=True)

    # Remove unwanted tag elements:
    cleaned_text = ''
    blacklist = [
        '[document]',
        'noscript',
        'header',
        'html',
        'meta',
        'head',
        'input',
        'script',
        'style', ]

    # Then we will loop over every item in the extract text and make sure that the beautifulsoup4 tag
    # is NOT in the blacklist
    for item in elements:
        if item.parent.name not in blacklist:
            cleaned_text += '{} '.format(item)

    # Remove any tab separation and strip the text:
    cleaned_text = cleaned_text.replace('\t', '')
    return cleaned_text.strip()


def parse_page(link):
    # print(f'parse_page: {link}')
    # downloaded_url = trafilatura.fetch_url(link, no_ssl=True)
    # try:
    #     a = trafilatura.extract(downloaded_url, output_format='json', with_metadata=False, include_comments=False,
    #                             date_extraction_params={'extensive_search': True, 'original_date': True})
    # except AttributeError:
    #     a = trafilatura.extract(downloaded_url, output_format='json', with_metadata=False,
    #                             date_extraction_params={'extensive_search': True, 'original_date': True})
    # if a:
    #     json_output = json.loads(a)
    #     process_page(downloaded_url)
    #     return downloaded_url, json_output['text']
    # else:
    try:
        headers = {
            'Accept'                   : 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding'          : 'gzip, deflate',
            'Accept-Language'          : 'en',
            'Cache-Control'            : 'no-cache',
            'Connection'               : 'keep-alive',
            'Pragma'                   : 'no-cache',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent'               : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2041.18',

        }
        print(f'downloading {link} ... ', end='')
        r = requests.get(link, headers=headers)
        print(f'done')

        # We will only extract the text from successful requests:
        if r.status_code == 200:

            print(f'analyzing page ... ', end='')

            print(f'decode ', end='')
            decoded = r.content.decode('utf-8', errors='ignore')
            print(f'strip/split ', end='')
            pp = link.strip('/').split('/')
            print(f'cksum ', end='')
            c = binascii.crc32(r.content)
            # c = calculator.checksum(r.content)

            name = pp[-1]
            fname = f'data/{c:08x}-{name}'
            with open(fname, "wb") as file:
                file.write(r.content)
                print(f'written to {fname} OK')

            print(f'text ', end='')
            content = beautifulsoup_extract_text_fallback(r.content)

            print(f'links ', end='')
            process_page(r)

            print(f'done ')
            return decoded, content
        else:
            # This line will handle for any failures in both the Trafilature and BeautifulSoup4 functions:
            print(f'requests error: {r.status_code}/{r.reason}')

            return "", np.nan
    # Handling for any URLs that don't have the correct protocol
    except Exception as e:
        print(f'excepton: {e}')
        return "", np.nan


def process_page(response):
    all_relative = re.findall('href=(\'|")(.*?)(\'|")', response.content.decode('utf-8', errors='ignore'))
    for link in all_relative:
        if 'http' in link[1] or 'javascript' in link[1]:
            continue
        push_url('http://fsb.ru/' + link[1])
    all_abs = re.findall('href=(\'|")(http.*?)(\'|")', response.content.decode('utf-8', errors='ignore'))
    for link in all_abs:
        if 'http' not in link[1]:
            continue
        push_url(link[1])


def push_url(url):
    global urls, done_urls
    print(f'push: {url}')
    if url not in done_urls:
        print(f'[push_url/{threading.get_ident()}] get {url} ... [done: {len(done)}]')

        try:
            page, text = parse_page(url)
        except Exception as e:
            print(f'exception: {e}')
        else:
            print(f'size: {len(page)} bytes')
            time.sleep(3)

            done.append({'url': url, 'page': page, 'text': text})

        done_urls.append(url)
    else:
        print(f'already visited {url}')


single_url = 'http://fsb.ru/'
page, text = parse_page(single_url)

print(urls)

print(f'done {count(urls)}')
