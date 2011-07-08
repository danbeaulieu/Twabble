from Twabble.games.models import Game
from Twabble.games.models import Ownership
from Twabble.games.models import Owners
from Twabble.games.models import Word
from Twabble.games.models import Membership
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


class MembershipInline(admin.TabularInline): 
	model = Membership
	extra = 1 

class MyUserAdmin(UserAdmin): 
	inlines = (MembershipInline,)
	
class GameAdmin(admin.ModelAdmin): 
	inlines = (MembershipInline,) 

admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Ownership)
admin.site.register(Word)
admin.site.register(Owners)

#admin.site.register(Game)
#admin.site.register(Membership)
