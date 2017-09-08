import config
import time
import re
from selenium import webdriver


def login(driver):
    global token
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
    driver.get('https://www.facebook.com/groups/1772673526354548/pending/')

    pendings = driver.find_elements_by_class_name('fbUserPost')
    approves = driver.find_elements_by_xpath("//a[starts-with(@ajaxify,'/ajax/groups/mall/approve.php?')]")
    time.sleep(3)
    for index in range(len(pendings)):
        #print pending.find_element_by_tag_name('abbr').get_attribute('data-utime') #time
        if check_hashtag(pendings[index].find_element_by_tag_name('p').text):
            try:
                approves[index].click()
            except:
                print 'cannot click'
            time.sleep(3)
            pass


def pending_members(driver):
    driver.get('https://www.facebook.com/groups/1772673526354548/requests/')
    time.sleep(3)
    driver.find_element_by_name('approve_all').click()
    time.sleep(3)
    driver.find_element_by_xpath("//button[@action='confirm']").click()


def main():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")

    driver = webdriver.Chrome(chrome_options=options)
    login(driver)
    pending_members(driver)
    pending_posts(driver)
    raw_input("Input: ")

main()
