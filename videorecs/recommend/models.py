# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

# Create your models here.

@python_2_unicode_compatible  # only if you need to support Python 2
class User(models.Model):
    # Field helpers
    MALE = 'M'
    FEMALE = 'F'
    GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    )

    # Field definitions
    forename = models.CharField(max_length=32, blank=True)
    surname = models.CharField(max_length=32, blank=True)
    age = models.IntegerField(default=0)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default=MALE)
    occupation = models.CharField(max_length=32, blank=True)
    zipcode = models.CharField(max_length=10, blank=True)

    # Return self identifier
    def __str__(self):
        return self.id

    # Returns if user is Male
    def isMale(self):
        return self.gender == MALE

    # Returns if user is Female
    def isFemale(self):
        return self.gender == FEMALE


@python_2_unicode_compatible  # only if you need to support Python 2
class Reviews(models.Model):

    # Field definitions
    user_id = models.IntegerField(blank=False)
    movie_id = models.IntegerField(blank=False)
    rating = models.IntegerField(blank=False)
    timestamp = models.PositiveIntegerField(blank=False, default=0)

    # Return self identifier
    def __str__(self):
        return self.id


@python_2_unicode_compatible  # only if you need to support Python 2
class Movies(models.Model):

    # Field definitions
    movie_id = models.IntegerField(default=0, blank=False)
    title = models.CharField(max_length=256, blank=True)
    year = models.IntegerField(default=0, blank=True)
    image_url = models.CharField(max_length=256, blank=True)
    is_action = models.BooleanField(default=False)
    is_adventure = models.BooleanField(default=False)
    is_animation = models.BooleanField(default=False)
    is_childrens = models.BooleanField(default=False)
    is_comedy = models.BooleanField(default=False)
    is_crime = models.BooleanField(default=False)
    is_documentary = models.BooleanField(default=False)
    is_drama = models.BooleanField(default=False)
    is_fantasy = models.BooleanField(default=False)
    is_filmnoir = models.BooleanField(default=False)
    is_horror = models.BooleanField(default=False)
    is_musical = models.BooleanField(default=False)
    is_mystery = models.BooleanField(default=False)
    is_romance = models.BooleanField(default=False)
    is_scifi = models.BooleanField(default=False)
    is_thriller = models.BooleanField(default=False)
    is_war = models.BooleanField(default=False)
    is_western = models.BooleanField(default=False)

    # Return self identifier
    def __str__(self):
        return (self.title + ' (' + self.year + ')')

    def appendGenreString(self, existingGenre, flag, textToAdd):
        result = existingGenre
        if flag:
            if (len(existingGenre) > 1):
                result = result + ', '
            result = result + textToAdd
        return result

    # Generate a genre string
    def generateGenre(self):
        genre = '('
        genre = self.appendGenreString(genre, self.is_action, 'Action')
        genre = self.appendGenreString(genre, self.is_adventure, 'Adventure')
        genre = self.appendGenreString(genre, self.is_animation, 'Animation')
        genre = self.appendGenreString(genre, self.is_childrens, 'Children')
        genre = self.appendGenreString(genre, self.is_comedy, 'Comedy')
        genre = self.appendGenreString(genre, self.is_crime, 'Crime')
        genre = self.appendGenreString(genre, self.is_documentary, 'Documentary')
        genre = self.appendGenreString(genre, self.is_drama, 'Drama')
        genre = self.appendGenreString(genre, self.is_fantasy, 'Fantasy')
        genre = self.appendGenreString(genre, self.is_filmnoir, 'FilmNoir')
        genre = self.appendGenreString(genre, self.is_horror, 'Horror')
        genre = self.appendGenreString(genre, self.is_musical, 'Musical')
        genre = self.appendGenreString(genre, self.is_mystery, 'Mystery')
        genre = self.appendGenreString(genre, self.is_romance, 'Romance')
        genre = self.appendGenreString(genre, self.is_scifi, 'Sci-Fi')
        genre = self.appendGenreString(genre, self.is_thriller, 'Thriller')
        genre = self.appendGenreString(genre, self.is_war, 'War')
        genre = self.appendGenreString(genre, self.is_western, 'Western')
        if (len(genre) == 1):
            genre = genre + '<unknown>'
        genre = genre + ')'
        return genre

@python_2_unicode_compatible  # only if you need to support Python 2
class PersonalizeModel(models.Model):
    # Field helpers
    RECOMMEND = 'recommend'
    RANKINGS = 'ranking'
    SIMS = 'sims'
    TYPE_CHOICES = (
        (RECOMMEND, 'Recommendations'),
        (RANKINGS, 'List Re-Ranking'),
        (SIMS, 'Similar Items')
    )

    model_name = models.CharField(max_length=64, blank=False)
    model_arn = models.CharField(max_length=256, blank=False)
    model_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=RECOMMEND)
    model_sort_order = models.IntegerField(default=0)

    def __str__(self):
        return self.model_name
