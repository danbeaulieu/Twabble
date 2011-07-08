# Create your views here.
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from Twabble.games.models import Game, Membership, Ownership, Word
from Twabble.games.forms import NewGameForm, SearchForm
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

import oauthtwitter
import MySQLdb
from datetime import datetime
import twitter
from django.conf import settings
import oauth 
import urllib2
from utils import *

#   
CONSUMER_KEY = getattr(settings, 'CONSUMER_KEY', 'YOUR_KEY')  
CONSUMER_SECRET = getattr(settings, 'CONSUMER_SECRET', 'YOUR_SECRET')  
#

#
testdict = dict({'one':0})

# tests for a social circle, where a user follows the admin and the admin follows the user
# this needs to be refactored, otherwise we are going to constantly hit the twitter api
def allowed(game, user):
    api = twitter.Api(username='PlayTwabble', password='winter72')
    twitteruser = api.GetUser(user=user.username)
    adminfriends = api.GetFriends(user=game.admin.username)

    if twitteruser not in adminfriends:
        return False #just quit now

    twitteradmin = api.GetUser(user=game.admin.username)
    userfriends = api.GetFriends(user=user.username)
    if twitteradmin in userfriends:
        return True
    else:
        return False

def follow(request):
    userprofile = request.user.get_profile()
    if(userprofile.following == 0):
        # not following this user, need to to get the updates in our stream
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        # this creates a password manager
        passman.add_password(None, 'http://twitter.com', 'PlayTwabble', 'winter72')
        authhandler = urllib2.HTTPBasicAuthHandler(passman)
        # create the AuthHandler
        opener = urllib2.build_opener(authhandler)
        urllib2.install_opener(opener)
        req  = urllib2.Request('http://twitter.com/friendships/create/%s.json' % request.user, "")
        #urllib2.urlopen('http://twitter.com/friendships/create/%s.json' % request.user)
        try:				
            urllib2.urlopen(req)
            userprofile.following = 1
            userprofile.save()
        except:
            pass

def index(request):    active_games = Game.objects.all()[:5]
    newest_games = Game.objects.order_by('-creation_date')[:5]
    return render_to_response('games/index.html', {'active_games': active_games, 'newest_games': newest_games}, context_instance = RequestContext(request))

def login_prompt(request):
    request.session['game_action'] = request.GET['next']
    return render_to_response('games/login_prompt.html')

def member_stats(request, membership_id, membership_slug):
    try:
        m = Membership.objects.get(id=membership_id)
        oships = Ownership.objects.filter(game=m.gameid, owner=m.userid)
    except Membership.DoesNotExist:
        m = None
        oships = None
    return render_to_response('games/member_stats.html', {'membership' : m, 'oships': oships}, context_instance = RequestContext(request))

def twuser(request, twuser_id, twuser_name):
    # shows games and words owned by this user
    try:
        twuser = User.objects.get(id=twuser_id)
        games = Game.objects.filter(membership__userid=twuser)
        words = Word.objects.filter(id__in=twuser.ownership_set.values_list('word', flat=True).distinct())
    except User.DoesNotExist:
        twuser = None
        words = None
        games = None
    return render_to_response('games/user.html', {'twuser' : twuser, 'owned': words, 'games': games}, context_instance = RequestContext(request))

def search(request):
    games = None
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            games = Game.objects.filter(name__icontains=form.cleaned_data['name'])
    else:
        form = SearchForm() # An unbound form
	
    return render_to_response('games/search.html', {'games' : games, 'form': form}, context_instance = RequestContext(request))

#@login_required
def start(request):
    """Return form to make a game"""
    if request.method == 'POST': # If the form has been submitted...
        if not request.user.is_authenticated():
            return HttpResponseRedirect('/accounts/login/?next=%s' % request.path)
        form = NewGameForm(request.POST, httprequest=request) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            # make a new game with this user as the admin, and add a membership relationship
            g = Game(name=form.cleaned_data['name'], admin=request.user, access=form.cleaned_data['invite'], creation_date=form.cleaned_data['start'])
            g.save()		
            m = Membership(gameid=g, userid=request.user, join_date=datetime.now(), total_score=0)
            m.save()
            follow(request)
            if form.cleaned_data['send_tweet']:
                access_token = request.session.get('access_token', None)
                access_token = oauth.OAuthToken.from_string(access_token)
                
                twitter_inst = oauthtwitter.OAuthApi(CONSUMER_KEY, CONSUMER_SECRET, access_token)
                twitter_inst.PostUpdate(status="I just created a game at Twabble.com . Join my game and play against me at http://www.PlayTwabble.com/g/%s" % g.id)
            #userprofile = request.user.get_profile()
            #if(userprofile.following == 0):
            #    # not following this user, need to to get the updates in our stream
            #    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
            #    # this creates a password manager
            #    passman.add_password(None, 'http://twitter.com', 'PlayTwabble', 'winter72')
            #    authhandler = urllib2.HTTPBasicAuthHandler(passman)
            #    # create the AuthHandler
            #    opener = urllib2.build_opener(authhandler)
            #    urllib2.install_opener(opener)
            #    req  = urllib2.Request('http://twitter.com/friendships/create/%s.json' % request.user, "")
            #    #urllib2.urlopen('http://twitter.com/friendships/create/%s.json' % request.user)
            #    try:				
            #        urllib2.urlopen(req)
            #        userprofile.following = 1
            #        userprofile.save()
            #    except:
            #        pass
				
            return HttpResponseRedirect('/g/%d' % (g.id) ) # Redirect after POST
    else:
        form = NewGameForm() # An unbound form
	
    return render_to_response('games/start.html', {'form' : form}, context_instance = RequestContext(request))

