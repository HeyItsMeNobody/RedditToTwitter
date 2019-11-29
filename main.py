import config
import praw
import sys
import requests
import mimetypes
import tweepy
import time
import os
import redis

def is_url_image(url):
    #pylint: disable=unused-variable
    mimetype,encoding = mimetypes.guess_type(url)
    return (mimetype and mimetype.startswith('image'))

db = redis.Redis(host=config.redis['host'], port=config.redis['port'], db=config.redis['db'])

reddit = praw.Reddit(client_id=config.reddit['account']['clientId'],
                     client_secret=config.reddit['account']['clientSecret'],
                     user_agent=config.userAgent,
                     username=config.reddit['account']['username'],
                     password=config.reddit['account']['password'])

if (reddit.read_only):
    raise ValueError("Reddit is read only!?")

subreddit = reddit.subreddit(config.reddit['subreddit'])

print('--Reddit--')
print(f'Read only: {reddit.read_only}')
print(f'Name: {reddit.user.me().name}')
print(f'Karma: {reddit.user.me().link_karma}')
print(f'Subreddit: {subreddit.display_name}')

tweepyAuth = tweepy.OAuthHandler(config.twitter['account']['consumerKey'], config.twitter['account']['consumerSecret'])
tweepyAuth.set_access_token(config.twitter['account']['accessToken'], config.twitter['account']['accessTokenSecret'])
twitter = tweepy.API(tweepyAuth)

def tweet_image(url, message):
    filename = 'temp.jpg'
    request = requests.get(url, stream=True)
    if request.status_code == 200:
        with open(filename, 'wb') as image:
            for chunk in request:
                image.write(chunk)

        twitter.update_with_media(filename, status=message)
        os.remove(filename)
    else:
        print("Unable to download image")

print('--Twitter--')
print(f'Name: {twitter.me().screen_name}')
print(f'Follower count: {twitter.me().followers_count}')
print('--------')

while True:
    for submission in subreddit.new(limit=config.reddit['maxResults']):
        tempIDS = []
        for id in db.lrange(config.redis['tempcachekey'], 0, -1):
            tempIDS.append(id.decode('UTF-8'))

        print(f'Title: {submission.title}')
        print(f'Score: {submission.score}')
        print(f'ID: {submission.id}')
        print(f'URL: {submission.url}')
        print(f'Permalink: {submission.permalink}')

        # Skip posts that have already been seen
        if f"{submission.id}" in tempIDS:
            print("Already seen!")
            print('--------')
            continue

        print(f'tempIDS: {tempIDS}')
        rpushListLength = db.rpush(config.redis['tempcachekey'], submission.id)
        # Remove first entry when list bigger than maxResults
        print(f'rpushListLength: {rpushListLength}')
        if (rpushListLength > config.reddit['maxResults']):
            print ("Removing last list entry..")
            db.lpop(config.redis['tempcachekey'])

        if (is_url_image(submission.url) != True):
            print(f'URL isn\'t an image!')
        else:
            #tweet_image(submission.url, f'{submission.title} | http://reddit.com{submission.permalink}')
            print('Image tweeted!')

        print('--------')
    time.sleep(config.reddit['checkDelay'])