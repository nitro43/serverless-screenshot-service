import os
import hashlib
from urllib.parse import urlparse


import boto3
from flask import Flask, request, jsonify
from selenium import webdriver


DRIVER_LOC = os.environ['DRIVER_LOC']
BROWSER_LOC = os.environ['BROWSER_LOC']
WEBDRIVER_SCREEN_WIDTH = os.environ['WEBDRIVER_SCREEN_WIDTH']
WEBDRIVER_SCREEEN_HEIGHT = os.environ['WEBDRIVER_SCREEEN_HEIGHT']
WEBDRIVER_TIMEOUT = os.environ['WEBDRIVER_TIMEOUT']
BUCKET_NAME = os.environ['BUCKET_NAME']

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
app = Flask(__name__)


def _isvalid_url(url):
    parsed_url = urlparse(url)
    return bool(parsed_url.scheme and parsed_url.netloc)

def _get_hash(string):
    return hashlib.md5(string.encode()).hexdigest()


@app.route('/make_screenshot', methods=['POST'])
def make_screenshot():
    url = request.form['url']

    if not _isvalid_url(url):
        return jsonify({'error': f'giving url {url} are not valid'}), 422

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1280x1696')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--hide-scrollbars')
    chrome_options.add_argument('--disable-logging')
    chrome_options.add_argument('--silent')
    chrome_options.add_argument('--single-process')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--disable-dev-shm-usage')

    chrome_options.binary_location = BROWSER_LOC
    driver = webdriver.Chrome(executable_path=DRIVER_LOC,
                              service_log_path='/dev/null',
                              chrome_options=chrome_options)
    driver.get(url)
    # TODO validation
    s_shot = driver.get_screenshot_as_png()
    driver.close()
    driver.quit()

    url_hash = _get_hash(url)
    shot_url = f'https://{BUCKET_NAME}.s3.amazonaws.com/{url_hash}'
    table.put_item(Item={
        'target_url': url,
        'shot_url': shot_url
    })

    s3.put_object(Bucket=BUCKET_NAME,
                  Key=url_hash,
                  Body=s_shot,
                  ACL='public-read')

    return jsonify({'result':  {'target_url': url, 'shot_url': shot_url}})


@app.route('/screenshots', methods=['GET', 'POST'])
def get_screenshot():
    if request.method == 'POST':
        url = request.form['url']

        if not _isvalid_url(url):
            return jsonify({'error': f'giving url {url} are not valid'}), 422

        item = table.get_item(Key={'target_url': url}).get('Item')

        if not item:
            return jsonify({'error': 'not found'}), 404
        else:
            return jsonify({'result': item})

    else:
        items = table.scan().get('Items', [])
        results = []
        for item in items:
            results.append(
                {'target_url': item['target_url'], 'shot_url': item['shot_url']}
            )
        return jsonify({'result': results})
