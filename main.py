import json
import time
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from time import sleep
from pyvirtualdisplay import Display
import static
from bs4 import BeautifulSoup
import requests
import re

# Function to initialize the WebDriver
def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    return driver

    # Function to scrape data from Social Blade
def scrape_socialblade(channel_url, retries=3, timeout=120):
    driver = Chrome(service=Service(ChromeDriverManager().install()), options=options)
    url = channel_url

    for attempt in range(retries):
        try:
            driver.get(url)
            driver.set_page_load_timeout(timeout)
            wait = WebDriverWait(driver, timeout)

            if "captcha" in driver.page_source.lower():
                driver.quit()
                return {'Channel ID': channel_id, 'Error': 'CAPTCHA encountered'}

            data = {'Channel ID': channel_id}
            # GET CHANNEL NAME
            try:
                channel_name = wait.until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="YouTubeUserTopInfoBlock"]/div[1]/span[2]')
                )).text
            except TimeoutException:
                channel_name = "N/A"

            try:
                subscribers = wait.until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="YouTubeUserTopInfoBlock"]/div[3]/span[2]')
                )).text
            except TimeoutException:
                subscribers = "N/A"

            try:
                total_views = wait.until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="YouTubeUserTopInfoBlock"]/div[4]/span[2]')
                )).text
            except TimeoutException:
                total_views = "N/A"

            try:
                monthly_earnings = wait.until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="YouTubeUserTopInfoBlock"]/div[5]/span[2]')
                )).text
            except TimeoutException:
                monthly_earnings = "N/A"

            data['Subscribers'] = subscribers
            data['Total Views'] = total_views
            data['Estimated Monthly Earnings'] = monthly_earnings
            data['Channel Name'] = channel_name

            driver.quit()
            return data

        except (ReadTimeoutError, TimeoutException, WebDriverException) as e:
            if attempt < retries - 1:
                sleep(3)
            else:
                driver.quit()
                return {'Channel ID': channel_id, 'Error': str(e)}

