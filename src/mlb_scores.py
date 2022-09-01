import requests
import json
import os
from dotenv import load_dotenv


def get_mlb_scores(date='2022-08-11'):

    # get all the ids of a match for a url
    url = "https://v1.baseball.api-sports.io/games"

    payload = {'league': 1, 'season': 2022, 'date': date}

    headers = {
        'x-rapidapi-key': os.environ.get("RAPIDAPI_KEY"),
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }

    game_response = json.loads(requests.request(
        "GET", url, headers=headers, params=payload).text)

    try:
        assert (game_response['errors'] == [])
        print('Connected to MLB API')
    except:
        print("Error: "+str(game_response['errors']))

    score_match_dict = {}
    for match in game_response['response']:
        # get the fixture id
        game = match['id']

        # get the team names (there are two teams with "soxs" in the name)")
        if match['teams']['home']['name'] == 'Boston Red Sox':
            home_team = 'Red Sox'
        elif match['teams']['home']['name'] == 'Chicago White Sox':
            home_team = 'White Sox'
        else:
            home_team = match['teams']['home']['name'].split()[-1]

        if match['teams']['away']['name'] == 'Boston Red Sox':
            away_team = 'Red Sox'
        elif match['teams']['away']['name'] == 'Chicago White Sox':
            away_team = 'White Sox'
        else:
            away_team = match['teams']['away']['name'].split()[-1]

        # get the score
        home_score = match['scores']['home']['total']
        away_score = match['scores']['away']['total']

        # who won?
        if home_score > away_score:
            winner = 'Home'
        elif home_score < away_score:
            winner = 'Away'
        else:
            winner = 'Draw'

        score_match_dict[game] = {'home_team': home_team, 'away_team': away_team,
                                  'home_score': home_score, 'away_score': away_score, 'winner': winner}

    return score_match_dict


def get_mlb_odds(score_match_dict, date='2022-08-11'):
    url = "https://v1.baseball.api-sports.io/odds"

    payload = {'league': 1, 'season': 2022}

    headers = {
        'x-rapidapi-key': os.environ.get("RAPIDAPI_KEY"),
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }

    odds_response = json.loads(requests.request(
        "GET", url, headers=headers, params=payload).text)

    odds_match_dict = {}
    for match in odds_response['response']:
        if match['game']['id'] in score_match_dict.keys():
            assert (match['bookmakers'][0]['name'] == 'NordicBet')
            assert (match['bookmakers'][0]['bets']
                    [0]['name'] == 'Match Winner')

            odd_dict = {}
            for value in match['bookmakers'][0]['bets'][0]['values']:
                odd_dict[value['odd']] = value['value']

            pred_win = odd_dict[min(odd_dict.keys())]
            odds_match_dict[match['game']['id']] = pred_win
        else:
            pass
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


def create_tweet(correct_ids, upset_ids, score_match_dict, date='2022-08-11'):
    tweet_text = str("SURPRISES: \n")
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

    if len(tweet_text) >= 280:
        tweet_text_list = tweet_text.split('EXPECTED')
        tweet_text_list[1] = 'EXPECTED'+tweet_text_list[1]
    else:
        tweet_text_list = [tweet_text]

    return tweet_text_list


if __name__ == "__main__":
    load_dotenv()

    date = "2022-08-06"

    score_match_dict = get_mlb_scores(date)
    odds_match_dict = get_mlb_odds(date)
    correct_ids, upset_ids = get_correct_upsets(
        odds_match_dict, score_match_dict)
    tweet_text_list = create_tweet(
        correct_ids, upset_ids, score_match_dict, date)
    tweet_to_twitter(tweet_text_list, date)
    print(tweet_text_list)
