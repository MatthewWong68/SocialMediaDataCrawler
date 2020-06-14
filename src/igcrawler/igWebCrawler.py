import json
import time
import datetime
import pytz
import ast
import localStorage
import httplib
import sys
import chromedriver_binary

from hashtag import Hashtag
from page import Page
from post import Post
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

###################################################################################
##                             Setting/Config                                    ##
###################################################################################

# A post without text
# pageURL = "https://www.instagram.com/p/Bziq7f2C-jM/"

pageURL = "https://www.instagram.com/apple/feed/"

# A single post from apple
# pageURL = "https://www.instagram.com/p/B2UT-qaFKgy/"

guest_mode = False # login or not
serverOn = False # for testing (needed when server is turned off)
email = "email"
password = "password"
crawledTime = datetime.datetime.now()
crawledTimeInUnix = time.mktime(pytz.utc.localize(crawledTime).timetuple())
host = "192.101.1.70" # "127.0.0.1"
port = 50080 # 8000
headers = {'Content-type': 'application/json'} # Header for HTML
days = 7 

###################################################################################
##                          End of Setting/Config                                ##
###################################################################################

# Parameters(for cmd)
for arg in sys.argv:
  if (arg[:7]==("--mode=")):
    if((arg.replace("--mode=","")) == "login"):
      guest_mode = False
    if((arg.replace("--mode=","")) == "logout"):
      guest_mode = True
  if (arg[:10]==("--pageURL=")):
    pageURL = arg.replace("--pageURL=","")
  if (arg[:7]==("--days=")):
    days = int(arg.replace("--days=",""))
  if (arg[:8]==("--email=")):
    email = int(arg.replace("--email=",""))
  if (arg[:11]==("--password=")):
    password = int(arg.replace("--password=",""))
  if (arg[:7]==("--host=")):
    host = arg.replace("--host=","")
  if (arg[:7]==("--port=")):
    port = int(arg.replace("--port=",""))

###################################################################################
##                                 Transformation                                ##
###################################################################################

def readLike(node):
    like = 0
    try:
        classBeforeLike = node.find_element_by_class_name("EDfFK")
        like = classBeforeLike.find_element_by_css_selector("span").text
        if "views" in like:
            classBeforeLike.find_element_by_css_selector("span").click()
            like = node.find_element_by_class_name("vJRqr")
            like = like.find_element_by_css_selector("span").text
            node.find_element_by_class_name("QhbhU").click()
        like = int(like.replace(",",""))
    except:
        like = 0
    # print "like: " + str(like)
    return like

def readHashtag(id, pathOfText):

    hashtagCount = 0
    numberOfHashtag = len(pathOfText.find_elements_by_css_selector("a"))

    while(hashtagCount < numberOfHashtag):
        possibleHashtag = pathOfText.find_elements_by_css_selector("a")[hashtagCount].text
        if "#" in possibleHashtag:
            hashtag = possibleHashtag.replace("#","")

            h = Hashtag(id, hashtag)
            hashtagInJVersion = json.dumps(h.__dict__)
            print hashtagInJVersion

            if(serverOn):
                connection = httplib.HTTPConnection(host, port)
                connection.request("POST","/api/ig/hashtags/", hashtagInJVersion, headers)
                response = connection.getresponse()
                print("Status: {} and reason: {}".format(response.status, response.reason))

        hashtagCount += 1

def readText(id, classBeforeText):
    try:
        classBeforeText.find_element_by_class_name("sXUSN").click()
        pathOfText = classBeforeText.find_element_by_css_selector("span")
    except:
        pathOfText = classBeforeText.find_element_by_css_selector("span")
    text = pathOfText.text
    readHashtag(id, pathOfText)
    return text 

def checkText(id, node):
    text = ""
    try: 
        classBeforeText = node.find_element_by_class_name("X7jCj")
        text = readText(id, classBeforeText)
    except NoSuchElementException:
        text = "no-text"
    return text
    
def readComment(node):
    comment = 0 
    try:
        classBeforeComment = node.find_element_by_class_name("lnrre")
        comment = classBeforeComment.find_element_by_css_selector("span").text
        comment = int(comment.replace(",",""))
    except:
        comment = 0
    return comment

def readNode(author, node):
    path = node.find_element_by_class_name("_1o9PC")
    postTime = path.get_attribute("datetime")
    postTime = datetime.datetime.strptime(postTime, '%Y-%m-%dT%H:%M:%S.000Z')
    postTimeInUnix = time.mktime(postTime.timetuple()) + 60*60*8
    
    # Check if the time fits the user request
    if(postTimeInUnix > crawledTimeInUnix - 60*60*24*days):
        id = node.find_element_by_class_name("c-Yi7").get_attribute("href")[28:39].replace("/","")
        like = readLike(node)
        full_text = checkText(id, node)
        comment = readComment(node)

        p = Post(id, full_text, author, str(crawledTime), str(path.get_attribute("datetime")), like, comment)
        postInJVersion = json.dumps(p.__dict__)
        print postInJVersion
        print ""

###################################################################################
##                            Post update(service)                               ##
###################################################################################

        if(serverOn):
            connection = httplib.HTTPConnection(host, port)
            connection.request("POST","/api/ig/posts/", postInJVersion, headers)
            response = connection.getresponse()
            print("Status: {} and reason: {}".format(response.status, response.reason))

        booleanToExit = True
    
    else:
        booleanToExit = False
    
    return booleanToExit

def readPost(index):
    
    # Wait for the posts to appear in the page
    WebDriverWait(browser, 15).until(EC.visibility_of_any_elements_located((By.CLASS_NAME, "_1o9PC")))
    
    # try-catch clause for loading more posts
    try: 
        node = browser.find_elements_by_class_name("eo2As")[index]
    except:
        time.sleep(10)
        node = browser.find_elements_by_class_name("eo2As")[index]

    # move to the post
    action = ActionChains(browser)
    action.move_to_element(node).perform()

    return node

