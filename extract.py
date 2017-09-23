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
        return True
    else:
        print('FAIL: ' + str(text) + ' => ' + str(value))  
        return False

def prefix_tests():
    expect_equal(is_prefixed_by('nyan','nya',3),True,'nyan')
    expect_equal(is_prefixed_by('14th of May, 1865',' of ',8), True, '1865-05-14')
    expect_equal(is_prefixed_by('14th day of May, 1865', ' day of ',12), True, '1865-05-14')

def find_previous_word(text, offset=0):
    num_spaces = 0
    i = offset
    
    while (text[i].isalnum() or text[i].isspace()):
        if text[i].isspace():
            num_spaces += 1
            if num_spaces == 2:
                return i + 1
            
        if i == 0:
            return 0
        
        i -= 1
    
    i += 1
    while text[i].isspace():
        i += 1
    return i

def previous_tests():
    expect_equal(find_previous_word('one two three', 4), 0, 'first')
    expect_equal(find_previous_word('one two three', 8), 4, 'second')
    expect_equal(find_previous_word('one two three', 0), 0, 'zeroth')
    expect_equal(find_previous_word('[Document 336]November', 14), 14, 'bracket')
    expect_equal(find_previous_word('[Document 336] November', 15), 15, 'bracket2')
    expect_equal(find_previous_word('[Document 336]hi November', 17), 14, 'bracket3')
    
def extract_date(text, offset=0):
    text = text[offset:]
    
    # First we search for a month by full name. (A|B finds either A or B.)
    months = {'january':1, 'jan.':1,
              'february':2, 'feb.':2,
              'march':3, 'mar.':3,
              'april':4, 'apr.':4,
              'may':5, 
              'june':6, 'jun.':6,
              'july':7, 'jul.':7,
              'august':8, 'aug.':8, 
              'september':9, 'sep.':9,
              'october':10, 'oct.':10,
              'november':11, 'nov.':11,
              'december':12, 'dec.':12}
    exp = '|'.join(months.keys()).replace('.','\.') #make 'january|jan|february|feb...'
    match = re.search(exp, text, flags = re.IGNORECASE) 
    if not match:
        if 'undated' in text.lower():
            return 'Undated'
        return None

    # We found one. Use the match to get the month found, and then its index in the year.
    month_name = text[match.start() : match.end()]
    month = months[month_name.lower()]


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
    
    search_begin = find_previous_word(text, search_begin)
    search_end = min(match.end() + 30, len(text))
    search_space = text[search_begin : search_end]

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
    return expect_equal(res, date, text)
    

def run_tests():
    tests = [('January 4, 1952.', '1952-01-04'), 
             ('June 19, 1953.', '1953-06-19'),
             ('October 8, 1954-7 p.m.', '1954-10-08'),
             ('White House, 9:05 a.m., December 17, 1954', '1954-12-17'),
             ('Washington, undated', 'Undated'),
             ('May4, 1865', '1865-05-04'),
             ('Nyans were born in September, 1990', '1990-09'),
             ('Creatures were born in February 1980, on the 20th', '1980-02-20'),
             ('Undated', 'Undated'),
             ('14th of May, 1865', '1865-05-14'),
             ('14th day of May, 1865', '1865-05-14'),
             ('We met on the 10th of April, but the agreement was signed on the 16th day of May, 1992', '1992-05-16'),
             ('the 22d day of the month of April, 1865', '1865-04-22'),
             ('15th day of September (Saturday), 1990', '1990-09-15'),
             ('15th April, 1986', '1986-04-15'),
             #('15th day of September (Saturday), of the year 1990.','1990-09-15'),
             ('april 22nd, 1986', '1986-04-22'),
             #('the second day of June, the year of our Lord One thousand eight hundred and sixty-five.','1865-06-02'),
             ('on the 12th day of May, in the year 1865','1865-05-12'),
             ('on the 12th day of May, in the year of our Lord 1865','1865-05-12'),
             ('File No. 837.00/571. [Document 336]February 19, 1912.No. 122.]Sir: I','1912-02-19'),
             ('Telegram transmitted to the Secretary of State Dec. 11, 1911','1911-12-11')]
    num_success = 0
    for (text, expected_result) in tests:
        success = test_extract_date(text,expected_result)
        if success:
            num_success += 1
    print('\n{} out of {} tests succeeded'.format(num_success, len(tests)))
    
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
        maybe_date = extract_date(title)
    if not date and not maybe_date:
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
    main()
    #run_tests()
    #prefix_tests()
    #previous_tests()
