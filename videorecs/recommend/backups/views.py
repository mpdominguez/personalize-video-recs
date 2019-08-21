# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from random import randint

from .models import User

import personalizeAPI

#---
# Main application entry-point
#---
def index(request):
    # Build up a list
    metricData = personalizeAPI.createModelMetrics()

    # Go render the initial page
    context = {'modelMetrics': metricData}
    return render(request, 'recommend/index.html', context)

#---
# Form POST handler - either the RANDOM button or a user search
#---
def selectuser(request):
    # Reset all session variables once we're on the home page.  Note,
    # the 'reset' variable will essentially flush out the model dropdowns
    request.session['reset'] = 'on'
    request.session['mode'] = 'recommend'
    request.session['top25Genre'] = 'all'
    request.session['simsItem'] = '1'
    request.session['simsNextMovieID'] = '0'
    request.session['sims_ranking'] = 'off'
    request.session['showReviewsDataset'] = 'on'
    request.session['model1Choice'] = -1
    request.session['model2Choice'] = -1

    # Extract form parameters
    randomButton = request.POST.get('random', False)

    # If the RANDOM button the pick a random user
    if (randomButton):
        maxid = User.objects.count()
        nextUser = randint(1, maxid)
    # Otherewise jhust go to User 1 (should never happen)
    else:
        nextUser = 1
        
    # Go to the relevant Details page
    return HttpResponseRedirect(reverse('recommend:userDetail', args=(nextUser,)))
