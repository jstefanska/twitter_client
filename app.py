import base64
import requests
import psycopg2
import os
from datetime import datetime

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
else:
    db_pass = os.getenv('DB_PASS')

try:

    # select posted hashtags from hashtags table in DB
    conn = psycopg2.connect(host='localhost', port=5432, dbname='postgres', user='postgres',
                            password=db_pass)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("select hashtag from hashtags")
    hashtag = cur.fetchall()

    # request Tweets with each selected hashtag
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

        datetime = datetime.now()

        # insert requested Tweets to DB

        twitter_row = [(status['text'], status['id'], x, datetime) for status in tweet_data['statuses']]

        cur.executemany(
            "INSERT INTO public.twitter (tweet_content, tweet_id, hashtag, datetime) VALUES (%s,%s,%s,%s)",
            twitter_row)

    cur.close()
    conn.close()

except psycopg2.OperationalError as e:
    print("Unable to connect to the database!".format(e))
    exit(1)

print("Rows are updated.")
