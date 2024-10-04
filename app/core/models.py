"""
Database models.
"""
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email = self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using = self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using = self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length = 255, unique = True)
    name = models.CharField(max_length = 255)
    is_active = models.BooleanField(default = True)
    is_staff = models.BooleanField(default = False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Recipe(models.Model):
    """Recipe object."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
    )
    title = models.CharField(max_length = 255)
    description = models.TextField(blank = True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits = 5, decimal_places = 2)
    link = models.CharField(max_length = 255, blank = True)
    tags = models.ManyToManyField('Tag')  #bcz we can have many different recipes that have many different tags.
    ingredients = models.ManyToManyField('Ingredient')
# Any of our tags can be associated to any of our recipes and any of our recipes can be associated to any of our tags. run the test fails bcz we haven't created mgrations change yet. Creates model Tag 2. Adds field tags to recipe model that already existed. 0003 new migration file generated.

    def __str__(self):
        return self.title


class Tag(models.Model):    # primary usage of the tag is filtering mechanism so that you can tag your recipes and can filter by different tags.
    """Tag for filtering recipes."""
    name = models.CharField(max_length=255)  # name of the tag
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,  # if the user is deleted the tags associated will also get deleted
    )

    def __str__(self):
        return self.name  # returns the string representation that we r checking for in our test.
 # we need to add the link to tags from recipe model.

class Ingredient(models.Model):
    """Ingredient for recipes."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name    # run migrations as added a new model : it create model ingredients and added field ingredients to recipe