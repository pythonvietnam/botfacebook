# -*- coding:utf8 -*-
# author: ThangDX
import schedule
import config
import time
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

options = webdriver.ChromeOptions()
options.add_argument("--disable-notifications")

driver = webdriver.Chrome(chrome_options=options)
token = ''


def login():
    global token
    global driver
    driver.get('https://www.facebook.com/')

    driver.find_element_by_id("email").send_keys(config.USERNAME)
    driver.find_element_by_id("pass").send_keys(config.PASSWORD)
    driver.find_element_by_id("loginbutton").click()
    time.sleep(1)

    driver.get('https://www.facebook.com/me')
    token = driver.page_source.split('access_token:"')[1].split('",')[0]


def pending_members():
    global driver
    driver.get(config.GROUP_URL + 'requests/')
    time.sleep(3)
    driver.find_element_by_name('approve_all').click()
    time.sleep(3)
    driver.find_element_by_xpath("//button[@action='confirm']").click()
    time.sleep(3)


def pending_posts():
    global driver
    driver.get(config.GROUP_URL + 'pending/')
    time.sleep(3)
    approves = driver.find_elements_by_xpath("//a[starts-with(@ajaxify,'/ajax/groups/mall/approve.php?')]")
    for approve in approves:
        try:
            approve.click()
        except:
            pass
        time.sleep(3)


def get_feed_ids(url=None):
    global token
    global driver
    if url is None:
        url = config.GRAPH_URL + '157091584481035/feed?fields=id&since=' + str(
            int(time.time()) - config.DAYS * 3600 * 24) + '&access_token=' + token
    print url
    res = requests.get(url).json()
    try:
        if len(res['data']) == 0:
            return []
        else:
            return map(lambda x: x['id'], res['data']) + get_feed_ids(res['paging']['next'])
    except:
        login()


def check_hashtag(text):
    hashtags = map(lambda x: x[:(x + ' ').find(' ', 0)].lower(), re.findall('#.+', text))
    for hashtag in hashtags:
        for htag in config.HASHTAGS:
            if htag in hashtag:
                return True
    return False


def comment(feed_id):
    try:
        global driver
        id = feed_id.split('_')[1]
        url = 'https://m.facebook.com/groups/pythonvn/permalink/' + id + '/'
        driver.get(url)
        time.sleep(3)
        driver.find_element_by_id('composerInput').send_keys(config.HASHTAGS_MESSAGE)
        time.sleep(3)
        driver.find_element_by_name('submit').click()
    except:
        pass


def detect_feed(feed_id):
    global token
    global driver
    url = config.GRAPH_URL + feed_id + '?fields=message,comments&access_token=' + token
    res = requests.get(url).json()

    if not check_hashtag(res['message']):  # khong co hashtag hoac hashtag khong dung
        print "Khong co hashtag ", res['id'], res['message']
        id_of_user_comment = map(lambda user: user['from']['id'], res['comments']['data'])
        isComment = False
        for manager_id in config.MANAGER_IDS:
            if manager_id in id_of_user_comment:
                isComment = True
                break
        if not isComment:
            comment(res['id'])
            print "Vua comment xong"
        else:
            print "Da comment truoc do"
        print '================================='
    pass


def get_comments_of_feed(feed_id, url=None):
    global token
    global driver
    if url is None:
        url = config.GRAPH_URL + feed_id + '?fields=comments' + '&access_token=' + token
    try:
        res = requests.get(url).json()['comments']
        for data in res['data']:
            for word in config.DELETE_WORDS:
                if word in data['message'].lower() or data['message'] == '.':  # Delete comment
                    try:
                        #print data
                        delete_comment(data['id'].split('_')[-1])
                    except Exception as e:
                        print 'delete ',e
                        pass

    except Exception as e:
        print 'data ',e,requests.get(url).json()


def delete_comment(comment_id):
    global driver
    driver.get(config.FACEBOOK_URL + comment_id)
    comments = driver.find_elements_by_xpath("//div[starts-with(@id,'comment_js')]")

    for comment in comments:
        text = comment.find_element_by_class_name("UFICommentBody").text

        for word in config.DELETE_WORDS:
            if word in text.lower() or text == '.':
                comment.find_element_by_class_name('UFICommentCloseButton').click()
                time.sleep(3)
                # Xoa binh luan
                comment.find_element_by_xpath("//a[@data-testid='ufi_comment_menu_delete']").click()
                # Xoa binh luan va xoa thanh vien
                # driver.find_element_by_xpath("//a[@data-testid='ufi_comment_menu_delete_comment_and_remove_commenter']").click()
                time.sleep(3)
                comment.find_element_by_xpath("//a[@data-testid='ufi_hide_dialog_delete_button']").click()
                delete_comment(comment_id)
                print '===='
    pass


login()
print token
try:
    pending_posts()
except:
    pass

try:
    pending_members()
except:
    pass

for feed_id in get_feed_ids():
    detect_feed(feed_id)
    get_comments_of_feed(feed_id)
