#!/usr/bin/env python

import bs4
import urllib3
import os

def get_url(url):
    """Fetch URL contents"""
    urllib3.disable_warnings()
    http = urllib3.PoolManager()
    response = http.request('GET', url)    
    return response.data

def save_url_to_file(url, filename):
    """Download the history.state.gov HTML file with all the .epub links"""
    html = get_url(url)
    book_html_file = open(filename, mode='wb')  # Create the file (for writing.)
    book_html_file.write(html)
    book_html_file.close()

def get_book_html_soup(filename):
    """Create a Beautiful Soup from the HTML book above"""
    # You need to explicitly tell it that the file is UTF-8 encoded,
    # otherwise BeautifulSoup will get confused.
    book_html_file = open(filename, mode='r', encoding='utf-8')
    soup = bs4.BeautifulSoup(book_html_file, 'lxml')
    book_html_file.close()
    return soup

def read_book_urls(soup):
    """Extract all .epub URLs from the Soup"""
    book_urls = []
    for link in soup.findAll('a'):
        url = link.get('href')
        if ".epub" in url:
            book_urls.append(url)
    return book_urls

def download_books(book_urls):
    """Download all the URLs given as an argument"""
    for url in book_urls:
        filename = 'data/' + os.path.basename(url)
        if os.path.exists(filename):
            print("Skipping already downloaded file %s" % (filename))
            continue

        print("Downloading %s to %s" % (url, filename))
        book_file = open(filename, 'wb')
        book_file.write(get_url(url))
        book_file.close()

def main():
    books_url = 'https://history.state.gov/historicaldocuments/ebooks'
    local_file = 'data/ebooks.html'

    if not os.path.exists(local_file):
        if not os.path.exists('data'):
            os.mkdir('data')
        save_url_to_file(books_url, local_file)
    soup = get_book_html_soup(local_file)
    book_urls = read_book_urls(soup)
    download_books(book_urls)

if __name__ == '__main__':
    main()