# this has been deprecated, see game view in POST block
@login_required
def join(request, game_id):
    # add a membership and follow this user
    try:
        g = Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        g = None
        return render_to_response('games/game.html', {'game' : g, 'game_id' : game_id}, context_instance = RequestContext(request))
    if g.get_access_display() != 'Public':
        if allowed(game=g, user = request.user):
            return "you are allowed"
        else:
            return "You aren't friends"
        #else: don't make the membership, show an error
    m = Membership(gameid=g, userid=request.user, join_date=datetime.now())
    m.save()
    follow(request)
    return game(request, game_id)
    #return render_to_response('games/game.html', {'game' : g}, context_instance = RequestContext(request))

def games(request):
    if request.user.is_anonymous():
        game_list = None
    else:
        game_list = Game.objects.filter(membership__userid=request.user)
    return render_to_response('games/games.html', {'game_list' : game_list}, context_instance = RequestContext(request))

def game(request, game_id=None):
    testdict['one'] = testdict['one'] + 1
    denied = None
    try:
        game = Game.objects.get(id=game_id)
        #members = game.members.all() - This gets all the User objects for this game through the membership relationship
        #words taken in this game
        wordsOwned = Ownership.objects.filter(game=game)
        if request.method == 'POST': # this means a join or a leave
            button = request.POST.get('Button', '')
            if button == 'Join Game':
                if game.get_access_display() != 'Public' and not allowed(game=game, user = request.user): # this is gross
                    denied = True
                else:
                    try:
                        m = Membership(gameid=game, userid=request.user, join_date=datetime.now(), total_score=0)
                        m.save()
                        follow(request)
                    except MySQLdb.IntegrityError:
                        pass
            if button == 'Leave Game':
                #delete membership
                try:
                    memb_to_leave = Membership.objects.get(gameid=game, userid=request.user)
                    memb_to_leave.delete()
                    # unfollow if memberships == 0
                except Membership.DoesNotExist:
                    pass 
            if button == 'Delete Game':
                try:
                    Membership.objects.filter(gameid=game).delete()
                    Ownership.objects.filter(game=game).delete()
                    #for mtd in memberships_to_delete:
                    #    mtd.delete()
                    game.delete()
                    # also delete ownerships
                    return games(request)
                except Game.DoesNotExist:
                    pass       
        memberships = Membership.objects.filter(gameid=game)
        tagCloudSize(memberships)
        if request.user.is_anonymous():
            m = None
        else:
            m = Membership.objects.get(gameid=game, userid=request.user)
    except Game.DoesNotExist:
        game = None
        m = None
        memberships = None
        wordsOwned = None
    except Membership.DoesNotExist:
        m = None
    if game != None and game.admin == request.user:
        #this is the admin
        return render_to_response('games/gameadmin.html', {'game' : game, 'member' : m, 'memberships' : memberships, 'wordsOwned' : wordsOwned}, context_instance = RequestContext(request))	
    return render_to_response('games/game.html', {'game' : game, 'member' : m, 'memberships' : memberships, 'wordsOwned' : wordsOwned, 'denied': denied}, context_instance = RequestContext(request))

def mygames(request):
    if request.user.is_anonymous():
        game_list = None
    else:
	    game_list = Game.objects.filter(membership__userid=request.user)
    return render_to_response('games/games.html', {'game_list' : game_list}, context_instance = RequestContext(request))	

def twitter_signin(req):
	#if req.user: return HttpResponseRedirect('auth_info')
	token = get_unauthorized_token()
	req.session['token'] = token.to_string()
	return HttpResponseRedirect(get_authorization_url(token))

def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/")

def twitter_return(req):
    token = req.session.get('token', None)
    if not token:
        return render_to_response('callback.html', { 'token': True })
    token = oauth.OAuthToken.from_string(token)
    if token.key != req.GET.get('oauth_token', 'no-token'):
        return render_to_response('callback.html', {
            'mismatch': True
        })
    token = get_authorized_token(token)
    req.session['access_token'] = token.to_string()
    auth_user = authenticate(access_token=token)

	# if user is authenticated then login user
    if auth_user:
        login(req, auth_user)
    else:
        # We were not able to authenticate user
        # Redirect to login page
        #del req.session['access_token']
        #del req.session['request_token']
        return HttpResponse("Unable to authenticate you!")
    
    next = req.session.get('game_action', None)
    if next:
        del req.session['game_action']
        return HttpResponseRedirect(next)
	# authentication was successful, use is now logged in
    return HttpResponseRedirect("/")# Actually login
#	obj = is_authorized(token)
#	if obj is None:
#		return render_to_response('callback.html', {
#			'username': True
#		})
#	try: user = User.objects.get(username=obj['screen_name'])
#	except: user = User(username=obj['screen_name'])
#	user.oauth_token = token.key
#	user.oauth_token_secret = token.secret
#	user.save()
#	req.session['user_id'] = user.id
#	del req.session['token']
#
#	return HttpResponseRedirect(reverse('auth_info'))

def tagCloudSize(memberships):
    maxScore = max(float(memberships.order_by('-total_score')[0].total_score), 1.0)
    #minScore = memberships.order_by('total_score')[0]
    maxSize = 30
    minSize = 10
    for m in memberships:
        m.fontSize = int((m.total_score/maxScore) * maxSize) + minSize

