"""
Tests for models.
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


# lctr 91 => First we convert our new tag model instance to a string representation af follows. This is just a helper func. to create a test user that we can use to assign to our tag.
def create_user(email = 'user@example.com', password = 'testpass123'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email = email,
            password = password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))  #  glt indent krne se error aa rhi thi.

    def test_new_user_email_normalized(self):
        """Test email is normalised for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test creating a recipe is successful."""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )
        recipe = models.Recipe.objects.create(
        user = user,
        title = 'Sample recipe name',
        time_minutes = 5,
        price = Decimal('5.50'),
        description = 'Sample recipe description.',
        )

        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test creating a tag is successful."""
        user = create_user()  # We create a user that we can assign to the tag.
        tag = models.Tag.objects.create(user=user, name='Tag1')  # Then we create a new tag instance, we can the user to it and then name tag1

        self.assertEqual(str(tag), tag.name)   # Then we check when we convert the tag instance to a string using the str built in function, it converts the tag.name.
# So the above will test 2 things -> we have correct string representation set up for model instances 2. we can simply create new tag instance bcz if we can't create them, we'll get error.
# run test and fails bcz we haven't created new tag class inside our models, =>attribute error. Then open models.py in core app.

    def test_create_ingredient(self):  # creating a test user.
        """Test creating an ingredient is successful."""
        user = create_user()
        ingredient = models.Ingredient.objects.create(   # adding an ingredient
            user=user,
            name='Ingredient1'
        )

        self.assertEqual(str(ingredient), ingredient.name)  # checking if we convert that ingredients object to a string, it returns the name.  run the test to ensure it fails.