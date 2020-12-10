# file = open("Tonale06Feb19.csv", 'r')
# allLines = file.read().split("\n")
import csv as csv
dato=input('Inserire 15 per la differenza Normalizzata B2-B8 o 16 per la differenza Normalizzata B3-B11: ')
fileToSave = open("12Mar2020Adamello.csv",'w')
with open('12Mar2020AdamelloNDSIfirst1.csv', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for line in reader:
        #print(line[1])
        if dato=='15': 
            fileToSave.write(line[20]+","+line[15]+","+line[1]+'\n')
            print(line[15])
        elif dato=='16': 
            fileToSave.write(line[20]+","+line[16]+","+line[1]+'\n')
            print(line[16])
        #fileToSave.write(line[20]+","+line[15]+","+line[16]+","+line[1]+'\n')
print("Done!")
