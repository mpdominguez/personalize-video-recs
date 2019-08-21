import psycopg2
import json
import csv

HOST = 'personalize.c0azewoaia5d.us-east-1.rds.amazonaws.com'
DATABASE = 'videorec'
USER = 'vidrecdemo'
PASSWORD = 'recPassw0rd'
BLANK = ''
SQL = 'INSERT INTO recommend_user (forename, surname, age, gender, occupation, zipcode) VALUES (%s, %s, %s, %s, %s, %s)'

conn = psycopg2.connect(host='personalize.c0azewoaia5d.us-east-1.rds.amazonaws.com', database='videorec', user='vidrecdemo', password='recPassw0rd')
curs = conn.cursor()

with open('ml-100k/u.user') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter='|')
    line_count = 0
    for row in csv_reader:
        curs.execute(SQL, (BLANK, BLANK, int(row[1]), row[2], row[3], row[4]))
        line_count += 1
        if ((line_count % 250) == 0):
            print 'Reached ' + str(line_count) + ' lines.'
    print 'Processed ' + str(line_count) + ' lines.'

conn.commit()
curs.close()
conn.close()
