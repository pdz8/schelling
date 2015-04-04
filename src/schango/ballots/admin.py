from django.contrib import admin
import ballots.models as bm


###################
## Admin classes ##
###################

class BallotAdmin(admin.ModelAdmin):
	list_display = ['question']



###############################
## Register your models here ##
###############################

admin.site.register(bm.Ballot, BallotAdmin)
admin.site.register(bm.EthAccount)
