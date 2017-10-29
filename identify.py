#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  8 09:18:34 2017

@author: yanaotlan
"""

import csv
import re
import json
import sys
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

def identify_participants(title, country_finder, demonym_finder, stats):    
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
    
def track_countries(text, date, countries, country_finder, writer):
    if date == '' or date == 'NA' or date == 'Undated':
        return
    
    countries_found = set()
    match_iter = country_finder.finditer(text)
    for match in match_iter:
        country = match.group(0)
        if not country[0].isalpha():
            country = country[1:]
                              
        if not country[-1].isalpha():
            country = country[:-1]
        try:
            ccode = countries[country.lower()]
            countries_found.add((country, ccode))
        except:
            print("Unexpected error:", sys.exc_info()[0])
    
    for (country, ccode) in countries_found:
        writer.writerow([date, country, ccode])
    
def get_date(row):
    if row['Date'] != 'NA' and row['Date'] != 'Undated' and row['Date'] != '':
        return row['Date']
    else:
        return row['Possible Date']

def read_countries():
    with open('countries.csv', mode = 'r', encoding = 'utf-8') as csvfile:
       reader = csv.DictReader(csvfile)
       countries = ['soviet union']
       for row in reader:
           country = row['StateNme']
           if country not in countries:
               countries.append(country)
       return countries
   
def read_country_map():
    with open('countries.csv', mode = 'r', encoding = 'utf-8') as csvfile:
       reader = csv.DictReader(csvfile)
       countries = {'soviet union': 365}
       for row in reader:
           country = row['StateNme'].lower()
           ccode = row['CCode']
           countries[country] = ccode
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
    exp = '|'.join([ "[^\w]" + name + "[^\w]" for name in names])
    return re.compile(exp, flags = re.IGNORECASE)  


def main():
    with open('raw.csv', mode = 'r', encoding = 'utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        csv.field_size_limit(sys.maxsize)
        
        with open('country_timeline.csv', 'w') as csvfile:
            writer = csv.writer(csvfile) 
            writer.writerow(['Date','Country','CCode'])
            
            countries = read_country_map()
            demonyms = read_demonyms()
            country_finder = make_finder(countries.keys())
            #demonym_finder = make_finder(demonyms)
       
            #stats = {'memoranda_count': 0, 'valid': 0}
            for row in reader:
                track_countries(row['Text'], get_date(row), countries, country_finder, writer)

                #identify_participants(row['Title'], country_finder, demonym_finder, stats)
            #print(stats)
           
if __name__ == '__main__':
    main()

