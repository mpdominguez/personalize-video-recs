import psycopg2
import json
import csv

HOST = 'personalize.c0azewoaia5d.us-east-1.rds.amazonaws.com'
DATABASE = 'videorec'
USER = 'vidrecdemo'
PASSWORD = 'recPassw0rd'
BLANK = ''
SQL = 'INSERT INTO recommend_reviews (user_id, movie_id, rating, timestamp) VALUES (%s, %s, %s, %s)'

conn = psycopg2.connect(host='personalize.c0azewoaia5d.us-east-1.rds.amazonaws.com', database='videorec', user='vidrecdemo', password='recPassw0rd')
curs = conn.cursor()

with open('ml-100k/u.data') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter='	')
    line_count = 0
    for row in csv_reader:
        curs.execute(SQL, (int(row[0]), int(row[1]), int(row[2]), int(row[3])))
        line_count += 1
        if ((line_count % 1000) == 0):
            print 'Reached ' + str(line_count) + ' lines.'
    print 'Processed ' + str(line_count) + ' lines.'

conn.commit()
curs.close()
conn.close()
