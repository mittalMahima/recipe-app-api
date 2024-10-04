"""
Tests for the tags API.
"""
from django.contrib.auth import get_user_model  # fun. for gettimg user model
from django.urls import reverse  # so that we can configure our URLS that we need to test.
from django.test import TestCase

from rest_framework import status  # status code so that we can have user friendly names for the status codes that we're testing against.
from rest_framework.test import APIClient  # thtas our testing client

from core.models import Tag

from recipe.serializers import TagSerializer  # we will create after we write the test in next lesson.


TAGS_URL = reverse('recipe:tag-list')  # it will do a reverse lookup for the URL that we'll add for the tags API


# A function to get the tags detail URL (we need to provide the id of the tag, so would define it as a function)
def detail_url(tag_id):
    """Create and return a tag detail url."""
    return reverse('recipe:tag-detail', args=[tag_id])



def create_user(email='user@example.com', password='testpass123'):  # we have this function defined for other tests, we can reuse the sam efunc if we really want to avoid code duplication. Better to keep separate bcz sometimes u might want to add some custom code to your function for a specific model.
    """Create and return a sample user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving tags."""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user() # create user
        self.client = APIClient() # create client
        self.client.force_authenticate(self.user) # authenticate the user on the clients or request made to client

    def test_retrieve_tags(self):
        """Test retrieving a list of tags."""
        Tag.objects.create(user=self.user, name='Vegan')  # two sample tags that we'll use to test with
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)  # calling API, making an HTTP request to the tags listing URL

        tags = Tag.objects.all().order_by('-name')  # Check the result, depending on db used, items maybe returned in different order, so to ensure we r db agnostic (different order returned in different versions of same db), we explicitly mention in the test what order we expect to see the API return results.
        serializer = TagSerializer(tags, many=True)  # we'll serialize the result from our query here, setting many=true bcz its not only one object , it will be multiple objects(list of objects.)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)  #so that data of response matches the serializer that we created

    def test_tags_limited_to_user(self):
        """Test list of tags is limited to authenticated user."""
        user2 = create_user(email='user2@example.com')  # created another user
        Tag.objects.create(user=user2, name='Fruity')  # created tag for that user, we don't need to get a reference for this tag, we just wanna ensure that it is created in the db, that's why we don't assiogn it to a variable.
        tag = Tag.objects.create(user=self.user, name='Comfort Food')  # creating another tag for authenticated user

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)
# in the test above we created two tags , one was assigned to a different user, we called the API as the user that we authenticated with (in th esetup above), then we check that when we retrieve the tags=>aucessful 200 response, then we check there's only one result returned bcz we wouldn't expect the first user's tag to be returned bcz we r not authenticated as user, we r authenticated as other user, so we expect to see only one tag returned in the response. Then maybe one tag was returned but we r filtering the wrong user, so check that name and ID mtch the tag that we created for the authenticated user.
# run the test , fails on import TagSerailezer bcz not yet implemented.

    def test_update_tag(self):
        """Test updating a tag."""
        tag = Tag.objects.create(user=self.user, name='After Dinner')  # create tag here

        payload = {'name': 'Dessert'}  # we create a payload that we'll patch to the URL which generat the URL for the tag we created that we want to update
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)  # making request to find the patch to make a HTTP patch request to the URL with the payload that we defined.

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])  # we r checking that the name of the tag after we refreshed from db is now the name that we specified in the payload.(after that it should be renamed to Desert)
# Run the test w/c fails as we haven't implemented the feature yet. => no reverse match.

    def test_delete_tag(self):
        """Test deleting a tag."""
        tag = Tag.objects.create(user=self.user, name='Breakfast')  # Creating a new tag called breakfast

        url = detail_url(tag.id)  # Then getting a detail URL for that tag
        res = self.client.delete(url)  # calling HTTP delete method on that tag

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)  # Checkimg the result is HTTP 204 W/h is defualt response for calling the HTTP delete method.
        tags = Tag.objects.filter(user=self.user)  # retrieving all tags in system assigned to the authenticated user
        self.assertFalse(tags.exists())  # then we r asserting that the result does not exist, tags that exist =False, so there are not tags in the system, this is the case when the tags gets deleted.
        # Run the tes w/c fails bcz HTTP method not supported response=> AssertionError : 405! 204 as expected.