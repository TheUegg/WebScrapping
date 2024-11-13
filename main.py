import time
import random
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from urllib3.exceptions import ReadTimeoutError

# Set up Chrome options for Selenium
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # Optional for headless mode

# Function to get random channel IDs from YouTube
def get_random_channel_ids(keyword="music", required_channels=50):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    search_url = f"https://www.youtube.com/results?search_query={keyword}&sp=CAI%253D"  # Filter to show "channels" more prominently
    driver.get(search_url)
    time.sleep(3)  # Allow page to load

    channel_ids = set()  # Use a set to avoid duplicates
    attempts = 0
    max_scrolls = 20  # Increase the number of scrolls to load more results

    # Scroll until you collect enough channels
    while len(channel_ids) < required_channels and attempts < max_scrolls:
        # Scroll down to load more results
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Dynamically adjust sleep time based on collected channels and attempts
        if len(channel_ids) < 10:
            time.sleep(random.uniform(3, 5))  # Initial slower wait time for the first few channels
        elif len(channel_ids) < 30:
            time.sleep(random.uniform(2, 3))  # Slightly shorter wait time for the next batch
        else:
            time.sleep(random.uniform(1, 2))  # Shorter wait time as more channels are collected
        
        attempts += 1
        print(f"Scrolling attempt {attempts}...")

        # Extract unique channel IDs from multiple possible formats
        for element in driver.find_elements(By.XPATH, '//a[contains(@href, "/channel/")]'):
            channel_url = element.get_attribute("href")
            if "/channel/" in channel_url:
                channel_id = channel_url.split("/")[-1]
                channel_ids.add(channel_id)

        # Extract custom channel URLs (e.g., /c/ for custom URLs)
        for element in driver.find_elements(By.XPATH, '//a[contains(@href, "/c/")]'):
            channel_url = element.get_attribute("href")
            if "/c/" in channel_url:
                channel_id = channel_url.split("/")[-1]
                channel_ids.add(channel_id)
        
        # Extract old user URLs (e.g., /user/ for older YouTube channels)
        for element in driver.find_elements(By.XPATH, '//a[contains(@href, "/user/")]'):
            channel_url = element.get_attribute("href")
            if "/user/" in channel_url:
                channel_id = channel_url.split("/")[-1]
                channel_ids.add(channel_id)

        print(f"Collected {len(channel_ids)} unique channel IDs so far.")

    driver.quit()  # Close the driver after collecting channel IDs
    return list(channel_ids)

# Function to scrape data from Social Blade with retries
def scrape_socialblade(channel_id, retries=3, timeout=120):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    url = f"https://socialblade.com/youtube/channel/{channel_id}"
    
    for attempt in range(retries):
        try:
            driver.get(url)  # Navigate to the Social Blade page
            driver.set_page_load_timeout(timeout)  # Set a custom page load timeout
            wait = WebDriverWait(driver, timeout)  # Wait for the page elements

            # Check for CAPTCHA or block
            if "captcha" in driver.page_source.lower():
                print(f"CAPTCHA encountered for channel {channel_id}. Skipping...")
                driver.quit()
                return {'Channel ID': channel_id, 'Error': 'CAPTCHA encountered'}

            data = {'Channel ID': channel_id}

            # Extract data from Social Blade
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

            print(f"Channel Data: {data}")
            driver.quit()
            return data
        
        except (ReadTimeoutError, TimeoutException, WebDriverException) as e:
            print(f"Error scraping channel {channel_id}: {e}")
            if attempt < retries - 1:
                print(f"Retrying... ({attempt + 2}/{retries})")
                time.sleep(5)  # Wait before retrying
            else:
                driver.quit()
                return {'Channel ID': channel_id, 'Error': str(e)}

# Main function to get channel IDs and scrape data
def main():
    random_channels = get_random_channel_ids(keyword="music", required_channels=50)
    print(f"Collected {len(random_channels)} channel IDs.")

    scraped_data = []
    for i, channel in enumerate(random_channels):
        print(f"Scraping data for channel {i + 1}/{len(random_channels)}: {channel}")
        channel_data = scrape_socialblade(channel)
        scraped_data.append(channel_data)

    # Save scraped data to JSON
    with open('random_socialblade_data.json', 'w') as f:
        json.dump(scraped_data, f, indent=4)

    print(f"Scraping completed. Saved {len(scraped_data)} entries to JSON file.")

if __name__ == "__main__":
    main()
