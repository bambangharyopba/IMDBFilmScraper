import requests
from bs4 import BeautifulSoup
from queue import Queue
import re
import time
import sys

def getFilm(link):
    title = ''
    rate = ''
    bestrate = ''
    ratingCount = ''
    userReview = ''
    criticReview= ''
    time = ''
    genre = ''
    releasedate = ''
    link = link

    response_film = requests.get(link)
    page = BeautifulSoup(response_film.text, 'html.parser')
    titlebar = page.find('div', class_ = 'title_block')
    if titlebar != None:
        title = titlebar.find('div', class_ = 'title_wrapper').h1
        if title != None:
            title = title.text.strip()
        rate = titlebar.find('span', itemprop = 'ratingValue')
        if rate != None:
            rate = rate.text
        bestrate = titlebar.find('span', itemprop = 'bestRating')
        if bestrate != None:
            bestrate = bestrate.text
        ratingCount = titlebar.find('span', itemprop = 'ratingCount')
        if ratingCount != None:
            ratingCount = ratingCount.text
        reviewCount = titlebar.find_all('span', itemprop = 'reviewCount')
        if reviewCount != []:
            userReview = reviewCount[0].text
            criticReview = reviewCount[1].text
        subtext = titlebar.find('div', class_ = 'subtext')
        if subtext != None:
            subtext = subtext.text.split('|')
            subtext = [text.replace('\n','').strip() for text in subtext]
            if len(subtext) < 3:
                genre = subtext[0]
                releasedate = subtext[1]
            elif len(subtext) > 3:
                time = subtext[1]
                genre = subtext[2]
                releasedate = subtext[3]
            else:
                time = subtext[0]
                genre = subtext[1]
                releasedate = subtext[2]
        
        film = {'title' : title,
                'rate' : rate,
                'bestrate' : bestrate,
                'ratingCount' : ratingCount,
                'userReview' : userReview,
                'criticReview': criticReview,
                'time' : time,
                'genre' : genre,
                'releasedate' : releasedate,
                'link' : link}

    keyword_link = link + 'keywords'
    response_keyword = requests.get(keyword_link)
    keyword_page = BeautifulSoup(response_keyword.text, 'html.parser')
    keyword_table = keyword_page.find('div', id = 'keywords_content')
    keywords = keyword_table.find_all('div', class_ = 'sodatext')
    keywords = [keyword.a.text for keyword in keywords]

    film['keywords'] = keywords
    return film

def printFilm(film):
    print(f'Title   : {film["title"]}')
    print(f'Genre   : {film["genre"]}')
    print(f'Rate    : {film["rate"]} / {film["bestrate"]}')
    print(f'Time    : {film["time"]}')
    print(f'Date    : {film["releasedate"]}')
    print(f'Keywords: {", ".join(film["keywords"][:4])}')
    print(f'Link    : {film["link"]}')



if __name__ == '__main__':
    start = time.time()
    keyword = ''
    try:
        keyword = sys.argv[1]
    except IndexError:
        keyword = ""
    try:
        N = int(sys.argv[2])
    except IndexError:
        N = 1
    print(f'Keyword:{keyword}')
    print(f'N: {N}')
    start_url = 'https://www.imdb.com/feature/genre/?ref_=kw_brw_1'
    urlQ = Queue(maxsize=0)
    urlQ.put(start_url)

    response = requests.get(urlQ.get())
    html_soup = BeautifulSoup(response.text, 'html.parser')

    genres_container = html_soup.find_all('div', class_ = 'image')

    for container in genres_container:
        urlQ.put(container.a['href'])

    result = []
    films = []
    url = ''

    print('Searching...')
    print()

    while not urlQ.empty():
        url = urlQ.get()
        response_genre = requests.get(url)
        page = BeautifulSoup(response_genre.text, 'html.parser')
        items = page.find_all('div', class_ ='lister-item mode-advanced')

        for item in items:
            title = item.h3.a.text
            link = 'https://www.imdb.com' + item.h3.a['href']
            if re.search(keyword, title.lower()) and (title, link) not in result:
                result.append((title, link))
                film = getFilm(link)
                printFilm(film)
                films.append(film)
                if len(result) < N:
                    print()
                    print('Searching...')
                    print()
                break
        if len(result) >= N:
            break

        next_page = page.find('a', class_ = 'lister-page-next next-page')
        if next_page != None:
            url = 'https://www.imdb.com' + next_page['href']
            urlQ.put(url)
    finish = time.time()

    print()
    print(f'Elapsed time {finish - start} seconds')