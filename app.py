import base64
import os
import redis
import requests
import json

# generate bearer token from api_key and api_secret (provided in Twitter API project)
# api_key and api_secret should be set as environment variable for security

if 'API_KEY' not in os.environ:
    print("'API_KEY' environment variable does not exist")
    exit(1)
elif 'API_SECRET' not in os.environ:
    print("'API_SECRET' environment variable does not exist")
    exit(1)
else:
    api_key = os.getenv('API_KEY')
    api_secret = os.getenv('API_SECRET')
    token = '{}:{}'.format(api_key, api_secret).encode('ascii')
    b64_encoded_token = base64.b64encode(token)
    token = b64_encoded_token.decode('ascii')

# check authorization

base_url = 'https://api.twitter.com/'
auth_url = '{}oauth2/token'.format(base_url)

auth_headers = {
    'Authorization': 'Basic {}'.format(token),
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
}

auth_data = {
    'grant_type': 'client_credentials'
}

auth_resp = requests.post(auth_url, headers=auth_headers, data=auth_data)

if auth_resp.status_code == 200:
    auth_resp.json().keys()
    access_token = auth_resp.json()['access_token']
    print("Bearer token accepted.")
else:
    print("Bearer token authorization failed. Check your API key and API secret.")
    exit(1)

# request 10 recent Tweets

if 'DB_PASS' not in os.environ:
    print("'DB_PASS' environment variable does not exist")
    exit(1)
elif 'DB_HOST' not in os.environ:
    print("'DB_HOST' environment variable does not exist")
    exit(1)
elif 'DB_PORT' not in os.environ:
    print("'DB_PORT' environment variable does not exist")
    exit(1)
else:
    db_pass = os.getenv('DB_PASS')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')

class Tweet:
    tweet_content = ""
    tweet_id = ""

    def __init__(self, tweet_id, tweet_content):
        self.tweet_id = tweet_id
        self.tweet_content = tweet_content


try:

    r = redis.StrictRedis(
        host= db_host,
        port=db_port,
        password=db_pass,
        charset="utf-8",
        decode_responses=True)

    hashtag = r.smembers('hashtags')

    if hashtag == set():
        print("No hashtags in the database.")
        exit(1)

    else:
        for x in hashtag:
            search_headers = {
                'Authorization': 'Bearer {}'.format(access_token)
            }

            search_params = {
                'q': ('#%s' % x),
                'result_type': 'recent',
                'count': 10
            }

            search_url = 'https://api.twitter.com/1.1/search/tweets.json'

            search_resp = requests.get(search_url, headers=search_headers, params=search_params)

            tweet_data = search_resp.json()

            for status in tweet_data['statuses']:
                tweet = Tweet(status['id_str'], status['text'])
                tweet_json = str(json.dumps(tweet.__dict__))
                r.lpush(x, tweet_json)

        r.close()
        print('DB updated with new tweets.')
        exit(0)

except Exception as ex:
    print('Error:', ex)
    exit('Failed to connect, terminating.')
