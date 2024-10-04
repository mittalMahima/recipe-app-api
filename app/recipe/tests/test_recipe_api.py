"""
Tests for recipe APIs.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Recipe,
    Tag,  # to import our new Tag model.
)

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)
# We'll have one serializer that has recipe kind of preview that is written in the listing and then we'll have another serializer that adds a few more fields and gives more details about a specific recipe.


RECIPES_URL = reverse('recipe:recipe-list')   #  Gives recipe api thta we can use later on.


# Why defining detail URL as a function when we have the recipes URL  as a variable above? Reason=>we need to pass in the recipe id to the URL. So each detail will be different always conatining the unique id for recipe that we want to test with.
def detail_url(recipe_id):
    """Create and return a recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])  # Used to generate aunique URL for a specific recipes detail endpt.

def create_recipe(user, **params):             #  helper fun. to create a recipe & will bw used to create test recipes w/c we can use with our API.
    """Create and return a sample recipe."""    #  gives dynamic params **params is a dictionary of all params that were passed to create recipe fun.
    defaults = {                             #  Default values if we don't pass any param.
        'title': 'Sample recipe title',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample description',
        'link': 'http://example.com/recipe.pdf',
    }     #  also allows to override if want a change for a test. create a new dict and then call update w/c updates the default values
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_user(**params):  # Additional test => to make creating users in the system a bit easier.
    """Create a return a new user."""
    return get_user_model().objects.create_user(**params)
#  Just like user tests, breaking these to authenticated and unauthenticated (public want)test classes.
class PublicRecipeAPITests(TestCase):   #  Tests public API.
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()    # gives a test client that can be used for test added to this class.

    def test_auth_required(self):     # checks that authenticatoion is required for getting recipes. Allow only logged in user to see their recipes.
        """Test auth is required to call API."""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):   # creating a setup method that creates client and then creates the user and authenticates the client withr that user.
        self.client = APIClient()
        self.user = create_user(email = 'user@example.com', password = 'test123') # additionally added and removed the below 4 lines to refactor the code to make it neater.
        # self.user = get_user_model().objects.create_user(
        #     'user@example.com',
        #     'testpass123',
        # )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes."""
        create_recipe(user=self.user)    #  2 recipes created in db with these below line.
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)   #returns the recipes that were for the user in the system.

        recipes = Recipe.objects.all().order_by('-id')  #  id is incremental, latest recipe at top in db bcz we are retruning in reverse order.
        # pass the recipes that we got to the serializer

        serializer = RecipeSerializer(recipes, many=True)  # serializer created next lesson but used here to compare expected response from API.  WE expect result to match whatever the serializer returns.
        # many= true tells that we want it to pass in a list of items bcz serializer intends to return details w/c is just one item or we can returns list of items.
        self.assertEqual(res.status_code, status.HTTP_200_OK)   # check correct status and then we can check if it returned the correct data.
        # check the data returned matches th edata of al l recipes form serializer.
        self.assertEqual(res.data, serializer.data)   # Want to ensure that res.data that's the data dictionary that was returned in response is equal to serializer.data This is the data dictionary of th eobjects passed through the serializer.

