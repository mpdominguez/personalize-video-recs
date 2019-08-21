import csv
with open('u.item') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter='|')
    line_count = 0
    for row in csv_reader:
        line_count += 1
        if ((row[1] == "") or (row[2] == "") or (row[4] == "")):
            print 'Skipping movie ID=' + str(line_count)
