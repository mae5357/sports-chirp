import requests
import json
import os
from dotenv import load_dotenv


# wrap in function
def get_epl_scores(date='2022-08-06'):
    # get all the ids of a match for a url 
    url = "https://v3.football.api-sports.io/fixtures"

    payload={'league':39, 'season':2022, 'date': date}

    headers = {
        'x-rapidapi-key': os.environ.get("RAPIDAPI_KEY"),
    'x-rapidapi-host': 'v3.football.api-sports.io'
    }

    fixtures_response = json.loads(requests.request("GET", url, headers=headers, params=payload).text)

    assert(fixtures_response['errors'] == [])

    score_match_dict = {}
    for match in fixtures_response['response']:
        # get the fixture id
        fixture = match['fixture']['id']
        
        # get the team names
        home_team = match['teams']['home']['name']
        away_team = match['teams']['away']['name']

        # get the score
        home_score = match['score']['fulltime']['home']
        away_score = match['score']['fulltime']['away']

        # who won?
        if home_score > away_score:
            winner = 'Home'
        elif home_score < away_score:
            winner = 'Away'
        else:
            winner = 'Draw'

        score_match_dict[fixture]={'home_team':home_team, 'away_team':away_team, 'home_score':home_score, 'away_score':away_score, 'winner':winner}

    # returns a dictionary of the match id and the teams and score
    return score_match_dict

def get_epl_odds(date='2022-08-06'):
    url = "https://v3.football.api-sports.io/odds"

    payload={'league':39, 'season':2022, 'date': date}

    headers = {
        'x-rapidapi-key': os.environ.get("RAPIDAPI_KEY"),
    'x-rapidapi-host': 'v3.football.api-sports.io'
    }

    odds_response = json.loads(requests.request("GET", url, headers=headers, params=payload).text)


    odds_match_dict = {}
    for match in odds_response['response']:

        assert(match['bookmakers'][0]['bets'][0]['name'] == 'Match Winner')

        odd_dict = {}
        for value in match['bookmakers'][0]['bets'][0]['values']:
            odd_dict[value['odd']] = value['value']

        pred_win = odd_dict[max(odd_dict.keys())]

        odds_match_dict[match['fixture']['id']] = pred_win

    return odds_match_dict

def get_correct_upsets(odds_match_dict,score_match_dict):
    # get lists of correct and incorrect predictions
    correct_ids = []
    upset_ids = []
    for match_id in odds_match_dict.keys():
        if odds_match_dict[match_id]!=score_match_dict[match_id]['winner']:
            upset_ids.append(match_id) 
        else:
            correct_ids.append(match_id)
    return correct_ids, upset_ids

def create_tweet(correct_ids, upset_ids, score_match_dict, date='2022-08-06'):
    tweet_text = str('#EPL Matches {date}\n\n').format(date=date)
    tweet_text=tweet_text+str("UPSETS: \n")
    for id in upset_ids:
        score_match_dict[id]
        tweet_text=tweet_text+str("{home_team}: {home_score} - {away_team}: {away_score} \n").format(
            home_team=score_match_dict[id]['home_team'], 
            home_score=score_match_dict[id]['home_score'], 
            away_team=score_match_dict[id]['away_team'], 
            away_score=score_match_dict[id]['away_score'])

    tweet_text=tweet_text+str("\n EXPECTED: \n")
    for id in correct_ids:
        score_match_dict[id]
        tweet_text=tweet_text+(str("{home_team}: {home_score} - {away_team}: {away_score} \n").format(
            home_team=score_match_dict[id]['home_team'], 
            home_score=score_match_dict[id]['home_score'], 
            away_team=score_match_dict[id]['away_team'], 
            away_score=score_match_dict[id]['away_score']))

    return tweet_text

def tweet_to_twitter(tweet_text):
    from requests_oauthlib import OAuth1Session
    import os
    import json


    # In your terminal please set your environment variables by running the following lines of code.
    # export 'CONSUMER_KEY'='<your_consumer_key>'
    # export 'CONSUMER_SECRET'='<your_consumer_secret>'

    consumer_key =  os.environ.get("TWITTER_CONSUMER_KEY")
    consumer_secret = os.environ.get("TWITTER_CONSUMER_SECRET")

    payload = {"text": tweet_text}

    # Get request token
    request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
    oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

    try:
        fetch_response = oauth.fetch_request_token(request_token_url)
    except ValueError:
        print(
            "There may have been an issue with the consumer_key or consumer_secret you entered."
        )

    resource_owner_key = fetch_response.get("oauth_token")
    resource_owner_secret = fetch_response.get("oauth_token_secret")
    print("Got OAuth token: %s" % resource_owner_key)

    # Get authorization
    base_authorization_url = "https://api.twitter.com/oauth/authorize"
    authorization_url = oauth.authorization_url(base_authorization_url)
    print("Please go here and authorize: %s" % authorization_url)
    verifier = input("Paste the PIN here: ")

    # Get the access token
    access_token_url = "https://api.twitter.com/oauth/access_token"
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=verifier,
    )
    oauth_tokens = oauth.fetch_access_token(access_token_url)

    access_token = oauth_tokens["oauth_token"]
    access_token_secret = oauth_tokens["oauth_token_secret"]

    # Make the request
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )

    # Making the request
    response = oauth.post(
        "https://api.twitter.com/2/tweets",
        json=payload,
    )

    if response.status_code != 201:
        raise Exception(
            "Request returned an error: {} {}".format(response.status_code, response.text)
        )

    print("Response code: {}".format(response.status_code))

    # Saving the response as JSON
    json_response = response.json()
    print(json.dumps(json_response, indent=4, sort_keys=True))

if __name__ == "__main__":
    load_dotenv()

    date = "2022-08-06"

    score_match_dict = get_epl_scores()
    odds_match_dict = get_epl_odds()
    correct_ids, upset_ids = get_correct_upsets(odds_match_dict,score_match_dict)
    tweet_text = create_tweet(correct_ids, upset_ids, score_match_dict, date)
    tweet_to_twitter(tweet_text)
    print(tweet_text)

