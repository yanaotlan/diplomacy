#!/usr/bin/env python

import bs4
import csv
import glob
import os
import re
import shutil
import zipfile

# 1. Iterate over the document (d-files.)
# 2. Extract the title and text from each document using BeautifulSoup.
# 3. Store the data in a csv file, with title.

def find_epubs(path):
    """Return a list of all the .epub files in the given directory"""
    return glob.glob(path + "/*.epub")

def unzip(book, to_directory):
    """Unzip file to the given path"""
    if os.path.exists(to_directory):
        shutil.rmtree(to_directory)
    os.mkdir(to_directory)

    print("Extracting " + book)
    zip_ref = zipfile.ZipFile(book, 'r')
    zip_ref.extractall(to_directory)
    zip_ref.close()

def find_pages(path):
    """Return a list of all the d*.html files in the given path"""
    return glob.glob(path + "/d*.html")

def is_prefixed_by(text, prefix, offset):
    """Return True if prefix comes immediately before offset in text"""
    if len(prefix) > offset:
        return False
    return text.startswith(prefix, offset - len(prefix))

def expect_equal(value, ref, text):
    if value == ref:
        print('PASS: ' + str(text) + ' => ' + str(value))
    else:
        print('FAIL: ' + str(text) + ' => ' + str(value))   

def prefix_tests():
    expect_equal(is_prefixed_by('nyan','nya',3),True,'nyan')
    expect_equal(is_prefixed_by('14th of May, 1865',' of ',8), True, '1865-05-14')
    expect_equal(is_prefixed_by('14th day of May, 1865', ' day of ',12), True, '1865-05-14')
    

def extract_date(text, offset=0):
    text = text[offset:]
    
    # First we search for a month by full name. (A|B finds either A or B.)
    months = ['january', 'february', 'march', 'april', 'may', 'june', 'july',
              'august', 'september', 'october', 'november', 'december']
    match = re.search('|'.join(months), text, flags = re.IGNORECASE) 
    if not match:
        if 'undated' in text.lower():
            return 'Undated'
        return None

    # We found one. Use the match to get the month found, and then its index in the year.
    month_name = text[match.start() : match.end()]
    month = months.index(month_name.lower()) + 1
    
    print(month)

    # Now that we have the month, the day and year should surround the month.
    # We will find all the numbers in that small segment of the text, and then
    # assume that the smallest number is the day and the largest number is the
    # year.
    search_begin = match.start()
    
    if is_prefixed_by(text, ' day of the month of ', match.start()):
        search_begin -= len(' day of the month of ')
    elif is_prefixed_by(text, ' day of ', match.start()):
        search_begin -= len(' day of ')
    elif is_prefixed_by(text, ' of ', match.start()):
        search_begin -= len(' of ') # same as "search_begin - 8"
    
    search_begin = max(search_begin - len('NNth '), 0)
    search_end = min(match.end() + 30, len(text))
    search_space = text[search_begin : search_end]
    
    print(search_space)

    # The special character \d matches a digit, and + means "one or more of the previous". So fo
    # instance re.findall('\d+', 'there are 14 geese with 2 wings') will return ['14', '2'].
    numbers = re.findall('\d+', search_space)
    if len(numbers) == 0:
        return extract_date(text, match.end())

    # Convert all the numbers from strings to numeric values.
    numbers = list(map(int, numbers))

    # If we have multiple numbers, we'll assume the largest is the year and the
    # smallest is the day.
    if len(numbers) >= 2:
        numbers = numbers[0:2]
        day = min(numbers)
        year = max(numbers)
        if day > 31 or year < 1800 or year > 2100:
            return extract_date(text, match.end())

        return "{:04d}-{:02d}-{:02d}".format(year, month, day)
    else:
        year = int(numbers[0])
        if year < 1800:
            return extract_date(text, match.end())

        return "{:04d}-{:02d}".format(year, month)

def test_extract_date(text, date):
    res = extract_date(text)
    expect_equal(res, date, text)

def tests():
    test_extract_date('January 4, 1952.', '1952-01-04')
    test_extract_date('June 19, 1953.', '1953-06-19')
    test_extract_date('October 8, 1954-7 p.m.', '1954-10-08')
    test_extract_date('White House, 9:05 a.m., December 17, 1954', '1954-12-17')
    test_extract_date('Washington, undated', 'Undated')
    test_extract_date('May4, 1865', '1865-05-04')
    test_extract_date('Nyans were born in September, 1990', '1990-09')
    test_extract_date('Creatures were born in February 1980, on the 20th', '1980-02-20')
    test_extract_date('Undated', 'Undated')
    test_extract_date('14th of May, 1865', '1865-05-14')
    test_extract_date('14th day of May, 1865', '1865-05-14')
    test_extract_date('We met on the 10th of April, but the agreement was signed on the 16th day of May, 1992', '1992-05-16')
    test_extract_date('the 22d day of the month of April, 1865', '1865-04-22')
    test_extract_date('15th day of September (Saturday), 1990', '1990-09-15')
    test_extract_date('15th April, 1986', '1986-04-15')
    #test_extract_date('15th day of September (Saturday), of the year 1990.','1990-09-15')
    test_extract_date('april 22nd, 1986', '1986-04-22')
    #test_extract_date('the second day of June, the year of our Lord One thousand eight hundred and sixty-five.','1865-06-02')
    test_extract_date('on the 12th day of May, in the year 1865','1865-05-12')
    test_extract_date('on the 12th day of May, in the year of our Lord 1865','1865-05-12')
    
def extract_page_contents(path):
    """Extract title, date and text from the given HTML document (returns True if successful)"""
    page = open(path, mode = 'r', encoding = 'utf-8')
    soup = bs4.BeautifulSoup(page, "lxml")
    page.close()
    
    #Extract title.
    title = soup.title.text
    if 'Editorial Note' in title:
        return None #(here None is the same as False, but not always)

    #Extract date.
    date = None
    maybe_date = None
    date_tags = soup.find_all('p', 'dateline')

    if len(date_tags) > 0:
        date = extract_date(date_tags[0].text)
    if not date:
        date = extract_date(title)
    if not date:
        maybe_date = extract_date(soup.text)
    #if not date and not maybe_date:
        #raise Exception('Failed to find a date for {}'.format(path))

    
    #Extract text.
    text = soup.text
    return {'title': title, 'date': date, 'maybe_date': maybe_date, 'text': text}
    
    #print('title: {}\ndate: {}\ntext: {}'.format(title.encode('utf-8'), date, text))
    #return True

def main():
    with open('raw.csv', mode = 'w', encoding = 'utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Title', 'Date', 'Possible Date', 'Text', 'Book', 'Page'])
        
        for book in find_epubs("data"):
            unzip(book, "book")
            for page in find_pages("book/OEBPS"):
                contents = extract_page_contents(page)
                if contents:
                    writer.writerow([contents['title'], 
                                     contents['date'],
                                     contents['maybe_date'],
                                     contents['text'], 
                                     book, 
                                     page])

if __name__ == '__main__':
    #main()
    tests()
    #prefix_tests()