import os
import tweepy

def lambda_handler(event, context, tweet='Hello World!'):
    print("Get Credentials")
    try:
        consumer_key = os.environ.get("CONSUMER_KEY")
        consumer_secret = os.environ.get("CONSUMER_SECRET")
        access_token = os.environ.get("ACCESS_TOKEN")
        access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
    except Exception as e:
        print("Error getting credentials: {}".format(e))
        raise e

    print("Authenticate")
    try:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
    except Exception as e:
        print("Error authenticating: {}".format(e))
        raise e

    print("post tweet: {tweet}")
    try:
        api.update_status(tweet)
    except Exception as e:
        print("Error tweeting: {}".format(e))
        raise e

    return {
        'statusCode': 200,
        'tweet': tweet
    }
