import json
import os
import shutil
import requests


# do not change
URL = 'https://candfans.jp/api'
CONTENT_URL = 'https://fanty-master-storage.s3.ap-northeast-1.amazonaws.com'

def assure_dir(path: str) -> None:
    if not os.path.isdir(path):
        os.mkdir(path)

def create_auth() -> dict:
    with open('auth.json') as f:
        ljson = json.load(f)
    
    return {
        'User-Agent': ljson['User-Agent'],
        "Accept": "application/json, text/plain, */*",
        "Cookie": ljson['Cookie'],
        "Accept-Encoding": "gzip, deflate",
        'X-Xsrf-Token': ljson['X-Xsrf-Token'],
        'Referer': 'https://candfans.jp',
    }

def api_request(endpoint: str, getparams=None) -> requests.Response:
    return requests.get(URL + endpoint, 
                        headers=create_auth(),
                        params=getparams,
                        )

def get_follow() -> dict:
    user_info = api_request('/user/get-user-mine').json()
    
    user_id = user_info['data']['users'][0]['id']
    
    return api_request(f'/user/get-follow/{user_id}').json()['data']

def select_sub() -> list['str']:
    # Get Subscriptions
    SUBS = get_follow()
    
    sub_dict.update({"0": "*** Download All Models ***"})
    ALL_LIST = []
    
    for i in range(1, len(SUBS) + 1):
        ALL_LIST.append(i)
    
    for i in range(0, len(SUBS)):
        sub_dict.update({i+1: SUBS[i]['username']})
        sub_userid_dict.update({i+1: SUBS[i]['user_id']})
    
    if len(sub_dict) == 1:
        print('No models subbed')
        exit()
    
    MODELS = str((input('\n'.join('{} | {}'.format(key, value) for key, value in sub_dict.items()) + "\nEnter number to download model\n")))
    
    if MODELS == '0':
        return ALL_LIST
    else:
        return [x.strip() for x in MODELS.split(',')]

def download_file(source: str, profile: str, path: str) -> None:
    r = requests.get(source, stream=True)
    
    print(source)
    with open(f'profiles/{profile}/photos/{path}', 'wb') as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)

def get_photo_url(content_path: str) -> str:
    return CONTENT_URL + content_path

def get_content_paths(post: dict) -> list[str]:
    content_path = [
        post['contents_path1'],
        post['contents_path2'],
        post['contents_path3'],
        post['contents_path4'],
    ]
    
    return [_ for _ in content_path if _ != '']

def get_all_photos(user_id: str):
    has_more_page = True
    page = 0
    while has_more_page:
        photos = api_request('/contents/get-timeline',
                    getparams={
                    'user_id': user_id,
                    'page': page
                },
        ).json()['data']
        
        # begin download photos 
        for photo in photos:
            # skip the unaviable img
            if not photo['can_browsing'] == 0:
                username = photo['username']
                for content_path in get_content_paths(photo):
                    path = content_path.split('/')[-1]
                    if not os.path.isfile(f'profiles/{username}/photos/{path}'):
                        download_file(source=get_photo_url(content_path), profile=username, path=path)
        
        if len(photos) == 0:
            has_more_page = False
        
        page += 1

if __name__ == '__main__':
    print('\n')
    print(
    """
    """
    )

    sub_dict = {}
    sub_userid_dict = {}

    SELECTED_MODELS = select_sub()
    
    for M in SELECTED_MODELS:
        PROFILE_ID = str(sub_userid_dict[int(M)])
        PROFILE = str(sub_dict[int(M)])
        
        print('\ncandfans-dl is downloading content to profiles/' + PROFILE + '!\n')

        if os.path.isdir('profiles/' + PROFILE):
            print("\nThe folder profiles/" + PROFILE + " exists.")
            print("Media already present will not be re-downloaded.")
        
        assure_dir("profiles")
        assure_dir("profiles/" + PROFILE)
        assure_dir("profiles/" + PROFILE + "/photos")
        assure_dir("profiles/" + PROFILE + "/videos")
        print("Saving profile info...")
        get_all_photos(PROFILE_ID)
