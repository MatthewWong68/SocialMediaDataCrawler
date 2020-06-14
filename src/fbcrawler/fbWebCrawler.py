import json
import time
import datetime
import pytz
import ast
import localStorage
import httplib
import sys
import chromedriver_binary

from feed import Feed
from hashtag import Hashtag
from page import Page
from manager import Manager
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

###################################################################################
##                             Setting/Config                                    ##
###################################################################################

booleanToExitWhileLoop = True
guest_mode = False # login or not
serverOn = False # for testing (needed when server is turned off)
CURRENT_TIME_IN_UNIX_TIMESTAMP = time.mktime(datetime.datetime.now().timetuple())
bottomLoadMoreId = "www_pages_reaction_see_more_unitwww_pages_posts"
headers = {'Content-type': 'application/json'} # Header for HTML
days = 7 # 14
# pageURL = "https://www.facebook.com/pg/NTAS1985/posts/?ref=page_internal"
# pageURL = "https://www.facebook.com/pg/chianglaiwan/posts/?ref=page_internal"
# pageURL = "https://www.facebook.com/pg/futhead/posts/?ref=page_internal"
# pageURL = "https://www.facebook.com/pg/JobsDB.HongKong/posts/?ref=page_internal"
# pageURL = "https://www.facebook.com/NTAS1985/posts/1332910596868881"
pageURL = "https://www.facebook.com/pg/111804036872044/posts/?ref=page_internal"
email = "abc@xyz.com"
password = "1233211234567"
crawled_dt = datetime.datetime.now()
host = "127.0.0.1"
port = 50080 # 8000
TIME_SET_BY_USER = CURRENT_TIME_IN_UNIX_TIMESTAMP-60*60*24*days

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

# A function to switch a possible string into a int. For example, 25K to 25000
def switchingReactionToInt(maybeString):
  if "M" in maybeString:
      num = float(maybeString[:len(maybeString)-1])*1000000
  elif "K" in maybeString:
      num = float(maybeString[:len(maybeString)-1])*1000
  else:
      num = int(maybeString)
  return num

