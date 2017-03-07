from django.contrib import admin

from .models import Syndicate
from .models import PremiumBond
from .models import UserProfile

# Register your models here.
admin.site.register(Syndicate)
admin.site.register(PremiumBond)
admin.site.register(UserProfile)
