from django.contrib import admin
from .models import (
    Category,
    CollectionCentre,
    Staff,
    User,
    CollectionRequest,
    Assignment,
    Collection,
    Recycling,
    Feedback
)

admin.site.register(Category)
admin.site.register(CollectionCentre)
admin.site.register(Staff)
admin.site.register(User)
admin.site.register(CollectionRequest)
admin.site.register(Assignment)
admin.site.register(Collection)
admin.site.register(Recycling)
admin.site.register(Feedback)