def readPage():
    
    WebDriverWait(browser, 15).until(EC.visibility_of_any_elements_located((By.CLASS_NAME, "k9GMp")))

    # Author name 
    author = browser.find_elements_by_css_selector("h1")[0].text

    informationBar = browser.find_element_by_class_name("k9GMp")

    # Number of posts
    numberOfPost = informationBar.find_elements_by_css_selector("li")[0]
    numberOfPost = int(numberOfPost.find_element_by_css_selector("span>span").text.replace(",",""))
    
    # Number of followers
    numberOfFollowers = informationBar.find_elements_by_css_selector("li")[1]
    try: 
        numberOfFollowers = int(numberOfFollowers.find_element_by_css_selector("span").get_attribute("title").replace(",",""))
    except: 
        numberOfFollowers = int(numberOfFollowers.find_element_by_css_selector("span>span").get_attribute("title").replace(",",""))
    
    # Number of following
    numberOfFollowing = informationBar.find_elements_by_css_selector("li")[2]
    numberOfFollowing = int(numberOfFollowing.find_element_by_css_selector("span").text.replace(",",""))
    
    p = Page(author, numberOfPost, numberOfFollowers, numberOfFollowing)
    pageInJVersion = json.dumps(p.__dict__)
    print pageInJVersion

    if(serverOn):
        connection = httplib.HTTPConnection(host, port)
        connection.request("POST","/api/ig/pages/", pageInJVersion, headers)
        response = connection.getresponse()
        print("Status: {} and reason: {}".format(response.status, response.reason))

    return author

def startReadingPost():
    
    booleanToExit = True
    author = readPage()

    for n in range(0, 4, 1):
        try:
            booleanToExit = readNode(author, readPost(n))
        except:
            booleanToExit = False

    try: 
        while(booleanToExit):
            booleanToExit = readNode(author, readPost(4))
    except:
        booleanToExit = False

def save_cookie(driver, path):
    fileIO = open(path, 'w+')
    allCookies = driver.get_cookies()

    n = 0
    while(n < len(allCookies)):
        if (allCookies[n].has_key('expiry')):
            allCookies[n]['expiry'] = int(allCookies[n]['expiry'])
            n += 1
        else:
            n += 1

    fileIO.write(str(allCookies))
    fileIO.close()

def load_cookie(driver, path):
    fileIO = open(path, 'r+')
    listOfCookies = ast.literal_eval(fileIO.read())
    
    cookieIndex = 0
    while(cookieIndex < len(listOfCookies)):
        driver.add_cookie(listOfCookies[cookieIndex])
        cookieIndex += 1

def save_local_storage(driver, path):
    storage = localStorage.localStorage(driver)
    fileIO = open(path, 'w+')
    fileIO.write(str(storage))
    fileIO.close()

def load_local_storage(driver, path):
    fileIO = open(path, 'r+')
    listOfLocalStorage = ast.literal_eval(fileIO.read())

    localStorageIndex = 0
    while(localStorageIndex < len(listOfLocalStorage)):
        localStorage.localStorage(driver).set(listOfLocalStorage.keys()[localStorageIndex],listOfLocalStorage.values()[localStorageIndex])
        localStorageIndex += 1

###################################################################################
##                              Pre-crawl action                                 ##
###################################################################################

options = webdriver.ChromeOptions()
options.add_argument('user-agent="Mozilla/5.0 (iPod; U; CPU iPhone OS 2_1 like Mac OS X; ja-jp) AppleWebKit/525.18.1 (KHTML, like Gecko) Version/3.1.1 Mobile/5F137 Safari/525.20"')
# browser = webdriver.Chrome(chromedriver_binary.chromedriver_filename)
browser = webdriver.Chrome(chrome_options=options)
browser.set_window_size(1288, 689) # 1288,689

if (guest_mode):

    browser.get("https://www.instagram.com/accounts/login/")

    WebDriverWait(browser, 15).until(EC.visibility_of_any_elements_located((By.CLASS_NAME, "HmktE")))

    browser.find_elements_by_class_name("f0n8F")[0].send_keys(email)
    browser.find_elements_by_class_name("f0n8F")[1].send_keys(password)
    browser.find_elements_by_class_name("L3NKy")[1].click()

    WebDriverWait(browser, 15).until(EC.visibility_of_any_elements_located((By.CLASS_NAME, "GAMXX")))
    browser.find_element_by_class_name("GAMXX").click()
    
    WebDriverWait(browser, 15).until(EC.visibility_of_any_elements_located((By.CLASS_NAME, "M9sTE")))
    browser.get(pageURL)
    save_cookie(browser, "ig_cookie.txt")
    save_local_storage(browser, "ig_localStorage.txt")
    
else:
    browser.get(pageURL)
    load_cookie(browser, "ig_cookie.txt")
    load_local_storage(browser, "ig_localStorage.txt")
    browser.refresh()
###################################################################################
##                           Finish Pre-crawl action                             ##
###################################################################################

###################################################################################
##                                    Crawl                                      ##
###################################################################################
    
    # Case for reading a single post
    if ("instagram.com/p/" in pageURL):
        WebDriverWait(browser, 15).until(EC.visibility_of_any_elements_located((By.CLASS_NAME, "BrX75")))
        browser.find_element_by_class_name("BrX75").click()
        author = readPage()
        browser.back()
        readNode(author, browser)

    # Case for reading a page
    else:
        startReadingPost()
    
    browser.close()
###################################################################################
##                                  End of Crawl                                 ##
###################################################################################