import csv

with open('nyan.csv', 'w') as csvfile:
    nyanwriter = csv.writer(csvfile)
    nyanwriter.writerow(['Name','Age','Cuteness'])
    nyanwriter.writerow(['Creature,sea',37,0.3])
    nyanwriter.writerow(['Nyan-Nyan','nyan',999999])