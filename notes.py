def identify(title, country_finder, demonym_finder, stats):    
    match = country_finder.search(title) 
    if not match:
        return None #No country name indicates internal communication 
    
    if re.search('Memorandum', title, flags = re.IGNORECASE):
        return None #Memoranda are not direct communication
    
    word = find_previous_word(title, match.start())
    if word in stats:
        stats[word] += 1
    else:
        stats[word] = 1
        
    if word == 'of':
        maybe_title = find_previous_word(title, match.start()-len(word))
        if maybe_title == 'Republic':
            print(title)
        #print('{} \t {}'.format(maybe_title, title))
 
        #print('Found \'in {}\' in {}'.format(match.group(0), title))
        #exclude: and before cname, memorandum, to, between, in, for
        #include Federal Republic of, to Republic of China 
        
        
        
Next time!
add participants to all messages where applicable (US and ...)
mark valid messages
write to csv
add code to create new_raw_csv to identify.py