# reason for below test is even though the above test retrieves recipes for users, we don't know whether it would return all the recipes w/c we don't want, we only want to return the recipes forthe authenticated user that's currently logged in.
#we will add receipes for another user and check that they don;t exist in the response
    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user."""
        other_user = create_user(email = 'other@example.com', password = 'test123')  # Additonal to refactor the code commenting below lines.
        # other_user = get_user_model().objects.create_user(
        #     'other@example.com',
        #     'password123',
        # )
        create_recipe(user=other_user)  # recipe of new user that we created.
        create_recipe(user=self.user)   # recipe of the authenticated user that we created in our setup method above.

        res = self.client.get(RECIPES_URL)  # we expect to see only the recipe of authenticated user as we want to filter by authenticated user.

        recipes = Recipe.objects.filter(user=self.user) # filter the recipes just for the authenticated user.
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)  # compare response data with serializer data
        # No worries for the order here bcz we'll return a single recipe in this test
        # Its expected for this test to fail on import error because we imported serializer w/c we will create later on => no module named recipe.serializers.
# Now add the test to the authnticated tests.
    def test_get_recipe_detail(self):
        """Test get recipe detail."""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)  #  serializes the recipe that we r creating above.
        self.assertEqual(res.data, serializer.data)
    # in the above test we create sample recipe, assign it to the user that we use for authentication, then create a detail URL using the Id of the recipe, then call client.call method to get the URL and pass in the recipe that we created to the serializer
    # and this is just one specific recipe, wedon't pass in many = true and then we check the result of our client was the same as the result of  serializer and that the details returned correctly.
    # run the test and get import error.
    # Then open serializers.py to add the serailizer.
    def test_create_recipe(self):
        """Test creating a recipe."""    # We won't use the create recipe helper fun. bcz wholept. of this test is creating a recipe through the API, so we don't want to create a recipe through our test fun that we created just for test purposes. we wanna pass a payload to the API with the contents of a recipe. we wanna ensure that recipe was created successfully and correctly in db.
        payload = {   #  create a dictionart and deine the fields that we want to pass to the API by creating payload variable.
            'title': 'Sample recipe',
            'time_minutes': 30,
            'price': Decimal('5.99'),
        }
        res = self.client.post(RECIPES_URL, payload)  # bcz to create a recipe, u need to jst post it to the recipe URL => /api/recipes/recipe. This will pass in a post request with this payload to this endpt.

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)  # the response that u should return an api after it creates a new object in the system, will include the ID in the response.
        recipe = Recipe.objects.get(id=res.data['id'])  # getting the recipe by the id.
        # retrieve a specific recipe with the id that was returned from the payload.
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)  # get attribute built in func provided by python, allows us to get an argument but w/o actually having to use dot notation
        self.assertEqual(recipe.user, self.user)  #check that user assigned to api matches the user we're aunthenticated with.
        # iterate through the payload with key = name
# in the test above we start by defining a payload(sample payload that we can post to our recipe endpt.)
# then we call client.post to make an HTTP POST request to recipes URL and pass in payload
# then we check the get 201 response w/c is the success response for creating new objects via an api.
# run the test=>integrity error bcz we haven't configured the view to set the authenticated user with recipe.
# bcz we're using model viewsets , most  of the funtionality for creating an object already exists in the code provided to us by DRF. The logic that doesn't exist is to set the object's user to the authenticated user when we create objects in the system.

# Here we add some additional tests.
    def test_partial_update(self):  # When u update the part of an object and not the full object. Ensures that other fields aren't presented to the payload aren't updated as part of this change.
        """Test partial update of a recipe."""
        original_link = 'https://example.com/recipe.pdf'  # Setting the original link as a variable bcz this is specifically meant to ttest the partial update.
        recipe = create_recipe(   # We create a recipe w/c has an authentiacted user.
            user=self.user,
            title='Sample recipe title',
            link=original_link,
        )

        payload = {'title': 'New recipe title'}  # It should jst change the title bzc that is the only field we provided in the payload and not any other fields.
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()   # bcz by default the model is not refreshed bcz django doesn't automatically refresh the fields once you retrieve them.
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)  # checking that user is the original user to ensure that didn't change

    def test_full_update(self):
        """Test full update of recipe."""
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe title',
            link='https://exmaple.com/recipe.pdf',
            description='Sample recipe description.',
        )

        payload = {    # dictionary
            'title': 'New recipe title',
            'link': 'https://example.com/new-recipe.pdf',
            'description': 'New recipe description',
            'time_minutes': 10,
            'price': Decimal('2.50'),
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)  # put method made for a full update of an object, it should put the entire payload that we provided into that object.

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():   # lop through all values in payload and ensure they're set correctly on the recipe. [Ensure the values matches what is assigned to key in the db.]
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)  # we don't expect that to change bcz this needs to be the authenticated user. Check if the user as assigned is correct.
# in above test we created a sample recipe, added a payload

    def test_update_user_returns_error(self):   # once the recipe created in a user's name, its always assigned to that user.
        """Test changing the recipe user results in an error."""
        new_user = create_user(email='user2@example.com', password='test123')
        recipe = create_recipe(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)  # Ensuring that we do not update the user when they call patch with a new user. its more of a security check.
        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe successful."""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)  # default DRF response for a delete =>successful but has no content to return.
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())  # asserts that the recipe no longer exists in the db

    def test_delete_other_users_recipe_error(self):
        """Test trying to delete another users recipe gives error."""
        new_user = create_user(email='user2@example.com', password='test123')
        recipe = create_recipe(user=new_user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())  # security check to ensure that if u try to delete another user's recipe, it won't be allowed.

