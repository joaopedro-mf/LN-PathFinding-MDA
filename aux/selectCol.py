import csv


fileinclude = '../LN_results_mda_final_all_algoritms.csv'
paths = []
with open(fileinclude, encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        paths.append([row[0],row[1],row[2],row[3],row[7],row[8],row[10],row[13]])

    
saidda = 'LN_results_mda_final.csv'  
with open(saidda, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(paths)
