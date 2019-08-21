import psycopg2
import json
import csv

HOST = 'personalize.c0azewoaia5d.us-east-1.rds.amazonaws.com'
DATABASE = 'videorec'
USER = 'vidrecdemo'
PASSWORD = 'recPassw0rd'
BLANK = ''
SQL = 'INSERT INTO recommend_movies (movie_id, title, year, image_url, is_action, is_adventure, is_animation, is_childrens, is_comedy, is_crime, is_documentary, is_drama, is_fantasy, is_filmnoir, is_horror, is_musical, is_mystery, is_romance, is_scifi, is_thriller, is_war, is_western) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

conn = psycopg2.connect(host='personalize.c0azewoaia5d.us-east-1.rds.amazonaws.com', database='videorec', user='vidrecdemo', password='recPassw0rd')
curs = conn.cursor()

with open('u.item') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter='	')
    line_count = 0
    for row in csv_reader:
        curs.execute(SQL, (int(row[0]), row[1], int(row[2]), row[4], bool(int(row[6])), bool(int(row[7])), bool(int(row[8])), bool(int(row[9])), bool(int(row[10])), bool(int(row[11])), bool(int(row[12])), bool(int(row[13])), bool(int(row[14])), bool(int(row[15])), bool(int(row[16])), bool(int(row[17])), bool(int(row[18])), bool(int(row[19])), bool(int(row[20])), bool(int(row[21])), bool(int(row[22])), bool(int(row[23])) ) )
        line_count += 1
        if (((line_count % 100) == 0) or (line_count >=2000)):
            print 'Reached ' + str(line_count) + ' lines.'
    print 'Processed ' + str(line_count) + ' lines.'

conn.commit()
curs.close()
conn.close()
