import requests
import array
from dat import URL
from datetime import datetime
import json


def fetch_api_key(user):
    with open('userdata.json') as data:
        d = json.load(data)
    try:
        return d[user]['api_key']
    except KeyError:
        return False


def make_request(user, path: str, payload: dict = {}):
    key = fetch_api_key(user)
    if not key:
        return False
    r = requests.get(URL + path, params=payload, headers={'Authorization': f'Bearer {key}'})
    d = r.json()
    return d


def get_reviews(user):
    if not fetch_api_key(user):
        return False
    data = make_request(user, "summary")
    twelve_reviews = 0
    upcoming_reviews = data['data']['reviews']
    for i in upcoming_reviews:
        if len(i['subject_ids']) > 0:
            next_count = len(i['subject_ids'])
            break
    for i in range(1, 13):
        twelve_reviews += len(upcoming_reviews[i]['subject_ids'])
    full_reviews = twelve_reviews
    for i in range(13, 25):
        full_reviews += len(upcoming_reviews[i]['subject_ids'])
    time_now = datetime.utcnow()
    time_next = datetime.strptime(data['data']['next_reviews_at'][:-1], '%Y-%m-%dT%H:%M:%S.%f')
    remaining_time = time_next - time_now
    next_review_message = f"You have {next_count} reviews "
    if time_now < time_next:
        next_review_message += f"in {str(remaining_time)[:-7]}"
    else:
        next_review_message += "right now!"
    return {
        'lessons': len(data['data']['lessons'][0]['subject_ids']),
        'reviews': len(data['data']['reviews'][0]['subject_ids']),
        'twelve': twelve_reviews,
        'twentyfour': full_reviews,
        'next': next_review_message
    }


def get_stages(user):
    if not fetch_api_key(user):
        return False
    stage = []
    for x in range(10):
        data = make_request(user, "assignments", {'srs_stages': x})
        stage.append(data['total_count'])
    return {
        'unlocked': stage[0],
        'apprentice_1': stage[1],
        'apprentice_2': stage[2],
        'apprentice_3': stage[3],
        'apprentice_4': stage[4],
        'guru_1': stage[5],
        'guru_2': stage[6],
        'master': stage[7],
        'enlightened': stage[8],
        'burned': stage[9]
    }


x = make_request("202262859902615561", "summary")
