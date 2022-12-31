import os
import tweepy
import datetime
from .src.lib.mlb_scores import *


def make_tweet():
    """
    Make a tweet of yesterday's MLB results
    """
    load_dotenv()

    yesterday_date = (datetime.date.today() -
                      datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    score_match_dict = get_mlb_scores(yesterday_date)

    if score_match_dict == False:
        return False
    else:
        score_match_dict = get_mlb_scores(yesterday_date)
        odds_match_dict = get_mlb_odds(score_match_dict, yesterday_date)
        correct_ids, upset_ids = get_correct_upsets(
            odds_match_dict, score_match_dict)
        tweet_list = create_tweet(correct_ids, upset_ids,
                                  score_match_dict, yesterday_date)

    for tweet in tweet_list:
        print(tweet)
    return tweet_list


def lambda_handler(event, context, tweet='Hello World!'):
    print("Get tweet")
    tweet_list = make_tweet()

    if tweet_list == False:
        print("No games yesterday. No need to tweet.")
    else:
        for tweet in tweet_list:
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

            print("Post tweet: {tweet}".format(tweet=tweet))
            try:
                api.update_status(tweet)
            except Exception as e:
                print("Error tweeting: {}".format(e))
                raise e

            return {
                'statusCode': 200,
                'tweet': tweet
            }
