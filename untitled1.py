import pandas as pd


### Extract participants

#1.Iterate over the entries in the raw file 
#2.Identify titles that include entries such as "ambassador of country A", "president of country B"
#3.Add participants (names if possible and country of origin) to the file
#   3.1. format: sender country| sender name | receiver country | receiver name

#take a random sample from the big raw file to work with
def test_sample(file, size, column = 'Title'):
    #read the raw file
    df = pd.read_csv(file)
    #sample the file
    sample = df.sample(n = size, replace = False)
    column = sample[column]
    #print(column)

def test_main():
    test_sample('raw.csv', 10000)
    #get participants ( people divided by 'to')

if __name__ == '__main__':
    test_main()