"""
Serializers for recipe APIs
"""
from rest_framework import serializers

from core.models import (
    Recipe,
    Tag,
    Ingredient,
)


class IngredientSerializer(serializers.ModelSerializer):   # need to be defined before recipe serializer
    """Serializer for ingredients."""

    class Meta:
        model = Ingredient  # telling w/c model to represent
        fields = ['id', 'name']  # fields of the model that we wanna control or atleast view through the serializer
        read_only_fields = ['id']  # => we can't change the id field


# We first move thetag serilizer above the recipe serializer bcz we nee to assign the tag serializer as a nested serializer to our recipe serializer. defing tag serializer at the bottom of the file won't work bcz we try and referenceit before it is actually been assigned
# now we can use this tag serlzr as a nested serlzr to our recipe serlzr
class TagSerializer(serializers.ModelSerializer):  # we will have a list of tags assigned to our recipe
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']     # these are the fields that we want to co nvert from our model to our serializer.
        read_only_fields = ['id']  # we don't want them to be able to modify the ID , we just want to view it. Now set views in views.py

# Define serializer for recipe objects.
class RecipeSerializer(serializers.ModelSerializer):   # we'll use model serlzr. bcz this serlzr will represent a specific model in the system w/c is our recipe model.
    """Serializer for recipes."""
    tags = TagSerializer(many = True, required = False)  # We make tags an optional part of our recipe but we can provide them if we want, many =true bcz this will be a list of items

    class Meta:  # We need to set the model.
        model = Recipe  # tells DRF that we'll use Recipe model with this serializer
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags']   # list all the fields that we want to use with this serializer.
        read_only_fields = ['id']   # bcz we don't want them to change the db id of a recipe. we only want them to be able to change the other fields that we'he listed in fields.
# rerun the test it'll still fail but the reason => no reverse match bcz we haven't added the URL for the recipe endpt.
# Before we add the URL , we will crete a view bcz u need to have view before u configure your app to point to it. After this open views.py created inside recipe app.

    def _get_or_create_tags(self, tags, recipe):  # refactpring the code to reduce duplication b/w create and update method.
        """Handle getting or creating tags as needed."""     # took auth user out of create to ensure that any new tags are assigned to the correct user that is authenticated.
        auth_user = self.context['request'].user  # gets the authenticated user , we r using self.context request bcz we r doing this in a serializer and not the view. The context is passed to the serializer by the view when u r using the serializer for that particular view. That's a way to get the context of the request from the actual serializer code.
        # took this functionality out of create bcz we need this for both updating and creating
        for tag in tags:  # looping through all of the tags that we popped from the validated data and gets all of the tags if they exist or creates them and add if they don't exist.
            tag_obj, created = Tag.objects.get_or_create(  # helper method available for your model manager, gets the value if it already exists or if it doesn't exist then it creates a value with the values that we pass in, Giving us a functionality not to create duplicate tags in the system
                user=auth_user,
                **tag,  # we could write name = tag['name], but we put ** as we want to remove or take all of the values that are passed into the tag to ensure if we add any additional functionality to our tag in future, so the fields to the tag will be supported w/o having to modify the code here. run test and it passes.
            )
            recipe.tags.add(tag_obj)

    # add feature to be able to create them by adding some custom logic to RecipeSerializer class by adding new method to the class that allows us to override the behaviour of the create functionality
    def create(self, validated_data):  # custom logic that we add to create recipes via the serializer
        """Create a recipe."""
        tags = validated_data.pop('tags', [])  #  getting all th etags here, => remove the tags object from the validated data and assign it to the tags variable here(get would do the same except that it would keep the tags inside validate data, but we wanna remove it if it exists.)
        # We r using pop bcz we want to ensure we remove the tags before we create recipe using []
        #  if tags exist in validated data, we remove validated data and assign it to new variable called tags, and if it doesn't exist we will defualt this empty list => [] as written in tags
        # after removing tags, with rest of the validated data, we'll create a new recipe
    # Added the feature to create new tags in the system when we create recipes.
        recipe = Recipe.objects.create(**validated_data)   # creating the recipe that needs to be created
        # auth_user = self.context['request'].user  # gets the authenticated user , we r using self.context request bcz we r doing this in a serializer and not the view. The context is passed to the serializer by the view when u r using the serializer for that particular view. That's a way to get the context of the request from the actual serializer code.
        # for tag in tags:  # looping through all of the tags that we popped from the validated data
        #     tag_obj, created = Tag.objects.get_or_create(  # helper method available for your model manager, gets the value if it already exists or if it doesn't exist then it creates a value with the values that we pass in, Giving us a functionality not to create duplicate tags in the system
        #         user=auth_user,
        #         **tag,  # we could write name = tag['name], but we put ** as we want to remove or take all of the values that are passed into the tag to ensure if we add any additional functionality to our tag in future, so the fields to the tag will be supported w/o having to modify the code here. run test and it passes.
        #     )
        #     recipe.tags.add(tag_obj)  # the above commented code is shifted to _get_or_create_tags method above.
        self._get_or_create_tags(tags, recipe)   # either creating or assigning tags as needed.
        return recipe
    # Abstracted the feature to get or create tags into a separate method and for create we call that method


    def update(self, instance, validated_data):  # same as create method except that u get the instance as well. So we an insatnce an validsated data that we want to update as parameters        """Update recipe."""
        tags = validated_data.pop('tags', None)  # getting the tags and if there is no tag provide none(=>we get None as default)
        if tags is not None:   # if tags was an empty list, then it would be assigned as an empty list in above line tags. (an empty list is not the same as none)
            instance.tags.clear()  # clears the existing tags that are assigned. [An empty list is not none, so it supports the ability to be able to clear all of the tags that are assinged to the recipe.]
            self._get_or_create_tags(tags, instance)  # if they provide an empty list, then noneed to create any tags and for loop won't be executed and u won't have any tags.

        for attr, value in validated_data.items():  # THisi srest of the validated data, everything outside of the tag, nested value, we r jst going to assign to our instance here
            setattr(instance, attr, value)   # takes an instance and assigns the attribute, the value that is provided here

        instance.save()   # saves all the updates chnages to the instance
        return instance   # returning the instance from the update method.  run the test and check it passes.

class RecipeDetailSerializer(RecipeSerializer):  # using RecipeSerializer as the base class bcz the detail serializer will be and extension of RecipeSerializer, so we want to take allthe functionality of Rec.Serlzr. and add some extra fields for detail serializer. Thus we can aviod duplicatimg the code where we define the model and all of different fields.
    """Serializer for recipe detail view."""

    class Meta(RecipeSerializer.Meta):  # passing the meta class to that we get all meta values that were provided to the recipe serializer.
        fields = RecipeSerializer.Meta.fields + ['description']
# now create view open views.py
