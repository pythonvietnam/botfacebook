# -*- coding:utf8 -*-
# author: ThangDX
import schedule
import config
import time
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


token = 'EAACEdEose0cBAIyfZBRoaaM0NdDmJRZCXrZBUPQZBxZA5zTGdLT0qP1XuRJ85PfmBIUVQQ06AzqKIAYXjXuEPXkvyyjYcoYJExeXWmWib6VwX9lyEZBdavx5E9pPAhlJZBI3Vrm5qK3BfujPt4YaAXZA2oB4m9gjHYjHOkfNBBmEGw0OcgZCanqkIkfqbc1wXG4wZD'
options = webdriver.ChromeOptions()
options.add_argument("--disable-notifications")

driver = webdriver.Chrome(chrome_options=options)


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


def check_hashtag(text):
    hashtags = map(lambda x: x[:(x + ' ').find(' ', 0)].lower(), re.findall('#.+', text))
    for hashtag in hashtags:
        for htag in config.HASHTAGS:
            if htag in hashtag:
                return True
    return False


def pending_posts():
    global driver
    driver.get(config.GROUP_URL+'pending/')

    members_warning_hashtag = []
    pendings = driver.find_elements_by_class_name('fbUserPost')
    approves = driver.find_elements_by_xpath("//a[starts-with(@ajaxify,'/ajax/groups/mall/approve.php?')]")
    time.sleep(3)
    for index in range(len(pendings)):
        if check_hashtag(pendings[index].find_element_by_tag_name('p').text):
            try:
                approves[index].click()
            except:
                print 'cannot click'
            time.sleep(3)
            pass
        else:
            members_warning_hashtag.append(pendings[index].find_elements_by_tag_name('a')[3].get_attribute('href').split('?')[0])
    members_warning_hashtag = list(set(members_warning_hashtag))
    #print members_warning_hashtag
    driver.get('https://www.messenger.com/')
    time.sleep(3)
    try:
        driver.find_element_by_id("email").send_keys(config.USERNAME)
        driver.find_element_by_id("pass").send_keys(config.PASSWORD)
        driver.find_element_by_id("loginbutton").click()
        time.sleep(1)
    except:
        driver.find_element_by_tag_name('button').click()

    for member in members_warning_hashtag:
        try:
            driver.get(member.replace('www.facebook.com', 'www.messenger.com/t'))
            time.sleep(3)
            driver.find_element_by_xpath("//div[@contenteditable='true']").send_keys(config.HASHTAGS_MESSAGE + Keys.ENTER)
            time.sleep(3)
        except:
            pass


def pending_members():
    global driver
    driver.get(config.GROUP_URL+'requests/')
    time.sleep(3)
    driver.find_element_by_name('approve_all').click()
    time.sleep(3)
    driver.find_element_by_xpath("//button[@action='confirm']").click()


def get_feed_ids(url=None):
    global token
    global driver
    if url is None:
        url = config.GRAPH_URL+'157091584481035/feed?fields=id&since='+str(int(time.time())-config.DAYS*3600*24)+'&access_token='+token
    res = requests.get(url).json()
    try:
        if len(res['data']) == 0:
            return []
        else:
            return map(lambda x: x['id'],res['data'])+get_feed_ids(res['paging']['next'])
    except:
        login()


def get_comments_of_feed(feed_id, url=None):
    global token
    global driver
    if url is None:
        url = config.GRAPH_URL+feed_id+'?fields=comments'+'&access_token='+token
    res = requests.get(url).json()['comments']
    try:
        for data in res['data']:
            for word in config.DELETE_WORDS:
                if word in data['message']:# Delete comment
                    try:
                        delete_comment(data['id'].split('_')[-1])
                    except:
                        pass
    except:
        print res


def delete_comment(comment_id):
    global driver
    driver.get(config.FACEBOOK_URL+comment_id)
    comments = driver.find_elements_by_xpath("//div[starts-with(@id,'comment_js')]")
    for comment in comments:
        for word in config.DELETE_WORDS:
            if word in comment.text:
                comment.find_element_by_class_name('UFICommentCloseButton').click()
                time.sleep(3)
                #Xoa binh luan
                driver.find_element_by_xpath("//a[@data-testid='ufi_comment_menu_delete']").click()
                #Xoa binh luan va xoa thanh vien
                #driver.find_element_by_xpath("//a[@data-testid='ufi_comment_menu_delete_comment_and_remove_commenter']").click()
                time.sleep(3)
                driver.find_element_by_xpath("//a[@data-testid='ufi_hide_dialog_delete_button']").click()
                delete_comment(comment_id)
                print '===='
    pass




def main():
    global driver
    try:
        pending_members()
    except:
        pass

    pending_posts()

    for feed_id in get_feed_ids():
        get_comments_of_feed(feed_id)


login()
main()

# schedule.every(3).minutes.do(main)
# while True:
#     schedule.run_pending()
#     time.sleep(1)