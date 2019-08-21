# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import boto3
import personalizeAPI
from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import loader
from django.db import connection

from .models import User, Reviews, Movies

# Drop-down model options
MODEL_DROPDOWN_NONE_SORT = -1
MODEL_SELECTED = 'selected'
model1Options = []
model2Options = []

#-----
# Callback handler to display dataset details
#-----
def userDetail(request, user):
    personalize = personalizeAPI.getPersonalizeApi(personalizeAPI.API_RUNTIME)
    nextUser = user
    try:
        userData = get_object_or_404(User, pk=nextUser)
    except:
        nextUser = 1
        userData = get_object_or_404(User, pk=nextUser)

    # Start by seeing if we're refreshing the trained models
    refreshModels = request.POST.get('refreshModels', False)
    if (refreshModels):
        # Generate metrics and modesl from Personalize, then act like we've done a reset
        personalizeAPI.createModelMetrics()
        request.session['reset'] = 'on'
    
    # If we've come from the main screen then treat it like changing
    # op-mode, as otherwise model dropdowns might retain invalid options
    try:
        reset = request.session['reset']
        opMode = request.session['mode']
        del request.session['reset']
    except:
        # Nope, so read the op-mode from the session
        opMode = request.POST.get('opMode', False)
        
    # Pick out all of the other possible POST parameters
    showReviewsToggle = request.POST.get('showReviewsToggle', False)
    genreChoice = request.POST.get('top25Genre', 'all')
    simsNextMovie = request.POST.get('simsNextMovieID', False)
    simsRerank = request.POST.get('enableReranking', False)
    model1Choice = request.POST.get('model1Dropdown', False)
    model2Choice = request.POST.get('model2Dropdown', False)

    # Process based upon what was selected
    if (opMode):
        request.session['mode'] = opMode
        # Clear the model drop-down and selected item, as we've changed mode
        del model1Options[:]
        del model2Options[:]
        request.session['model1Choice'] = MODEL_DROPDOWN_NONE_SORT
        request.session['model2Choice'] = MODEL_DROPDOWN_NONE_SORT
        request.session['rankGenre'] = genreChoice
        
        # If we're switching to SIMS then start with their top film
        if (opMode == "sims"):
            with connection.cursor() as cursor:
                cursor.execute("select movie_id from recommend_reviews where user_id=%s order by rating desc, id asc limit 1", [nextUser])
                for index, rev in enumerate(cursor.fetchall()):
                    request.session['simsItem'] = ('%s' % rev[0])
    else:
        # Not changing mode, so other options are not mutually exclusive
        if (simsRerank):
            # Changing how we re-rank
            request.session['sims_ranking'] = simsRerank
            simsNextMovie = request.POST.get('simsNextMovieModeToggle', False)
        if (showReviewsToggle):
            request.session['showReviewsDataset'] = showReviewsToggle
        if (genreChoice):
            # Just store our new selected re-ranking genre
            request.session['rankGenre'] = genreChoice
        if (model1Choice):
            # Changed the model, so need to re-genenerate the dropdown
            # from scratch to keep the selected option
            request.session['model1Choice'] = model1Choice
            del model1Options[:]
            populateModelDropdown(request.session['mode'], model1Options, model1Choice)
        if (model2Choice):
            # Changed the model, so need to re-genenerate the dropdown
            # from scratch to keep the selected option
            request.session['model2Choice'] = model2Choice
            del model2Options[:]
            populateModelDropdown(request.session['mode'], model2Options, model2Choice)

    # Pick off session variables as needed to see what we need to generate
    showReviewsDataset = request.session['showReviewsDataset']
    model1Choice = request.session['model1Choice']
    model2Choice = request.session['model2Choice']

    simsBaseMovie = request.session['simsItem']
    if (simsNextMovie == False):
        simsNextMovie = simsBaseMovie
    selected_rank_genre = request.session['rankGenre']
    simsRerankList = request.session['sims_ranking']
    demo_mode = request.session['mode']

    # If we have no model drop-downs defined then we need to create them
    if (len(model1Options) == 0):
        populateModelDropdown(demo_mode, model1Options, model1Choice)
        populateModelDropdown(demo_mode, model2Options, model2Choice)

    # Clear all our result lists
    datasetUserReviews = []     # User's top-25 reviews
    model1PersonalizeList = []  # Results from Personalize Model 1
    model1PersonalizeTitle = [] # Title for the segment on screen for Model 1 results
    model2PersonalizeList = []  # Results from Personalize Model 2
    model2PersonalizeTitle = [] # Title for the segment on screen for Model 2 results
    review_info = []            # User's movie review statistics summary
    popularGenreFilms = []  # Selected genre's top-25 movies
    popularRankedList = []  # User's personalized ranking of top-25
    simsMovieList = []      # SIMS item recommendations (23, as need two slots)
    simsOrderingDisabled = True    # Disable SIMS ordering if there are no RANKING algorithms

    # Get the user's rough review summary    
    reviews_list = Reviews.objects.filter(user_id=nextUser)
    if reviews_list:
        num_reviews = len(reviews_list)
        with connection.cursor() as cursor:
            cursor.execute("select count(rating) as count from recommend_reviews where user_id=%s group by rating order by rating desc", [nextUser])
            for index, rev in enumerate(cursor.fetchall()):
                review_info.append("%s* = %.1f%% (%s reviews)" % (5-index, (100.0 * int(rev[0])/num_reviews), int(rev[0])))
                
    # Load up their top-25 films.  Build up list
    # based upon the formats from Personalize
    if (showReviewsDataset == 'on'):
        top25array = {}
        with connection.cursor() as cursor:
            top25list = []
            cursor.execute("select movie_id from recommend_reviews where user_id=%s order by rating desc, id asc limit 25", [nextUser])
            for index, rev in enumerate(cursor.fetchall()):
                nextTuple = {}
                nextTuple['itemId'] = ('%s' % rev[0])
                top25list.append(nextTuple)
            top25array['itemList'] = top25list
        datasetUserReviews = buildFilmContext(top25array, 'itemList', nextUser, True, False)

    #------
    # RECOMMEND mode needs multiple potential lists of films
    #------
    if (demo_mode == "recommend"):
        # Get the results for Model 1 (if any)
        if (int(model1Choice) != MODEL_DROPDOWN_NONE_SORT):
            model1Details = personalizeAPI.getModelForSelection(demo_mode, model1Choice)
            response = personalize.get_recommendations(campaignArn=model1Details[personalizeAPI.MODEL_ARN], userId=nextUser)
            model1PersonalizeList = buildFilmContext(response, 'itemList', nextUser, False, False)
            model1PersonalizeTitle = "Personalization: " + model1Details[personalizeAPI.MODEL_NAME]
            
        # Get the results for Model 2 (if any)
        if (int(model2Choice) != MODEL_DROPDOWN_NONE_SORT):
            model2Details = personalizeAPI.getModelForSelection(demo_mode, model2Choice)
            response = personalize.get_recommendations(campaignArn=model2Details[personalizeAPI.MODEL_ARN], userId=nextUser)
            model2PersonalizeList = buildFilmContext(response, 'itemList', nextUser, False, False)
            model2PersonalizeTitle = "Personalization: " + model2Details[personalizeAPI.MODEL_NAME]

    #------
    # RANKING mode needs to source a top-25 list, then get the personalized variation
    #------
    elif (demo_mode == "ranking"):
        # Need the rankings no matter what, as we always show them
        baseRankings = getRankingFilms(selected_rank_genre)
        popularGenreFilms = buildFilmContext(baseRankings, 'itemList', nextUser, False, False)
        
        # Get the results for Model 1 (if any)
        if (int(model1Choice) != MODEL_DROPDOWN_NONE_SORT):
            # Extract useful info from the popular array above
            popularFilmsArray = []
            for filmEntry in baseRankings['itemList']:
                popularFilmsArray.append(filmEntry['itemId'])

            # Get model details and re-rank accordingly
            model1Details = personalizeAPI.getModelForSelection(demo_mode, model1Choice)
            response = personalize.personalize_ranking(campaignArn=model1Details[personalizeAPI.MODEL_ARN], inputList=popularFilmsArray, userId=nextUser)
            model1PersonalizeList = buildFilmContext(response, 'personalizedRanking', nextUser, False, False)
            model1PersonalizeTitle = "Rankings: " + model1Details[personalizeAPI.MODEL_NAME]
            
    #------
    # SIMS mode wants current selection, plus placeholder, plus 23 SIM entries
    # Note, we'll optinally re-rank for the user and show this list in order.  Also,
    # (simsNextMovie != simsBaseMovie) => we've just clicked on simsNextMovie
    #------
    elif (demo_mode == "sims"):
        # Check if we can re-order before we start
        rankingARN = personalizeAPI.getArbitraryRankingARN()
        simsOrderingDisabled = (rankingARN == "")

        # Get the results for Model 1 (if any)
        if (int(model1Choice) != MODEL_DROPDOWN_NONE_SORT):
            
            # Get the list of similar-item responses
            model1Details = personalizeAPI.getModelForSelection(demo_mode, model1Choice)
            response = personalize.get_recommendations(campaignArn=model1Details[personalizeAPI.MODEL_ARN], itemId=simsNextMovie)
            topItemName = 'itemList'
            
            # Re-rank that list if we've been asked to
            if (simsRerankList == 'on'):
                similarFilmList = []
                for filmEntry in response['itemList']:
                    similarFilmList.append(filmEntry['itemId'])
                response = personalize.personalize_ranking(campaignArn=rankingARN, inputList=similarFilmList, userId=nextUser)
                topItemName = 'personalizedRanking'
            model1PersonalizeList = buildFilmContext(response, topItemName, nextUser, False, simsNextMovie)
            model1PersonalizeTitle = "Similar Items: " + model1Details[personalizeAPI.MODEL_NAME]
        
    # Build up the full data context for the view_detail.html view
    context = {
        'userid': nextUser,
        'age': userData.age,
        'gender': userData.gender,
        'occupation': userData.occupation,
        'demo_mode': demo_mode,
        'review_list': review_info,
        'movie_list': datasetUserReviews,
        'ranking_genre': selected_rank_genre,
        'most_popular_films': popularGenreFilms,
        'sims_base_movie': simsBaseMovie,
        'sims_ranking': simsRerankList,
        'sims_next_movie': simsNextMovie,
        'simsOrderingDisabled': simsOrderingDisabled,
        'showReviewsDataset': showReviewsDataset,
        'modelDropdown1': model1Options,
        'model1PersonalizeList': model1PersonalizeList,
        'model1PersonalizeTitle': model1PersonalizeTitle,
        'modelDropdown2': model2Options,
        'model2PersonalizeList': model2PersonalizeList,
        'model2PersonalizeTitle': model2PersonalizeTitle,
    }
    return render(request, 'recommend/view_detail.html', context)