def get_channel_urls(driver):
    urls = []
    for url in static.URLS:
        links = []
        hrefs = []
        driver.get(url)
        sleep(5)

        elements = []
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, 'a[data-testid="channel-card-link"]')
        except Exception as e:
            pass

        print(f"Collected {len(elements)} elements.", flush=True)

        hrefs = [element.get_attribute('href') for element in elements]
        print(f"Collected {len(hrefs)} hrefs.", flush=True)
        print(hrefs, flush=True)
        links = [href for href in hrefs if ("/youtube-stats/channel/" in href)]

        print(f"Collected {len(links)} channel links.", flush=True)

        print(links, flush=True)

        for link in links:
            try:
                urls.append(link)
                print("Collected channel URL:", link, flush=True)
            except Exception as e:
                print(f"Error collecting channel URL: {e}", flush=True)
                pass


        # # Get the page source
        # page_source = driver.page_source
        
        # # Regular expression to extract all "channel_id" values
        # channel_ids = re.findall(r'"channel_id":"([^"]+)"', page_source)
        channel_ids = []
        # scripts = driver.find_element_by_tag_name("script")  # Or use more specific locators
        scripts = driver.find_elements(By.TAG_NAME, "script")
        print(f"Collected {len(scripts)} scripts.", flush=True)
        for script in scripts:
            script_content = script.get_attribute("innerHTML")
            print(f"Script content: {script_content}", flush=True)
            
            # Search for the pattern that contains the 'channel_id' in the script
            # This regex assumes the data is in the format: channel_id: "UCxxxxxxx"
            match = re.search(r'\"channel_id\":\"UC[0-9A-Za-z-]{21,}\"', script_content)
            if match:
                channel_ids.append(match.group(1))  # Add the channel_id to the list
        
        # remove duplicates
        channel_ids = list(set(channel_ids))

        # construct the channel URLs
        base = [f"https://www.https://vidiq.com/youtube-stats/channel/{channel_id}" for channel_id in channel_ids]
        urls.extend(base)
        print(f"Collected {len(base)} channel URLs.", flush=True)

        print(f"Collected {len(urls)} channel URLs.", flush=True)
        print(urls, flush=True)


    return urls


        #  # ---------------------------------------- PARTE 2 ----------------------------------------


        # headers = {
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        # 'Accept-Encoding': 'gzip, deflate, br',
        # 'Accept-Language': 'en-US,en;q=0.9',
        # 'Connection': 'keep-alive',
        # 'Referer': 'https://socialblade.com/',
        # 'Upgrade-Insecure-Requests': '1'
        # }

        # response = requests.get(url, headers=headers)
        # response.raise_for_status()
        # soup = BeautifulSoup(response.text, 'html.parser')
        # links = soup.find_all('a')
        # print(f"Collected {len(links)} links.", flush=True)
        # for link in links:
        #     if "/youtube/c/" in link.get('href') or "/youtube/channel/" in link.get('href'):
        #         urls.append(link.get('href'))
        #         print("Collected channel URL:", link.get('href'), flush=True)

        #  PARTE 3 -----------------------------------------

        # urls = []

        # # Set up Chrome options for headless mode
        # options = Options()
        # options.headless = True  # Run the browser in headless mode (no UI)

        # # Make sure you have the chromedriver path correct or use a WebDriver manager
        # driver = webdriver.Chrome(options=options)

        # # URL to scrape
        # url = 'https://socialblade.com/youtube/top/category/autos'  # Example URL

        # try:
        #     # Open the URL with Selenium
        #     driver.get(url)

        #     # Give the page some time to load
        #     time.sleep(5)  # Adjust based on the speed of your internet connection

        #     # Get the page source after it has loaded
        #     page_source = driver.page_source

        #     # Parse the page with BeautifulSoup
        #     soup = BeautifulSoup(page_source, 'html.parser')
        #     links = soup.find_all('a')
        #     print(f"Collected {len(links)} links.", flush=True)

        #     for link in links:
        #         href = link.get('href')
        #         if href and ("/youtube/c/" in href or "/youtube/channel/" in href):
        #             urls.append(href)
        #             print("Collected channel URL:", href, flush=True)

        # finally:
        #     # Close the browser after scraping
        #     driver.quit()
        #     return urls

def get_driver() -> WebDriver:

    sleep(5)
    print("------------------------------------------------------------------------------------------", flush=True)

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")

    retries = 5
    for i in range(retries):
        try:
            driver = webdriver.Remote("http://chrome:4444/wd/hub", options=chrome_options)
            return driver
        except WebDriverException:
            print(f"Attempt {i+1}/{retries} failed, retrying...", flush=True)
            sleep(3)
        raise Exception("Could not connect to Selenium server")


    # Default=0
    driver.implicitly_wait(10)

    return driver


# Main execution
if __name__ == "__main__":

    try:
        display = Display(visible=0, size=(1920, 1080))
        display.start()
    except Exception as e:
        print(e, flush=True)
        raise Exception("Erro ao iniciar display")

    driver = get_driver()

    # Set up Chrome options for headless mode
    # options = Options()
    # options.headless = True  # Run the browser in headless mode (no UI)

    # # Make sure you have the chromedriver path correct or use a WebDriver manager
    # driver = webdriver.Chrome(options=options)


    try:
        # keywords = ["music", "gaming"]
        # max_channels_per_keyword = 10
        # results = {}

        # for keyword in keywords:
        #     results[keyword] = collect_channels(driver, keyword, max_channels=max_channels_per_keyword)

        urls = get_channel_urls(driver)

        print(f'Collected {len(urls)} channel URLs. E terminou', flush=True)

        # Scrape data from Social Blade
        for url in urls:
            print(f"Scraping data for channel: {url}", flush=True)
            data = scrape_socialblade(url)
            # Save to output.json
            print(data, flush=True)
            json.dump(data, open("outputs/output.json", "a"))
            print(f"Data saved to output.json", flush=True)

        # # Output results
        # print("\nFinal Results:")
        # for keyword, channels in results.items():
        #     print(f"{keyword}: {channels}")

    finally:
        driver.quit()
