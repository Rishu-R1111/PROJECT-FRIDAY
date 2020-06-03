import urllib3
import urllib2
import urllib
import re
import requests
from bs4 import BeautifulSoup
urllib3.disable_warnings()
USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}


def fetch_results(search_term):
    assert isinstance(search_term, str), 'Search term must be a string'
    escaped_search_term = search_term.replace(' ', '+')
    print (escaped_search_term)

    google_url = 'https://www.google.com'
    response = requests.get(google_url, headers=USER_AGENT)
    response.raise_for_status()
    return response.text


def parse_results(html):
        soup = BeautifulSoup(html, 'html.parser')

        result_block = soup.find_all('a', attrs={'class': 'gb_P'})
        find_me = soup.find_all('li')
        print(find_me)
        if len(result_block) > 0:
            print (len(result_block))
            for er in range(0, len(result_block)):
                name_is = result_block[er].text
                print(name_is)


if __name__ == '__main__':

    html = fetch_results('')
    parse_results(html) 
