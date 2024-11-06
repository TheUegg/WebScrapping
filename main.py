from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
import json



# Set up Selenium options for Chrome
options = webdriver.ChromeOptions()
#options.add_argument("--headless")

# Function to get random YouTube channel IDs
def get_random_channel_ids(keyword="trending"):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    search_url = f"https://www.youtube.com/results?search_query={keyword}"
    driver.get(search_url)
    time.sleep(3)  # Allow page to load

    channel_ids = set()  # Use a set to avoid duplicates

    # Locate channel links in search results
    for element in driver.find_elements(By.XPATH, '//a[contains(@href, "/channel/")]'):
        channel_url = element.get_attribute("href")
        # Extract the unique channel ID from the URL
        if "channel" in channel_url:
            channel_id = channel_url.split("/")[-1]
            channel_ids.add(channel_id)

        # Stop once you have a few unique channel IDs
        if len(channel_ids) >= 10:
            break

    driver.quit()  # Close the driver after fetching channel IDs
    return list(channel_ids)


# Example to get random channels based on the keyword
random_channels = get_random_channel_ids()
print("Random Channel IDs:", random_channels)

def scrape_socialblade(channel_id):

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    url = f"https://socialblade.com/youtube/channel/{channel_id}"
    driver.get(url)
    wait = WebDriverWait(driver, 15)  # Increase wait time

    # Check for CAPTCHA
    if "captcha" in driver.page_source.lower():
        print(f"CAPTCHA encountered for channel {channel_id}. Skipping...")
        driver.quit()
        return {'Channel ID': channel_id, 'Error': 'CAPTCHA encountered'}


    data = {'Channel ID': channel_id}

    try:
        # Try different approaches for each element

        # Subscribers
        try:
            subscribers = wait.until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="YouTubeUserTopInfoBlock"]/div[3]/span[2]')
            )).text
        except TimeoutException:
            subscribers = "N/A"  # Set to "N/A" if not found

        # Total Views
        try:
            total_views = wait.until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="YouTubeUserTopInfoBlock"]/div[4]/span[2]')
            )).text
        except TimeoutException:
            total_views = "N/A"

        # Estimated Monthly Earnings
        try:
            monthly_earnings = wait.until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="YouTubeUserTopInfoBlock"]/div[5]/span[2]')
            )).text
        except TimeoutException:
            monthly_earnings = "N/A"

        data['Subscribers'] = subscribers
        data['Total Views'] = total_views
        data['Estimated Monthly Earnings'] = monthly_earnings

    except Exception as e:
        print(f"Error scraping data for channel {channel_id}: {e}")

    driver.quit()  # Close the driver after each channel
    return data

# Scrape data for each random channel
scraped_data = []
for channel in random_channels:
    scraped_data.append(scrape_socialblade(channel))

# Print the scraped data
print("Scraped Data:", scraped_data)

# Save data to JSON file
with open('random_socialblade_data.json', 'w') as f:
    json.dump(scraped_data, f, indent=4)
