"""
Tests for the ingredients API.
"""
from django.contrib.auth import get_user_model  # to get the model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status     # for checking the status code
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')  # URL of API that we r testing


def create_user(email='user@example.com', password='testpass123'):   # helper funtion to create a user
    """Create and return user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicIngredientsApiTests(TestCase):  # Tests that authentication is required for the endpt.
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving ingredients."""
        res = self.client.get(INGREDIENTS_URL)  ,   # we r making a request to the endpt. before we r authenticated  and checking it returns unauthorised response.

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving a list of ingredients."""
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Vanilla')

        res = self.client.get(INGREDIENTS_URL)   # URL to imgredeints api

        ingredients = Ingredient.objects.all().order_by('-name')  # retrieve the ingredients from the db and for evry test run, db is entirely refreshed, can pass it to the serializer and can use it to validate that the API is returning correct result
        serializer = IngredientSerializer(ingredients, many=True)  # passing in all the ingredients that we returned from above line and passing many = true to say that we want to serialize many different items instead of a single item.
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test list of ingredients is limited to authenticated user."""
        user2 = create_user(email='user2@example.com')   # creating new user w/c is unauthenticated and an ingredient for that user and we'll use that for the test.
        Ingredient.objects.create(user=user2, name='Salt')
        ingredient = Ingredient.objects.create(user=self.user, name='Pepper')  #creating another user w/c i s assigned to the authenticated user

        res = self.client.get(INGREDIENTS_URL)   # calling the get method to do HTTP get on the ingredients URL to  get a list of all the ingredients for the authenticated user

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)  # checking that the length of result was 1. Since we created two different ingredients but only one was assigned to the authenticated user, we would expect only one to be returned
        self.assertEqual(res.data[0]['name'], ingredient.name)   # checking that it's not returning the ingredient linked to another user. Now runthe test and it fails for inmgredient serializer not found.
        self.assertEqual(res.data[0]['id'], ingredient.id)