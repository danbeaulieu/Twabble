from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify

class MyModel(models.Model):
	name = models.CharField(max_length=200)

	def __unicode__(self):
		return "name: %s" % self.name
	
	def get_absolute_url(self):
		return "g"

# Create your models here.
class Game(models.Model):
    ACCESS_CHOICES = (
        (0, 'Public'),
        (1, 'SocialCycle'),
    )
    name = models.CharField(max_length=200)
    leader = models.ForeignKey(User, related_name='leader', null=True, blank=True)
    admin = models.ForeignKey(User, related_name='admin')
    creation_date = models.DateTimeField()
    members = models.ManyToManyField(User, through='Membership')
    access = models.IntegerField(choices=ACCESS_CHOICES)

    def __unicode__(self):
        return "name: %s admin: %s" % (self.name, self.admin)

    def get_absolute_url(self):
        return "/g/%i/" % self.id

#create user, then create game, then create a membership
class Membership(models.Model):
    gameid = models.ForeignKey(Game)
    userid = models.ForeignKey(User)
    join_date = models.DateTimeField(null=True, blank=True)
    total_score = models.IntegerField(default=0)
    slug = models.SlugField()

    class Meta:
        unique_together = ('gameid', 'userid')

    def joined(self):
        return self.join_date != None
    
    def __unicode__(self):
        return "user \"%s\" part of group \"%s\"" % (self.userid.username, self.gameid.name)
    
    def get_absolute_url(self):
        return "/m/%i/%s" % (self.id, self.slug)
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify('%s in game %s' % (self.userid, self.gameid.name))

        super(Membership, self).save(*args, **kwargs)

 
class Word(models.Model):
    word = models.CharField(max_length=200, unique=True)
    score = models.IntegerField()
    
    def __unicode__(self):
        return "word: %s score: %d" % (self.word, self.score)
    
    def getSize(self):
        return int((self.score/51.0) * 30) + 10

class Owners(models.Model):
	membership = models.ForeignKey(Membership)
	word = models.ForeignKey(Word)
	messageid = models.IntegerField()
	
	class Meta:
		unique_together = ('membership', 'word')
	
	def __unicode__(self):
		return "user %s owns word \"%s\" score: %d in game %s" % (self.membership.userid, self.word, self.word.score, self.membership.gameid)
		
#get rid of owner, game replace with foreignkey to membership
class Ownership(models.Model):
    owner = models.ForeignKey(User)
    game = models.ForeignKey(Game)
    word = models.ForeignKey(Word)
    messageid = models.CharField(max_length=200)
    date_won = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('game', 'word')
    
    def __unicode__(self):
        return "user %s owns word \"%s\" score: %d in game %s" % (self.owner, self.word, self.word.score, self.game)

class UserProfile(models.Model):
	user = models.ForeignKey(User)
	access_token = models.CharField(max_length=255, blank=True, null=True, editable=False)
	profile_image_url = models.URLField(blank=True, null=True)
	location = models.CharField(max_length=100, blank=True, null=True)
	url = models.URLField(blank=True, null=True)
	description = models.CharField(max_length=160, blank=True, null=True)
	following = models.BooleanField(default=False)

	def __str__(self):
		return "%s's profile" % self.user

def create_user_profile(sender, instance, created, **kwargs):
	if created:
		profile, created = UserProfile.objects.get_or_create(user=instance)

post_save.connect(create_user_profile, sender=User)

    
