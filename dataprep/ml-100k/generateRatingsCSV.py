import boto3

import json
import numpy as np
import pandas as pd
import time

personalize = boto3.client(service_name='personalize', endpoint_url='https://personalize.us-east-1.amazonaws.com', region_name='us-east-1')
personalize_runtime = boto3.client(service_name='personalize-runtime', endpoint_url='https://personalize-runtime.us-east-1.amazonaws.com', region_name='us-east-1')

bucket = "ak-personalize-demo"                   # replace with the name of your S3 bucket
filename = "top-review-movie-lens-100k.csv"

# read in the raw file
data = pd.read_csv('./u.data', sep='\t', names=['USER_ID', 'ITEM_ID', 'RATING', 'TIMESTAMP'])

# keep only movies rated 3.6 and above
data = data[data['RATING'] > 3.6]

# select columns that match the columns in the Personalization schema
data = data[['USER_ID', 'ITEM_ID', 'TIMESTAMP']]

# reviews are 20th Sep 97 - 23rd Apr 98 - these are old, and break the SIMS
# models, so shift all the ranges to 19th Aug 29 - 1st Apr 19
data['TIMESTAMP'] = data['TIMESTAMP'] + 660833618

# Output the data-frame to a CSV and upload to the bucket
data.to_csv(filename, index=False)
boto3.Session().resource('s3').Bucket(bucket).Object(filename).upload_file(filename)
