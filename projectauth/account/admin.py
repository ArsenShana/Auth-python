from django.contrib import admin
from .models import User, Role, BusinessElement, AccessRule

admin.site.register(User)
admin.site.register(Role)
admin.site.register(BusinessElement)
admin.site.register(AccessRule)