# Now we'll add some additional test inside test_recipe_api instead of test_tags_api bcz we r going to suppot creating tags directly through our recipe, so when people use API , they'll create new recipes, we allow them to specify tags in that recipe and if those tags don''t exist, we'll create them and assign them to the recipe, and if those tags do exist, we'll assign the existing tags to new recipe that's being created.

    def test_create_recipe_with_new_tags(self):
        """Test creating a recipe with new tags."""
        payload = {       # Setting the payload and then posting it to the recipes API
            'title': 'Thai Prawn Curry',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'tags': [{'name': 'Thai'}, {'name': 'Dinner'}],  # pass a list of objects(list of dictionaries), these are the two tags that'll be created and assigned to the recipe API
        }
        res = self.client.post(RECIPES_URL, payload, format='json')  # we'll post this to the recipes URL, bcz we r providing nested objects, we set th eformat= JSON, to ensure it gets converted to JSON and is successfully posted to the API

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)   # assert that response code is HTTP 201 created w/c we expect when we create new objects
        recipes = Recipe.objects.filter(user=self.user)   # Filtering all the recipes that r currently assigned to the authenticated user
        self.assertEqual(recipes.count(), 1)  # checking the count of those recipes as one
        recipe = recipes[0]   # assign the recipe variable to the first item that was returned in recipes
        self.assertEqual(recipe.tags.count(), 2)  # checking that these are two tags assigned to the new recipe that was created
        for tag in payload['tags']:   # loop through each tags that we expect to be created and check if they exist
            exists = recipe.tags.filter(
                name=tag['name'],   # ensures correct name and user owns the tags
                user=self.user,
            ).exists()
            self.assertTrue(exists)

# when user is creating a new recipe, if they use a tag that already exists in the db, we don't want it to recreate that tag and have a duplicate in the db. we want to reuse that tag and assign that tag to the new recipe that was created.
    def test_create_recipe_with_existing_tags(self):
        """Test creating a recipe with existing tag."""
        tag_indian = Tag.objects.create(user=self.user, name='Indian')
        payload = {    # paylaod for new recipe having two tags in the payload
            'title': 'Pongal',
            'time_minutes': 60,
            'price': Decimal('4.50'),
            'tags': [{'name': 'Indian'}, {'name': 'Breakfast'}],
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)  # We expect 1 recipe to exist
        recipe = recipes[0]  # so we get the first result from the recipes that we returned
        self.assertEqual(recipe.tags.count(), 2)  # there should be two tags associated with that recipe.
        self.assertIn(tag_indian, recipe.tags.all())   # ensures that the spcific tag that we created exists in the tags that were assigned to the recipe. Testing a unique functionality that it actually reassigns the tag to this recipe and not creating a new one.
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)
# run the test and it should fail recipe tag count 0 expected


#  Update tags assigned to a recipe

    def test_create_tag_on_update(self):  # check that if we update a recipe, but provide a different tag that doesn't exist, then we'll create that tag in the system
        """Test create tag when updating a recipe."""
        recipe = create_recipe(user=self.user)  # creates a sample recipe that we can test with

        payload = {'tags': [{'name': 'Lunch'}]}  # creating a payload that can be used to test our request
        url = detail_url(recipe.id)  # generate URL for the detail endpt. for the recipe that we previously created
        res = self.client.patch(url, payload, format='json')  # HTTP PATCH request to the URL, w/c is a paryial update request w/c means we only want to update the values which we provide in the payload.

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='Lunch')  # retrieving the new tag that we expect to be created
        self.assertIn(new_tag, recipe.tags.all())  # checking the new tag that we retrieved exists in the recipe
 # we don't need to call refresh db on recipe instance when using many to many fields bcz when we call recipe tags to all, it will do a separate query and will retrieve all fresh objects for that recipe.

    def test_update_recipe_assign_tag(self):
        """Test assigning an existing tag when updating a recipe."""
        tag_breakfast = Tag.objects.create(user=self.user, name='Breakfast')  #creating a new tag
        recipe = create_recipe(user=self.user)  # creating a recipe assigned to authenticated user
        recipe.tags.add(tag_breakfast)  # adding breakfast tag to the recipe

        tag_lunch = Tag.objects.create(user=self.user, name='Lunch')  # creating another tag
        payload = {'tags': [{'name': 'Lunch'}]}  # creating payload w/c is designed to change the tags of our recipe to lunch
        url = detail_url(recipe.id)  # getting the detail URL for recipe
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())  # checking that the result tag is in the result
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self):  # we'll setup a recipe with a tag and we'll clear those assigned tags in our request
        """Test clearing a recipes tags."""
        tag = Tag.objects.create(user=self.user, name='Dessert')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)

        payload = {'tags': []}  # passing in an ewmpty list for tags
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')  # HTTP patch request to the API. run the test and they fail on

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

# run the test fails as DRF doesn't support writing test for nested fields. We need to override the update method in order to provide this functionality.