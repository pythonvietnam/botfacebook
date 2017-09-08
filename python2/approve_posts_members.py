# -*- coding:utf8 -*-
# author: ThangDX

import config
import time
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


def login(driver):
    driver.get('https://www.facebook.com/')

    driver.find_element_by_id("email").send_keys(config.USERNAME)
    driver.find_element_by_id("pass").send_keys(config.PASSWORD)
    driver.find_element_by_id("loginbutton").click()
    time.sleep(1)


def check_hashtag(text):
    hashtags = map(lambda x: x[:(x + ' ').find(' ', 0)].lower(), re.findall('#.+', text))
    for hashtag in hashtags:
        for htag in config.HASHTAGS:
            if htag in hashtag:
                return True
    return False


def pending_posts(driver):
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
    print members_warning_hashtag
    driver.get('https://www.messenger.com/')
    driver.find_element_by_tag_name('button').click()
    for member in members_warning_hashtag:
        driver.get(member.replace('www.facebook.com', 'www.messenger.com/t'))
        time.sleep(3)
        driver.find_element_by_xpath("//div[@contenteditable='true']").send_keys(config.HASHTAGS_MESSAGE + Keys.ENTER)
        time.sleep(3)


def pending_members(driver):
    driver.get(config.GROUP_URL+'requests/')
    time.sleep(3)
    driver.find_element_by_name('approve_all').click()
    time.sleep(3)
    driver.find_element_by_xpath("//button[@action='confirm']").click()


def main():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")

    driver = webdriver.Chrome(chrome_options=options)
    login(driver)
    #pending_members(driver)
    pending_posts(driver)


    raw_input("Input: ")

main()
