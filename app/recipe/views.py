from django.shortcuts import render
"""
Views for the recipe APIs
"""
from rest_framework import (
    viewsets,
    mixins,   # jst a thing that we can mixin to a view to add additional functionality
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated   # bcz that is the permission that we want to check before users can use the recipe end point.

# Create your views here.
from core.models import (
    Recipe,
    Tag,
    Ingredient,
) # imports our Recipe model and serializers w/c we can use to get our recipe serializers.
from recipe import serializers


# We need to modify the view set and we need to tell it that we're calling the detail endpoint instead of using the recipe serializer that we defined in serializer class we want to use detail serializer.
# for this we override the method called get serializer class so that if user calls the detail endpt., we we'll use the detail serializer instead of defualt w/c is configured for the list view. It is the method called when DRF wants to determine the class that's being used for a particular action.
class RecipeViewSet(viewsets.ModelViewSet):
# there are various different viewsets available 1. model viewset (u specifically set up to work directly with a model.) Wer using it bcz we'll use a lotof the existing logic that is provided by serializer in order to perform CRUD Oprtns.
    """View for manage recipe APIs."""   # APIs bcz viewset will generate different endpoints - list endpt., id endpt. or specific detail endpt. It also able to perform different methods to perform diff. actions on the recipes.
     # Configue our viewset to tell it what we need to use in the system.
    # serializer_class = serializers.RecipeSerializer
    serializer_class = serializers.RecipeDetailSerializer  # Reason why we changed this is bcz now we got the detail serializer, most of the methods that we perform inside the recipe viewset will use the detail one instead of list.
    #  Bcz we have added multiple different endpts. for CRUD on new items. So all the different situations except listing, we wnat to  use the detail serializer.
    queryset = Recipe.objects.all()   # represents the objects that are available for this viewset, bcz this is a model viewset,its expected to work with a model.
    #  above line=>it would return all the objects that we define but
    authentication_classes = [TokenAuthentication]  # in orderto use any of the endpts. provided by this feature u need to use token authentication
    permission_classes = [IsAuthenticated]  # and then u need to be aunthenticated ot use the APIs. If u make request to api and u r unauthenticated, it'll give u an error.

# if we implement the view as it is,it would allow us to manage all of the diff. recipes int he system but we want to ensure that those recipes are filtered to the authenticated user.
#  Therefore we override get_queryset method provided by model viewset.
    def get_queryset(self):  # called in order to get the objects from our quesry set.
        """Retrieve recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')  # but we added an additional filter to filter by the user that is assigned to the request.
# now configure URLs to this recipe viewset
    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':  # check if the action is list
            return serializers.RecipeSerializer   #  then we use the recipe serializer. Now its important that u don't call the constructor of this object bcz this expects u to return a reference to a class not object of a class.so don't use (). You just want to return a reference to the class and then DRF instantiate an object and use in the viewset.

        return self.serializer_class  # else we return the configured serializer class that we configured on our recipe.

# rerun the test

# We need to modify or add one method to our existing view in order to tell it to save the correct user to the recipe that are created.
    def perform_create(self, serializer):    # This method is the way that we override the behaviour for when DRF saves a model in view set. When we create a new object (new recipe) through the create feature of this model view set, we'll call this method as part of that object's creation
        """Create a new recipe."""
        serializer.save(user=self.request.user)  # This will set the user value to the current authenticated user when we save the object.
    # accepts a param called serializer and this should be a validated serializer. So we expect serializer data to be already validated by the view set before this method is called and thenthis method is called
# This makes our test pass and ensure that new recipes are created have the correct user id assigned. Now rerun the test and it passes.

# bcz we r going to have basic CRUD implementation, we'll use the viewset bcz its just simple to CRUD on a model
class TagViewSet(mixins.DestroyModelMixin,   # implement feature for deleting the tag by adding another mixin that allow us to destroy. Run the test, it passes and => implemented the ability to delete models
                 mixins.UpdateModelMixin,   # We need to modify the mixins so that we can have the update model mixin. ensure mixins are defined before the generic feature(so that it can override some behaviour),imp as defined in DRF documnetation. run test again, should pass.
                 mixins.ListModelMixin,   # This is a mixin that allows u to add the listing functionality for listing models, generic viewset allows u to throw mixin so that we can have the viewset functionality that we desire for our articular API
                 viewsets.GenericViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Now we need to override the get query set method that comes with our viewset to ensure we return only the queryset objects for the authenticated user, by default, it would return all of the different tags that exist in the db regardless of the user that created them. We wanna ensure that we filter them down to the user that created them.
    def get_queryset(self):
        """Filter queryset to authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-name')  # We like to be expilixit whil ereturning objects as sometimes depending on version or type of the db, it may return them in a different order, so u shoul=d always add a feature where the user can customize the order, so we hard coded so that oit orders by reverse name
# Now add the URL mapping for this view.
# Modify to support updating the tag items, can be done easily bcz we have viewset and we r using the mixins.


class IngredientViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Manage ingredients in the database."""
    serializer_class = serializers.IngredientSerializer  # specified th eserializer class and set it to our new ingredient serializer
    queryset = Ingredient.objects.all()  # sets our query set to the ingredients objects, it tells DRF what models we want to be manageable through the ingredient view set.
    authentication_classes = [TokenAuthentication]   # adds the support for using token authentication, this i sthe only option for authentication on this viewset.
    permission_classes = [IsAuthenticated]   # it means all users musyt be authenticated to use this endpt, u can't make request to the endpt. unless u r authenticated.
# defined the ingredient viewset

    def get_queryset(self):   # to filter the objects that are managed by this view set to the authenticated user. we only want users to view and update and make changes to their ingredients, not other user's ingredients
        """Filter queryset to authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-name')   # wire this view to a url
