"""
URL mappings for the recipe app.
"""
from django.urls import (
    path,  # function to define a path
    include,  # function to include urls by url names
)

from rest_framework.routers import DefaultRouter  #  default router provided by DRF. u can use this with an API View to automatically create routes for all of the different options availabe for that view.

from recipe import views


router = DefaultRouter()  # create default router
router.register('recipes', views.RecipeViewSet)  # register our viewset with the default router with the name recipes.
router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)

# recipe view will have auto generated URLs depending on the functionality enabled in the viewset.
# since we r using model viewset, it will support all the available methods for CRUD AND HTTP get, put, post, patch, and delete. it will create and register the endpts. for each of those options.
app_name = 'recipe'  # define the name w/c is used to identify the name when we do the reverse lookup of URLs

urlpatterns = [
    path('', include(router.urls)),  # to include the URLs that are generated automatically by the router.
]
# so URL gives u the URL s options and u can use that to retrieve the URLs that r available.

# lastly wire this up inside the main URLs so that we can actually access it . => app/app/urls.py