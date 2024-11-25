import json
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
import static

# Function to initialize the WebDriver
def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    return driver

# Function to scroll and collect channels for a given keyword
    # def collect_channels(driver, keyword, max_channels=10):
    #     channels = set()
    #     base_url = static.BASE_URL + keyword + static.TREAT_AS_VIDEO
    #     driver.get(base_url)

    #     print(f"Collecting channels for keyword: {keyword}")

    #     scroll_attempts = 0
    #     max_scroll_attempts = 20
    #     while len(channels) < max_channels and scroll_attempts < max_scroll_attempts:
    #         try:
    #             # Find all channel links
    #             elements = retry_on_stale(
    #                 driver,
    #                 lambda: driver.find_elements(By.XPATH, '//a[contains(@href, "/channel/") and not(contains(@href, "/user/"))]')
    #             )
    #             for element in elements:
    #                 channel_url = element.get_attribute("href")
    #                 if channel_url and channel_url not in channels:
    #                     print(f"Collected channel: {channel_url}")
    #                     channels.add(channel_url)
    #                     if len(channels) >= max_channels:
    #                         break

    #             # Scroll down to load more results
    #             driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
    #             sleep(2)  # Adjust if necessary
    #             scroll_attempts += 1
    #             print(f"Scrolling attempt {scroll_attempts}. Collected {len(channels)} channels so far.")

    #         except (NoSuchElementException, TimeoutException) as e:
    #             print(f"Error encountered during scrolling: {e}")
    #             scroll_attempts += 1
    #             sleep(2)

    #     print(f"Finished collecting {len(channels)} channels for keyword '{keyword}'.")
    #     return list(channels)


    # # Function to handle stale elements and retry operations
    # def retry_on_stale(driver, find_element_fn, max_retries=5, delay=1):
    #     for attempt in range(max_retries):
    #         try:
    #             return find_element_fn()
    #         except StaleElementReferenceException:
    #             sleep(delay)
    #     raise StaleElementReferenceException("Max retries exceeded.")

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

def get_channel_urls():
    urls = []
    for url in static.URLS:
        links = []
        hrefs = []
        driver.get(url)
        sleep(5)
            
        elements = []
        try:
            elements = driver.find_elements(By.TAG_NAME, 'a')
        except Exception as e:
            pass

        hrefs = [element.get_attribute('href') for element in elements]
        print(f"Collected {len(hrefs)} links.", flush=True)
        print(hrefs, flush=True)
        links = [href for href in hrefs if ("/youtube/c/" in href) or ("/youtube/channel/" in href)]

        print(f"Collected {len(links)} channel links.", flush=True)

        print(links, flush=True)

        for link in links:
            try:
                urls.append(link)
                print("Collected channel URL:", link, flush=True)
            except Exception as e:
                print(f"Error collecting channel URL: {e}", flush=True)
                pass
        
    print(f"Collected {len(urls)} channel URLs.", flush=True)
    return urls

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
    driver = get_driver()
    try:
        # keywords = ["music", "gaming"]
        # max_channels_per_keyword = 10
        # results = {}

        # for keyword in keywords:
        #     results[keyword] = collect_channels(driver, keyword, max_channels=max_channels_per_keyword)

        urls = get_channel_urls()

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