#---
# Populate the model dropdown.  Django doesn't allow conditional 'selected' based
# upon two variables, so need to send a 'selected' string with each entry
#---
def populateModelDropdown(currentOpMode, dropdown, selected):
    # Always start our model drop-downs with 'None'
    noneEntry = {}
    noneEntry[personalizeAPI.MODEL_NAME] = "No Model Selected"
    noneEntry[personalizeAPI.MODEL_SORT] = MODEL_DROPDOWN_NONE_SORT
    if (selected == MODEL_DROPDOWN_NONE_SORT):
        noneEntry[MODEL_SELECTED] = "selected"
    else:
        noneEntry[MODEL_SELECTED] = ""
    dropdown.append(noneEntry)
    
    # Get models for our current mode and add them all in that order
    modelList = personalizeAPI.getModelsForMode(currentOpMode)
    for model in modelList:
        nextEntry = {}
        nextEntry[personalizeAPI.MODEL_NAME] = model[personalizeAPI.MODEL_NAME]
        nextEntry[personalizeAPI.MODEL_SORT] = model[personalizeAPI.MODEL_SORT]
        if (int(selected) == int(model[personalizeAPI.MODEL_SORT])):
            nextEntry[MODEL_SELECTED] = "selected"
        else:
            nextEntry[MODEL_SELECTED] = ""
        dropdown.append(nextEntry)