# A function to read feeds in a specific time 
def readFeed(index):
  
  # Scroll down for more new feeds

    if ((index % 5) == 0):
      
      try:
        WebDriverWait(browser, 15).until(EC.visibility_of_element_located((By.ID, bottomLoadMoreId)))
      
        action = ActionChains(browser)
        action.move_to_element(browser.find_element_by_id(bottomLoadMoreId)).perform()
      except:
        action = ActionChains(browser)
    
    # Check how many post is in the web page
    numberOfPost = len(browser.find_elements_by_css_selector("._3ccb"))

    # If index is larger than the number of post, then exit
    if (index < numberOfPost):

      # Identify the node, which is ready to read next
      node = browser.find_elements_by_css_selector("._3ccb")[index]
      
      WebDriverWait(browser, 15).until(EC.visibility_of_element_located((By.CLASS_NAME, "_5pcq")))
      classBeforeUnixTime = node.find_element_by_class_name("_5pcq")

      # Case for a post which is an advertisement(did't show the time of the post)
      if("partner" in classBeforeUnixTime.text):
        booleanToExitWhileLoop = True

      else:
        htmlForTesting = node.find_element_by_class_name("_1dwg").find_element_by_css_selector("div").get_attribute('innerHTML')
        unixTime = classBeforeUnixTime.find_elements_by_css_selector("abbr")[0].get_attribute("data-utime")

        if(("cover photo" in node.find_element_by_css_selector("h5").text) or ("profile picture" in node.find_element_by_css_selector("h5").text)):
          booleanToExitWhileLoop = True

        elif("Pinned" in htmlForTesting) and (float(unixTime) < TIME_SET_BY_USER):
          booleanToExitWhileLoop = True

        elif((float(unixTime) >= TIME_SET_BY_USER) or (("Pinned" in htmlForTesting) and (float(unixTime) >= TIME_SET_BY_USER))):
          booleanToExitWhileLoop = True

          # ID of the post will be read afterwards
          classBeforeID = node.find_elements_by_css_selector("form > input")[2]

          # Author of the post
          classBeforeAuthor = node.find_elements_by_css_selector("a")[2]
          author = classBeforeAuthor.text
        
          # Text of the post will be read afterwards
          textLink = node.find_element_by_class_name("userContent")

          # A function to test whether the feed has see more button 
          if ("see_more_link_inner" in textLink.get_attribute("innerHTML")):
            action = ActionChains(browser)
            seeMoreButton = node.find_element_by_class_name("see_more_link_inner")
            action.move_to_element(seeMoreButton).perform()
            seeMoreButton.click()

          # Store the text of the post
          actualText = textLink.get_attribute("textContent")
          actualText = actualText.replace("See Translation","").replace("See more","").replace("See original","").replace("Rate this translation","")
          if (actualText == ""):
            actualText = "no-text"

          # Read hashtag of the post(if there's)
          hashtagIndex = 0
          classBeforeHashtag = textLink.find_elements_by_class_name("_58cm")
          numberOfHashtag = len(classBeforeHashtag)
          while (numberOfHashtag > 0):
            h = Hashtag(classBeforeID.get_attribute("value"), classBeforeHashtag[hashtagIndex].text)
            
            hashtagInJVersion = json.dumps(h.__dict__)
            print hashtagInJVersion

            if(serverOn):
              connection = httplib.HTTPConnection(host, port)
              connection.request("POST","/api/fb/hashtags/", hashtagInJVersion, headers)
              response = connection.getresponse()
              print("Status: {} and reason: {}".format(response.status, response.reason))

            numberOfHashtag = numberOfHashtag - 1
            hashtagIndex = hashtagIndex + 1

          # if it has reaction
          if("3dli" in node.find_element_by_css_selector("form").get_attribute("innerHTML")):
            WebDriverWait(browser, 15).until(EC.element_to_be_clickable((By.CLASS_NAME, "_3dli")))

            # Reactions of the post
            classBeforeReaction = node.find_element_by_class_name("_3dli")
            reactionLink = classBeforeReaction.find_elements_by_css_selector("span > span")[0]

            # Number of reaction of the post
            reaction = int(switchingReactionToInt(reactionLink.text))

            # Scroll to the reaction link 
            action = ActionChains(browser)
            action.move_to_element(reactionLink).perform()

            # Click onto the view reaction button
            classBeforeReaction.find_elements_by_css_selector("span")[0].click()

            # Wait until the numbers are shown.
            WebDriverWait(browser, 15).until(EC.element_to_be_clickable((By.CLASS_NAME, "layerCancel")))
            feelingBar = browser.find_element_by_class_name("_21ab")
            like = 0
            love = 0
            angry = 0
            wow = 0
            haha = 0
            sad = 0
            
  ###################################################################################
  ##                                 Transformation                                ##
  ###################################################################################
            countInBar = len(feelingBar.find_elements_by_css_selector("div > ul > li"))

            # If the post have only one kind of reaction(for example, the post have only 40 likes, no angry...)
            if countInBar == 1:
              feelingInSentence = feelingBar.find_elements_by_css_selector("div > ul > li > a > span > span")[0].get_attribute("aria-label")
              if (feelingInSentence[-2:]=="ke"):
                likeInString = feelingInSentence.split(' ', 1)[0]
                like = int(switchingReactionToInt(likeInString))
              elif (feelingInSentence[-2:]=="ve"):
                loveInString = feelingInSentence.split(' ', 1)[0]
                love = int(switchingReactionToInt(loveInString))
              elif (feelingInSentence[-2:]=="ry"):
                angryInString = feelingInSentence.split(' ', 1)[0]
                angry = int(switchingReactionToInt(angryInString))
              elif (feelingInSentence[-2:]=="ow"):
                wowInString = feelingInSentence.split(' ', 1)[0]
                wow = int(switchingReactionToInt(wowInString))
              elif (feelingInSentence[-2:]=="ha"):
                hahaInString = feelingInSentence.split(' ', 1)[0]
                haha = int(switchingReactionToInt(hahaInString))
              elif (feelingInSentence[-2:]=="ad"):
                sadInString = feelingInSentence.split(' ', 1)[0]
                sad = int(switchingReactionToInt(sadInString))
              
              feelingBar.find_element_by_class_name("layerCancel").click()

            else:
              for n in range(1, len(feelingBar.find_elements_by_css_selector("div > ul > li")), 1):

                feelingInSentence = feelingBar.find_elements_by_css_selector("div > ul > li > a > span > span")[n].get_attribute("aria-label")
                if (feelingInSentence[-2:]=="ke"):
                  likeInString = feelingInSentence.split(' ', 1)[0]
                  like = int(switchingReactionToInt(likeInString))
                elif (feelingInSentence[-2:]=="ve"):
                  loveInString = feelingInSentence.split(' ', 1)[0]
                  love = int(switchingReactionToInt(loveInString))
                elif (feelingInSentence[-2:]=="ry"):
                  angryInString = feelingInSentence.split(' ', 1)[0]
                  angry = int(switchingReactionToInt(angryInString))
                elif (feelingInSentence[-2:]=="ow"):
                  wowInString = feelingInSentence.split(' ', 1)[0]
                  wow = int(switchingReactionToInt(wowInString))
                elif (feelingInSentence[-2:]=="ha"):
                  hahaInString = feelingInSentence.split(' ', 1)[0]
                  haha = int(switchingReactionToInt(hahaInString))
                elif (feelingInSentence[-2:]=="ad"):
                  sadInString = feelingInSentence.split(' ', 1)[0]
                  sad = int(switchingReactionToInt(sadInString))
              
              feelingBar.find_element_by_class_name("layerCancel").click()

          else:
            like = 0
            love = 0
            angry = 0
            wow = 0
            haha = 0
            sad = 0
            reaction = 0

          classBeforeShareAndComment = node.find_element_by_class_name("_3vum")
          commentAndShare = classBeforeShareAndComment.find_element_by_class_name("_4vn1")
          indexForWhileLoop = len(commentAndShare.find_elements_by_css_selector("span"))
          commentAndShareIndex = 0
          comment = 0
          share_count = 0

          while(indexForWhileLoop > 0):
            commentOrShare = commentAndShare.find_elements_by_css_selector("span")[commentAndShareIndex].text
            if (commentOrShare[-2:]=="ts"):
              commentInString = commentOrShare.replace(" comments", "")
              comment = int(switchingReactionToInt(commentInString))
            elif (commentOrShare[-2:]=="nt"):
              commentInString = commentOrShare.replace(" comment", "")
              comment = int(commentInString)
            elif (commentOrShare[-2:]=="es"):
              shareInString = commentOrShare.replace(" shares", "")
              share_count = int(switchingReactionToInt(shareInString))
            elif (commentOrShare[-2:]=="re"):
              shareInString = commentOrShare.replace(" share", "")
              share_count = int(shareInString)
            indexForWhileLoop = indexForWhileLoop - 1
            commentAndShareIndex = commentAndShareIndex + 1

          # id of the post
          id = classBeforeID.get_attribute("value")
          localTimeParsed = datetime.datetime.fromtimestamp(float(unixTime))
          utcTime = pytz.utc.localize(localTimeParsed)
        
          f = Feed(id, actualText, author, reaction, str(pytz.utc.localize(crawled_dt)), str(utcTime), like, love, angry, wow, haha, sad, comment, share_count)
          feedInJVersion = json.dumps(f.__dict__)
          print feedInJVersion

  ###################################################################################
  ##                            Feed update(service)                               ##
  ###################################################################################

          if(serverOn):
            connection = httplib.HTTPConnection(host, port)
            connection.request("POST","/api/fb/feeds/", feedInJVersion, headers)
            response = connection.getresponse()
            print("Status: {} and reason: {}".format(response.status, response.reason))

        # If the time of the post is viewable, but the time is out of range, then exit with this else statement 
        else:
          booleanToExitWhileLoop = False

        return booleanToExitWhileLoop

    # If index is larger than the number of post, then exit with this else statement
    else: 
      booleanToExitWhileLoop = False

    return booleanToExitWhileLoop

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

