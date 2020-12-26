# twitter_client

twitter_client is a batch application which will get you 10 most recent Tweets with a chosen hashtag using Twitter API. It will get Tweet text and Tweet ID and write it to a Redis database.

There's Flask API created to use this batch application, by posting chosen hashtags and getting Tweets with it - **https://github.com/jstefanska/flask_api**

## Redis database and environment variables

First you need Redis database using e.g. Docker. Here you can find Dockerfile and Redis config with authorization password I used: https://github.com/jstefanska/flask_api/tree/master/Redis Then you need to create environment variables on your system, otherwise API won't work.
It should be the same database you're using for https://github.com/jstefanska/flask_api

For Redis, you need **DB_PORT**, **DB_HOST** and **DB_PASS**.

You also need API key and API secrted for Twitter API - for that you need to create a project in Twitter API.
Environment variables should be named **API_KEY** and **API_SECRET**.

## Openshift

This batch application is designed to run on Openshift, so you can run twitter_client as cron job in Openshift: https://github.com/jstefanska/twitter_client/blob/master/Openshift/twitter-client-job-cron.yaml

twitter_client will always get 10 most recent Tweets with provided hashtag. Popular option is currently not available due to issues on Twitter API side.
