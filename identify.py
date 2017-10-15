#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  8 09:18:34 2017

@author: yanaotlan
"""

import csv
import re
import json
import collections

def is_prefixed_by(text, prefix, offset):
    """Return True if prefix comes immediately before offset in text"""
    if len(prefix) > offset:
        return False
    return text.startswith(prefix, offset - len(prefix))  

def find_previous_word(text, offset=0):
    num_spaces = 0
    i = offset
    
    while i >= 0 and (text[i].isalnum() or text[i].isspace()):
        if text[i].isspace():
            num_spaces += 1
            if num_spaces == 2:
                break
        else:
            offset = i
        
        i -= 1
    
    return text[offset:].split()[0]

def find_previous_words(text, offset, num_words):
    words = []
    while len(words) < num_words and offset > 0:
        word = find_previous_word(text, offset)
        words.append(word.lower())
        offset -= len(word) + 1
    words.reverse()
    return words

def is_country_representative(text, offset):
    words = ' '.join(find_previous_words(text, offset, 5))
    if re.search('of the republic of', words):
        return True
    if re.search('to republic of', words):
        return True
    if re.search('of the federal republic of', words):
        return True
    return find_previous_word(text, offset) == 'of'

def identify(title, country_finder, demonym_finder, stats):    
    match = country_finder.search(title) 
    if not match:
        return None #No country name indicates internal communication 
    
    if re.search('Memorandum', title, flags = re.IGNORECASE):
        stats['memoranda_count'] += 1
        return None #Memoranda are not direct communication
    
    if not is_country_representative(title, match.start()):
        #print(title) #comment out to print valid titles
        return None
    stats['valid'] += 1
    print(title) #comment out to print invalid titles
        
    
def get_date(row):
    if row['Date'] != 'NA' and row['Date'] != 'Undated':
        return row['Date']
    else:
        return row['Possible Date']

def read_countries():
    with open('countries.csv', mode = 'r', encoding = 'utf-8') as csvfile:
       reader = csv.DictReader(csvfile)
       countries = []
       for row in reader:
           country = row['StateNme']
           if country not in countries:
               countries.append(country)
       return countries
   
def read_demonyms():
    with open('countries.json', mode = 'r', encoding = 'utf-8') as file:
        countries = json.load(file)
        demonyms = []
        for country in countries:
            demonym = country['demonym']
            if demonym not in demonyms and len(demonym) > 0:
                demonyms.append(demonym)
        return demonyms

def make_finder(names):
    exp = '[^\w]|'.join(names)
    return re.compile(exp, flags = re.IGNORECASE)  


def main():
    with open('new_raw.csv', mode = 'r', encoding = 'utf-8') as csvfile:
       reader = csv.DictReader(csvfile)
       
       countries = read_countries()
       demonyms = read_demonyms()
       country_finder = make_finder(countries)
       demonym_finder = make_finder(demonyms)
       
       stats = {'memoranda_count': 0, 'valid': 0}
       for row in reader:
          #print(get_date(row))
           #if get_date(row) < '1930' or get_date(row) == 'NA' or get_date(row) == 'Undated':
               #continue
           identify(row['Title'], country_finder, demonym_finder, stats)
       print(stats)
           
if __name__ == '__main__':
    main()

