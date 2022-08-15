import requests
import json
import os
from dotenv import load_dotenv

from twitterbot import tweet_to_twitter

# wrap in function


def get_epl_scores(date='2022-08-06'):
    """
    Uses API-sports to get the scores of the matches for the given date. Returns a dictionary of match_id: {home_team, home_score, away_team, away_score}

    """
    # get all the ids of a match for a url
    url = "https://v3.football.api-sports.io/fixtures"

    payload = {'league': 39, 'season': 2022, 'date': date}

    headers = {
        'x-rapidapi-key': os.environ.get("RAPIDAPI_KEY"),
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }

    fixtures_response = json.loads(requests.request(
        "GET", url, headers=headers, params=payload).text)

    assert (fixtures_response['errors'] == [])

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

        score_match_dict[fixture] = {'home_team': home_team, 'away_team': away_team,
                                     'home_score': home_score, 'away_score': away_score, 'winner': winner}

    # returns a dictionary of the match id and the teams and score
    return score_match_dict


def get_epl_odds(date='2022-08-06'):
    url = "https://v3.football.api-sports.io/odds"

    payload = {'league': 39, 'season': 2022, 'date': date}

    headers = {
        'x-rapidapi-key': os.environ.get("RAPIDAPI_KEY"),
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }

    odds_response = json.loads(requests.request(
        "GET", url, headers=headers, params=payload).text)

    odds_match_dict = {}
    for match in odds_response['response']:

        assert (match['bookmakers'][0]['bets'][0]['name'] == 'Match Winner')

        odd_dict = {}
        for value in match['bookmakers'][0]['bets'][0]['values']:
            odd_dict[value['odd']] = value['value']

        pred_win = odd_dict[min(odd_dict.keys())]

        odds_match_dict[match['fixture']['id']] = pred_win

    return odds_match_dict


def get_correct_upsets(odds_match_dict, score_match_dict):
    # get lists of correct and incorrect predictions
    correct_ids = []
    upset_ids = []
    for match_id in odds_match_dict.keys():
        if odds_match_dict[match_id] != score_match_dict[match_id]['winner']:
            upset_ids.append(match_id)
        else:
            correct_ids.append(match_id)
    return correct_ids, upset_ids


def create_tweet(correct_ids, upset_ids, score_match_dict, date='2022-08-06'):
    tweet_text = str('#EPL Matches {date}\n\n').format(date=date)
    tweet_text = tweet_text+str("UPSETS: \n")
    for id in upset_ids:
        score_match_dict[id]
        tweet_text = tweet_text+str("{home_team}: {home_score} - {away_team}: {away_score} \n").format(
            home_team=score_match_dict[id]['home_team'],
            home_score=score_match_dict[id]['home_score'],
            away_team=score_match_dict[id]['away_team'],
            away_score=score_match_dict[id]['away_score'])

    tweet_text = tweet_text+str("\n EXPECTED: \n")
    for id in correct_ids:
        score_match_dict[id]
        tweet_text = tweet_text+(str("{home_team}: {home_score} - {away_team}: {away_score} \n").format(
            home_team=score_match_dict[id]['home_team'],
            home_score=score_match_dict[id]['home_score'],
            away_team=score_match_dict[id]['away_team'],
            away_score=score_match_dict[id]['away_score']))

    return tweet_text


if __name__ == "__main__":
    load_dotenv()

    date = "2022-08-06"

    score_match_dict = get_epl_scores()
    odds_match_dict = get_epl_odds()
    correct_ids, upset_ids = get_correct_upsets(
        odds_match_dict, score_match_dict)
    tweet_text = create_tweet(correct_ids, upset_ids, score_match_dict, date)
    tweet_to_twitter(tweet_text, '# EPL scores {date}'.format(date=date))
    print(tweet_text)