#-----
# Builds up a data context for a list of movie IDs.  Optionally will add on a
# user's rating for this film, but they only exist in the review dataset
#-----
def buildFilmContext(sourceList, listTopEntryName, nextUser, addRating, simsPrefix):
    
    filmDetails = []
    if (simsPrefix):
        # First, add on the sims film base
        thisFilm = {}
        nextMovie = Movies.objects.get(movie_id=simsPrefix)
        thisFilm['title'] = nextMovie.title
        thisFilm['year'] = nextMovie.year
        thisFilm['genre'] = nextMovie.generateGenre()
        thisFilm['poster'] = nextMovie.image_url
        thisFilm['movieID'] = simsPrefix
        thisFilm['noSimsLink'] = True
        filmDetails.append(thisFilm)
        # Then add on the "If you liked this, then..." image
        thisFilm = {}
        thisFilm['title'] = ""
        thisFilm['year'] = " "
        thisFilm['genre'] = ""
        thisFilm['poster'] = "/static/recommend/images/alsolike.png"
        thisFilm['movieID'] = simsPrefix
        thisFilm['noSimsLink'] = True
        filmDetails.append(thisFilm)
    
    # Build up details of the supplied film list (max = 25)
    for film in sourceList[listTopEntryName]:
        if (len(filmDetails) >= 25):
            break
        thisFilm = {}
        filmId = int(film['itemId'])
        nextMovie = Movies.objects.get(movie_id=filmId)
        if addRating:
            nextRating = Reviews.objects.get(user_id=nextUser, movie_id=filmId)
            thisFilm['rating'] = nextRating.rating
        thisFilm['title'] = nextMovie.title
        thisFilm['year'] = nextMovie.year
        thisFilm['genre'] = nextMovie.generateGenre()
        thisFilm['poster'] = nextMovie.image_url
        thisFilm['movieID'] = filmId
        thisFilm['noSimsLink'] = not simsPrefix
        filmDetails.append(thisFilm)
    return filmDetails

#----
# Looks up the top-25 rankings per genre from the database.  If the genre
# is set to "all" then we just look up the top-25 from the entire database
#----
def getRankingFilms(genre):
    # Build up the query string first - note that the Personalize
    # dataset only included user-item interactions where rating > 3.5
    queryString = "select movie_id, count(*) as NUM from recommend_reviews where rating > 3.5"
    if (genre != "all"):
        # Insert the inner query with just movie_id's for our genre
        queryString = queryString + "  and movie_id in (select movie_id from recommend_movies where is_" + genre + " is true)"
    queryString = queryString + " GROUP BY movie_id order by NUM desc limit 25"
    
    # Build up an array that matches the responses from Personalize API calls
    top25array = {}
    with connection.cursor() as cursor:
        top25list = []
        cursor.execute(queryString)
        for index, rev in enumerate(cursor.fetchall()):
            nextTuple = {}
            nextTuple['itemId'] = ('%s' % rev[0])
            top25list.append(nextTuple)
        top25array['itemList'] = top25list
    return top25array
