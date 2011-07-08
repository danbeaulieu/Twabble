from __future__ import with_statement
import os
from django.conf import settings
settings.configure( 
	DATABASE_ENGINE = "mysql", 
	DATABASE_NAME = "twabble", 
	DATABASE_USER = "root",
    DATABASE_PASSWORD = '1timesone'
	#INSTALLED_APPS = ("tunes")
)
from games.models import *

def getScore(word):
    total = 0
    for ch in word:
        total = total + values[ch]
    return total

values = dict()

letter = set('EAIONRTLSU')
for l in letter:
    values[l] = 1
letter = set('DG')
for l in letter:
    values[l] = 2
letter = set('BCMP')
for l in letter:
    values[l] = 3
letter = set('FHVWY')
for l in letter:
    values[l] = 4
values['K'] = 5
letter = set('JX')
for l in letter:
    values[l] = 8
letter = set('QZ')
for l in letter:
    values[l] = 10

count = 0
with open('%s/TWL06.txt' % os.getcwd(), 'r') as f:
    for line in f:
        word_line = line.strip()
        w = Word(word=word_line, score=getScore(word_line))
        #print w        
        w.save()
        count = count + 1
        if count % 5000 == 0:
            print w, count
        
        
print count