browser = webdriver.Chrome(chromedriver_binary.chromedriver_filename)
browser.set_window_size(1288, 689)

if (guest_mode):

  browser.get("http://www.facebook.com")
  browser.find_element_by_id("email").send_keys(email)
  browser.find_element_by_id("pass").send_keys(password)
  classBeforeLoginButton = browser.find_element_by_class_name("uiButton")
  classBeforeLoginButton.find_element_by_css_selector("input").click()

  save_cookie(browser, "cookie.txt")
  save_local_storage(browser, "localStorage.txt")

else:

  browser.get(pageURL)
  load_cookie(browser, "cookie.txt")
  load_local_storage(browser, "localStorage.txt")
###################################################################################
##                           Finish Pre-crawl action                             ##
###################################################################################
  
###################################################################################
##                                    Crawl                                      ##
###################################################################################
  browser.refresh()
  homeButton = browser.find_elements_by_class_name("_2yau")[0]
  
  # Case for reading a single post
  if "/pg/" in pageURL:
    index = 0
    while booleanToExitWhileLoop == True:
      booleanToExitWhileLoop = readFeed(index)
      index += 1

  # Case for reading a page
  else:
    readFeed(0)
    booleanToExitWhileLoop = False

  # Go to home page 
  action = ActionChains(browser)
  action.move_to_element(homeButton).perform()
  homeButton.click()

  # Taking the author name of the page 
  WebDriverWait(browser, 15).until(EC.visibility_of_any_elements_located((By.CLASS_NAME, "_64-f")))
  author_name = browser.find_element_by_class_name("_64-f").text

  # Wait until See More button to appear
  WebDriverWait(browser, 15).until(EC.visibility_of_any_elements_located((By.CLASS_NAME, "_1xgg")))
  action.move_to_element(browser.find_element_by_class_name("_1xgg")).perform()
  
  # Click on See More button
  seeMoreButton = browser.find_elements_by_class_name("_5dw8")[2].find_element_by_css_selector("a")
  seeMoreButton.click()

  # Wait Ads node to appear
  WebDriverWait(browser, 15).until(EC.visibility_of_any_elements_located((By.CLASS_NAME, "_7lxt")))

  # Summary (is or is not running ads)
  ads = True
  adsNode = browser.find_elements_by_class_name("_7lxt")[len(browser.find_elements_by_class_name("_7lxt"))-1]
  adsSentence = adsNode.find_element_by_class_name("_7lxr").text
  if "not" in adsSentence:
    ads = False
  else:
    ads = True
  
  print "Ads?: " + str(ads)

  # Click on Page History
  pageTransparency = browser.find_element_by_class_name("_7jy0")
  pageTransparency.find_elements_by_css_selector("ul > li")[1].click()

  # Wait until Page History to appear
  WebDriverWait(browser, 15).until(EC.visibility_of_any_elements_located((By.CLASS_NAME, "_7jxj")))

  # Page History (page created date)
  classBeforePageCreatedDate = browser.find_element_by_class_name("_7jxj").find_elements_by_class_name("_7jxk")[len(browser.find_elements_by_class_name("_7jxk"))-1]
  dateInPlainText = classBeforePageCreatedDate.find_elements_by_css_selector("div > span")[1].text
  pageCreatedDate = datetime.datetime.strptime(dateInPlainText, '%d %B %Y')
  pageCreatedDate = pageCreatedDate.strftime("%Y-%m-%d")
  
  totalNumberOfManager = 0
  managerInJVersion = []
  # Check if the information of the page manager is viewable(some page will not show where the page manager are)
  if (len(pageTransparency.find_elements_by_css_selector("ul > li")) > 2):
    
    # Click on Page manager
    pageTransparency.find_elements_by_css_selector("ul > li")[2].click()

    # Wait until Page manager to appear
    WebDriverWait(browser, 15).until(EC.visibility_of_any_elements_located((By.CLASS_NAME, "_7jxj")))

    # See who manage this page (take JSON of the countries)
    action.move_to_element(browser.find_element_by_class_name("uiOverlayButton")).perform()
    for n in range(1, len(browser.find_elements_by_class_name("_7jxk")), 1):
      managerInformation = browser.find_elements_by_class_name("_7jxk")[n].text
      if managerInformation[(len(managerInformation)-3):(len(managerInformation)-2)] == "(" :
        numberOfManager = managerInformation[(len(managerInformation)-2):(len(managerInformation)-1)]
        country = managerInformation[:len(managerInformation)-4]
      elif managerInformation[(len(managerInformation)-4):(len(managerInformation)-3)] == "(" :
        numberOfManager = managerInformation[(len(managerInformation)-3):(len(managerInformation)-1)]
        country = managerInformation[:len(managerInformation)-5]
      elif managerInformation[(len(managerInformation)-5):(len(managerInformation)-4)] == "(" :
        numberOfManager = managerInformation[(len(managerInformation)-4):(len(managerInformation)-1)]
        country = managerInformation[:len(managerInformation)-6]
      
      print "Country: " + country + " has " + numberOfManager + " manager."
      m = Manager(country, numberOfManager)
      managerInJVersion.append(m.__dict__)
      totalNumberOfManager = totalNumberOfManager + int(numberOfManager)
  
  p = Page(author_name, ads, pageCreatedDate, totalNumberOfManager, str(managerInJVersion))
  pageInJVersion = json.dumps(p.__dict__)

  if(serverOn):
    connection = httplib.HTTPConnection(host, port)
    connection.request("POST","/api/fb/pages/", pageInJVersion, headers)
    response = connection.getresponse()
    print("Status: {} and reason: {}".format(response.status, response.reason))

  print pageInJVersion

  browser.close()
###################################################################################
##                                  End of Crawl                                 ##
###################################################################################