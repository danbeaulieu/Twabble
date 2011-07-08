import urllib2
import simplejson
import time
import pprint
import twitter
import re
import MySQLdb
import os
import cPickle
import socket
from dateutil.parser import *
from datetime import datetime

from django.conf import settings
import settings as tw_settings
settings.configure( 
	DATABASE_ENGINE = tw_settings.DATABASE_ENGINE, 
	DATABASE_NAME = tw_settings.DATABASE_NAME, 
	DATABASE_USER = tw_settings.DATABASE_USER,
    DATABASE_PASSWORD = tw_settings.DATABASE_PASSWORD
)
from games.models import *
from django.contrib.auth.models import User
import logging
import logging.handlers

BOT_PATH = os.path.abspath(os.path.dirname(__file__))
LOG_FILENAME = '%s/logs/botlog.out' % BOT_PATH
# Set up a specific logger with our desired output level
my_logger = logging.getLogger('MyLogger')
my_logger.setLevel(logging.DEBUG)

# Add the log message handler to the logger
handler = logging.handlers.RotatingFileHandler(
              LOG_FILENAME, maxBytes=1000000, backupCount=5)
fm = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(fm)
my_logger.addHandler(handler)


def main():
    my_logger.debug('***starting up*** on %s' % socket.gethostname())
    since_id = None
    word_objs = Word.objects.all()
    api = twitter.Api(username='', password='')
    if socket.gethostname() != 'dan-laptop':
        my_logger.debug('tweeting from the server')
        api.PostUpdate(status=("It's %s. Time to get to work." % datetime.now()))
    while True:
        if since_id == None:
            FILE = open("%s/cPickle.txt" % BOT_PATH, 'r')
            try:
                since_id  = cPickle.load(FILE)
            except EOFError:
                since_id = 0
            finally:
                FILE.close()
            
        my_logger.debug('Get messages since id %s' % since_id)

        
        
        statuses = api.GetFriendsTimeline(count=200, since_id=since_id)
                    #GetFriendsTimeline
        Users = User.objects
        Games = Game.objects
        # need to reverse statuses
        statuses.reverse()
        for s in statuses:
            try:
                user = Users.get(username=s.user.screen_name)
            except User.DoesNotExist:
                continue
            since_id = max(since_id, s.id)
            FILE = open("cPickle.txt", 'w')
            cPickle.dump(since_id, FILE)
            FILE.close()
            #print s.user.name, s.text
            statusDate = parse(s.GetCreatedAt()).replace(tzinfo=None)

            my_logger.debug('status post date %s' % statusDate)
            
            game_list = Games.filter(membership__userid=user).filter(creation_date__lt=statusDate)#and older than this message
            #print '%s - %s' % (s.id, s.text)
            words = re.split('\s', s.text)
            # put it in a set to eliminate duplicates within the message
            words = set(words)
            for token in words:
                try:
                    w = word_objs.get(word=token)
                    #print 'assigning word', w
                    for gamem in game_list:
                        #print 'game created date', gamem.creation_date
                        #if status date came before game creation date, skip
                        # or alternately, check if this exists
                        o = Ownership(owner=user, game=gamem, word=w, messageid=s.id)
                        try:
                            o.save()
                            my_logger.debug('assigning word %s' % w)
                            m = Membership.objects.get(gameid=gamem, userid=user)
                            m.total_score = m.total_score + w.score
                            m.save()
                            #print user, "just earned", w
                        except MySQLdb.IntegrityError:
                            pass
                            # maybe keep a map of games->words we know are taken and test for it at the start
                        except:
                            my_logger.debug('Error')
                    
                except Word.DoesNotExist:
                    # maybe keep a list of bad words so we don't even try. python sets let you manipulate based on union/intersection etc
                    my_logger.debug('Word doesnt exist %s' % token)
        time.sleep(60 * 10) # 10 minutes
#i am going to start by undressing you... slowly.

if __name__ == "__main__":
	main()
