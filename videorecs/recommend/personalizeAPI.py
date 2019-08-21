import boto3
import collections
from .models import PersonalizeModel

# Types of API interface available
API_CONTROL = "control"
API_RUNTIME = "runtime"
API_EVENTS = "events"

MODEL_NAME = "name"
MODEL_ARN = "arn"
MODEL_SORT = "sort"

# Names of the Campaigns that we have built
ARN_REVIEWS = "MovieReviewCampaign"
ARN_GENRE_COMPOUND = "SingleCompoundGenre"
ARN_GENRE_TOP4 = "TopFourGenres"
ARN_DEMOG = "UserDemographics"
ARN_RANKINGS = "personal-ranking-model"
ARN_POPULARITY = "popular-movie-model"
ARN_SIMS = "similar-item-comparisons"

# Clickstream info
CLKSTR_DATASET_GROUP_ARN = "arn:aws:personalize:us-east-1:302460114512:dataset-group/MovieClickstreamDataset"
CLKSTR_EVENT_TRACKER_ARN = "arn:aws:personalize:us-east-1:302460114512:event-tracker/c5e5c81a"
CLKSTR_TRACKING_ID = "1f631706-1633-480f-a8cc-432c35cae938"

personalizeEndpoint = boto3.client('personalize', region_name='us-east-1')
personalizeRuntimEndpoint = boto3.client('personalize-runtime', region_name='us-east-1')
personalizeEventsEndpoint = boto3.client('personalize-events', region_name='us-east-1')
campaignDict = {}
configuredModels = collections.OrderedDict()

#---
# Get the boto3-based endpoint for Personalize
#---
def getPersonalizeApi(apiType):
    # First, make sure all the campaign info is loaded
    if (len(campaignDict) == 0):
        setupCampaignData()
    
    # Return the API endpoint that the caller wants
    if apiType == API_RUNTIME:
        return personalizeRuntimEndpoint
    elif apiType == API_CONTROL:
        return personalizeEndpoint
        
#---
# Build up the campaign dictionary
#---
def setupCampaignData():
    # Manually map our various campaigns into a Dictionary for easy lookup
    campaignDict[ARN_REVIEWS] = "arn:aws:personalize:us-east-1:302460114512:campaign/MovieReviewCampaign"
    campaignDict[ARN_GENRE_COMPOUND] = "arn:aws:personalize:us-east-1:302460114512:campaign/SingleGenreCampaign"
    campaignDict[ARN_GENRE_TOP4] = "arn:aws:personalize:us-east-1:302460114512:campaign/MultipleGenreCampaign"
    campaignDict[ARN_DEMOG] = "arn:aws:personalize:us-east-1:302460114512:campaign/MovieAndDemographicsCampaign"
    campaignDict[ARN_RANKINGS] = "arn:aws:personalize:us-east-1:302460114512:campaign/PersonalRankingCampaign"
    campaignDict[ARN_SIMS] = "arn:aws:personalize:us-east-1:302460114512:campaign/SimilarItems"
    campaignDict[ARN_POPULARITY] = "arn:aws:personalize:us-east-1:302460114512:campaign/popular-movie-model"

def getCampaignARN(modelName):
    return campaignDict[modelName]
    
#---
# Return list of models for a particular op type
#---
def getModelsForMode(opMode):
    if (len(configuredModels) == 0):
        loadConfiguredModels()
    return configuredModels[opMode]

#---
# Returns a specific model the given refernences
#---
def getModelForSelection(opMode, selection):
    modelResult = []
    modelSet = configuredModels[opMode]
    for modelInstance in modelSet:
        if (int(modelInstance[MODEL_SORT]) == int(selection)):
            modelResult = modelInstance

    return modelResult

#---
# SIMS needs a ranking algorithm, but we dont actually care which one, so get the first
#---
def getArbitraryRankingARN():
    resultARN = ""
    modelSet = configuredModels[PersonalizeModel.RANKINGS]
    if (len(modelSet) > 0):
        resultARN = modelSet[0][MODEL_ARN]
        
    return resultARN

#---
# Build up a list of metrics for our loaded models
#---
def createModelMetrics():
    # First, make sure all the campaign info is loaded
    loadConfiguredModels()

    # Loop through each model, and generate the config data
    metricData = []
    for modelType in configuredModels:
        modelSet = configuredModels[modelType]
        for modelInstance in modelSet:
            newMetric = getModelDetails(modelInstance[MODEL_NAME], modelInstance[MODEL_ARN])
            metricData.append(newMetric)

    return metricData

#---
# Load in all configured models
#---
def loadConfiguredModels():
    # Wipe the models to begin with and re-load each type
    configuredModels[PersonalizeModel.RECOMMEND] = loadSingleModelClass(PersonalizeModel.RECOMMEND)
    configuredModels[PersonalizeModel.RANKINGS] = loadSingleModelClass(PersonalizeModel.RANKINGS)
    configuredModels[PersonalizeModel.SIMS] = loadSingleModelClass(PersonalizeModel.SIMS)

    # Finally, load in the old campaign data (for now - delete when it all works!)
    setupCampaignData()

#---
# Load in a campaign config for a single model type
#---
def loadSingleModelClass(modelType):
    modelTypeList = []
    modelList = PersonalizeModel.objects.filter(model_type=modelType).order_by('model_sort_order')
    for singleModel in modelList:
        nextEntry = {}
        nextEntry[MODEL_NAME] = singleModel.model_name
        nextEntry[MODEL_ARN] = singleModel.model_arn
        nextEntry[MODEL_SORT] = singleModel.model_sort_order
        modelTypeList.append(nextEntry)
    return modelTypeList

#---
# Lookup the various metric for the given campaign, returning a title-prefixed dictionary
#---
def getModelDetails(title, campaignName):
    personalize = getPersonalizeApi(API_CONTROL)
    result = {}
    
    # Collect our data
    campaigns = personalize.describe_campaign(campaignArn=campaignName)
    
    solutionVersionArn = campaigns['campaign']['solutionVersionArn']

    # Some older models don't seem to carry through the recipe type
    try:
        recipe = personalize.describe_solution_version(solutionVersionArn=solutionVersionArn)['solutionVersion']['recipeArn']
        # Rip off anything before the '/'
        if (recipe.find('/') != -1):
            recipe = recipe[(recipe.find('/')+1):]
    except:
        recipe = "{preview recipe}"

    # Pick off metrics
    metrics = personalize.get_solution_metrics(solutionVersionArn=solutionVersionArn)
    pAt5 = metrics['metrics']['precision_at_5']
    pAt10 = metrics['metrics']['precision_at_10']
    pAt25 = metrics['metrics']['precision_at_25']

    # Build up the response and return it
    result['title'] = title
    result['recipe'] = recipe
    result['precisionAt5'] = str(pAt5)[0:6]
    result['precisionAt10'] = str(pAt10)[0:6]
    result['precisionAt25'] = str(pAt25)[0:6]
    return result
    