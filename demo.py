"""Something I do for fun :D
Build a bot to log into facebook, surf https://facebook.com/groups/pythonvn/
Parsing post to post,
Comment test demo
"""


import re
import time
import argparse
from selenium import webdriver
from bs4      import BeautifulSoup as BS


def firefoxbrowser():
    global browser
    try:
        browser      = webdriver.Firefox()
    except Exception as e: print(e)
    time.sleep(2)
    return browser

def getfacebook(user,pwd):
    firefoxbrowser()
    browser.get("https://www.facebook.com/")
    time.sleep(2)
    ###<---browser.save_screenshot("check.png")--->###
    try:
        elem = browser.find_element_by_xpath("//input[@id='email']")
        elem.send_keys(user)
        elem = browser.find_element_by_xpath("//input[@id='pass']")
        elem.send_keys(pwd)
        elem = browser.find_element_by_xpath("//label[@id='loginbutton']")
        elem.click()
    except Exception as e: print(e)
    browser.get("https://www.facebook.com/groups/pythonvn/")
    soup  = BS(browser.page_source, "html.parser")
    posts = soup.findAll(attrs = {"class":"_4-u2 mbm _4mrt _5jmm _5pat _5v3q _4-u8"})
    f = open("demo.txt", "w")
    f.write(ascii(posts[1]))
    f.close()
    for post in posts:
        posttext = post.get_text()
    

#getfacebook("****************", "****************")
#time.sleep(10)
#browser.save_screenshot("demo.png")
def Main():
    parser = argparse.ArgumentParser(description = "Demo test for some more works")
    parser.add_argument("username", help = "Your email goes here")
    parser.add_argument("password", help = "Your password goes here")
    args   = parser.parse_args()
    result = getfacebook(args.username, args.password)


if __name__ == "__main__":
    Main()
