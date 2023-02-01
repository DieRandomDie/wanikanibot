import math

import requests
import array
from dat import URL
from datetime import datetime
import json
from subject_ids import subject_counts


def fetch_api_key(user):
    with open('userdata.json') as data:
        d = json.load(data)
    try:
        return d[user]['api_key']
    except KeyError:
        return False


def make_request(user, path: str = "", payload: dict = {}, url: str = ''):
    if not url:
        url = URL
    key = fetch_api_key(user)
    if not key:
        return False
    r = requests.get(url + path, params=payload, headers={'Authorization': f'Bearer {key}'})
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


def get_stats(user):
    if not fetch_api_key(user):
        return False
    stage = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    subjects = [0, 0, 0]
    correct = [0, 0, 0]
    incorrect = [0, 0, 0]
    data = make_request("202262859902615561", path="review_statistics")
    for i in data['data']:
        cor = i['data']['meaning_correct'] + i['data']['reading_correct']
        inc = i['data']['meaning_incorrect'] + i['data']['reading_incorrect']
        s = i['data']['subject_type']
        if s == 'radical':
            correct[0] += cor
            incorrect[0] += inc
        elif s == 'kanji':
            correct[1] += cor
            incorrect[1] += inc
        else:
            correct[2] += cor
            incorrect[2] += inc
    data = make_request("202262859902615561", path="assignments")
    pages = math.ceil(data['total_count']/data['pages']['per_page'])-1
    for i in data['data']:
        stage[i['data']['srs_stage']] += 1
        s = i['data']['subject_type']
        if s == 'radical':
            subjects[0] += 1
        elif s == 'kanji':
            subjects[1] += 1
        else:
            subjects[2] += 1
    next_url = data['pages']['next_url']
    for i in range(pages):
        pass
    return {
        'radical': subjects[0],
        'radical_completion': round(subjects[0]/subject_counts[0]*100,2),
        'kanji': subjects[1],
        'kanji_completion': round(subjects[1]/subject_counts[1]*100,2),
        'vocabulary': subjects[2],
        'vocabulary_completion': round(subjects[2]/subject_counts[2]*100,2),
        'total': sum(subjects),
        'total_completion': round(sum(subjects)/sum(subject_counts)*100,2),
        'radical_accuracy': round(correct[0]/(correct[0]+incorrect[0])*100, 2),
        'kanji_accuracy': round(correct[1]/(correct[1]+incorrect[1])*100, 2),
        'vocabulary_accuracy': round(correct[2]/(correct[2]+incorrect[2])*100, 2),
        'total_accuracy': round(sum(correct)/(sum(correct)+sum(incorrect))*100, 2),
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


def get_subject_ids(s_type: str):
    id_list = []
    data = make_request("202262859902615561", path="subjects", payload={'types': s_type})
    pages = math.ceil(data['total_count']/data['pages']['per_page'])-1
    next_url = data['pages']['next_url']
    print(f"WaniKani Total {s_type}: {data['total_count']}")
    for i in data['data']:
        id_list.append(i['id'])
    for i in range(pages):
        data = make_request("202262859902615561", url=next_url)
        next_url = data['pages']['next_url']
        for j in data['data']:
            id_list.append(j['id'])
    print(f'List total: {len(id_list)}')
    print(id_list)
# get_subject_ids('vocabulary')


#today = datetime.utcnow().strftime('%Y-%m-%dT00:00:00.000000Z')
#print(today)
#data = make_request("202262859902615561", path="review_statistics", payload={'updated_after': today})
#print(data)