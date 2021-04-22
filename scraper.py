from selenium import webdriver
import requests
import os
import time

DRIVER_PATH = '/usr/bin/chromedriver'
URL = 'https://isis.tu-berlin.de/mod/videoservice/view.php/course/21135/browse'
FOLDER = "MI_1_Videos"

files = os.listdir(FOLDER)

driver = webdriver.Chrome(executable_path=DRIVER_PATH)
driver.get(URL)

input("Login and press any key")

# copy auth cookies to requests
cookies = driver.get_cookies()
s = requests.Session()
for c in cookies:
    s.cookies.set(c['name'], c['value'])

# find all video links
links = [l.get_attribute('href') for l in driver.find_elements_by_xpath('//a[contains(@href,"mod/videoservice/view.php")]')]
vid_links = list(set([l for l in links if "cm" in l and "#" not in l and "browse" not in l]))
num_videos = len(vid_links)

for idx, link in enumerate(vid_links):
    driver.get(link)
    time.sleep(1.5)

    vid_files = driver.find_elements_by_xpath('//video[contains(@src,".mp4")]')
    if len(vid_files) > 1:
        print("Oops there seems to more than video file on this page")
    elif len(vid_files) < 1:
        print("\nOops no video found on this site:", link)
    else:
        # find video title
        title = driver.find_elements_by_xpath("//div[contains(@class, 'video-view')]/h3")
        title = title[0].text
        title = title.replace("/", "|") + ".mp4"

        if title in files:
            print("File already downloaded")
            continue
        print(f"\nDownloading video ({idx+1}/{num_videos}):", title)

        # download video and save to disk
        vid = vid_files[0].get_attribute("src")
        response = s.get(vid, stream=True)

        print("Saving to disk")
        with open(os.path.join(FOLDER, title), 'wb') as f:
            f.write(response.content)
