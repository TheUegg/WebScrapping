from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException
import time

# Function to initialize the WebDriver
def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    return driver

# Function to handle stale elements and retry operations
def retry_on_stale(driver, find_element_fn, max_retries=5, delay=1):
    for attempt in range(max_retries):
        try:
            return find_element_fn()
        except StaleElementReferenceException:
            time.sleep(delay)
    raise StaleElementReferenceException("Max retries exceeded.")

# Function to scroll and collect channels for a given keyword
def collect_channels(driver, keyword, max_channels=10):
    channels = set()
    base_url = "https://www.youtube.com/results?search_query=" + keyword + "&sp=EgIQAg%253D%253D"
    driver.get(base_url)

    print(f"Collecting channels for keyword: {keyword}")

    scroll_attempts = 0
    max_scroll_attempts = 20
    while len(channels) < max_channels and scroll_attempts < max_scroll_attempts:
        try:
            # Find all channel links
            elements = retry_on_stale(
                driver,
                lambda: driver.find_elements(By.XPATH, '//a[contains(@href, "/channel/") and not(contains(@href, "/user/"))]')
            )
            for element in elements:
                channel_url = element.get_attribute("href")
                if channel_url and channel_url not in channels:
                    print(f"Collected channel: {channel_url}")
                    channels.add(channel_url)
                    if len(channels) >= max_channels:
                        break

            # Scroll down to load more results
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            time.sleep(2)  # Adjust if necessary
            scroll_attempts += 1
            print(f"Scrolling attempt {scroll_attempts}. Collected {len(channels)} channels so far.")

        except (NoSuchElementException, TimeoutException) as e:
            print(f"Error encountered during scrolling: {e}")
            scroll_attempts += 1
            time.sleep(2)

    print(f"Finished collecting {len(channels)} channels for keyword '{keyword}'.")
    return list(channels)

# Main execution
if __name__ == "__main__":
    driver = init_driver()
    try:
        keywords = ["music", "gaming"]
        max_channels_per_keyword = 10
        results = {}

        for keyword in keywords:
            results[keyword] = collect_channels(driver, keyword, max_channels=max_channels_per_keyword)

        # Output results
        print("\nFinal Results:")
        for keyword, channels in results.items():
            print(f"{keyword}: {channels}")

    finally:
        driver.quit()
