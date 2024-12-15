import json
import time
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from time import sleep
from pyvirtualdisplay import Display
import static
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Function to initialize the WebDriver
def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    return driver

# Function to scrape additional channel details
def get_channel_data(driver, channel_url):
    print(f"Scraping data for channel: {channel_url}", flush=True)
    driver.get(channel_url)
    sleep(5)

    # Define a dictionary to store channel data
    channel_data = {
        "url": channel_url,
        "subscribers": None,
        "video_views": None,
        "engagement_rate": None,
        "video_upload_frequency": None,
        "location": None,
        "category": None,
        "videos": None,
        "average_video_length": None
    }

    try:
        # Wait for the necessary elements to load
        #WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.yt-formatted-string')))

        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[contains(@class, "yt-formatted-string") and contains(text(), " subscribers")]')))
            subscribers_elem = driver.find_element(By.XPATH, '//*[contains(@class, "yt-formatted-string") and contains(text(), " subscribers")]')
            channel_data["subscribers"] = subscribers_elem.text.strip() if subscribers_elem else "N/A"
        except Exception as e:
            print(f"Error scraping subscribers for {channel_url}: {e}", flush=True)
            channel_data["subscribers"] = "N/A"


        # Scraping Subscriber count (adjust as needed)
        subscribers_elem = driver.find_element(By.XPATH, '//*[contains(@class, "yt-formatted-string") and contains(text(), " subscribers")]')
        if subscribers_elem:
            channel_data["subscribers"] = subscribers_elem.text.strip()

        # Scraping Video views (adjust as needed)
        views_elem = driver.find_element(By.XPATH, '//*[contains(@class, "view-count") and contains(text(), " views")]')
        if views_elem:
            channel_data["video_views"] = views_elem.text.strip()

        # Scraping Engagement Rate (adjust as needed)
        engagement_rate_elem = driver.find_element(By.XPATH, '//span[contains(text(), "Engagement Rate")]/following-sibling::span')
        if engagement_rate_elem:
            channel_data["engagement_rate"] = engagement_rate_elem.text.strip()

        # Scraping Video Upload Frequency (adjust as needed)
        upload_frequency_elem = driver.find_element(By.XPATH, '//*[contains(@class, "upload-frequency")]/following-sibling::span')
        if upload_frequency_elem:
            channel_data["video_upload_frequency"] = upload_frequency_elem.text.strip()

        # Scraping Location (adjust as needed)
        location_elem = driver.find_element(By.XPATH, '//*[contains(@class, "location")]')
        if location_elem:
            channel_data["location"] = location_elem.text.strip()

        # Scraping Category (adjust as needed)
        category_elem = driver.find_element(By.XPATH, '//*[contains(text(), "Category")]/following-sibling::span')
        if category_elem:
            channel_data["category"] = category_elem.text.strip()

        # Scraping number of videos (adjust as needed)
        videos_elem = driver.find_element(By.XPATH, '//*[contains(text(), "Videos")]/following-sibling::span')
        if videos_elem:
            channel_data["videos"] = videos_elem.text.strip()

        # Scraping Average video length (adjust as needed)
        avg_video_length_elem = driver.find_element(By.XPATH, '//*[contains(text(), "Avg. Video Length")]/following-sibling::span')
        if avg_video_length_elem:
            channel_data["average_video_length"] = avg_video_length_elem.text.strip()

    except Exception as e:
        print(f"Error scraping channel data for {channel_url}: {e}", flush=True)

    return channel_data

def get_channel_urls(driver):
    urls = set()  # Use a set to store unique URLs
    target_count = 1000  # Target number of unique channel URLs

    for url in static.URLS:
        if len(urls) >= target_count:
            print(f"Target of {target_count} channel URLs reached.", flush=True)
            break  # Stop if target count is met

        print(f"Visiting URL: {url}", flush=True)
        driver.get(url)
        sleep(5)

        try:
            scripts = driver.find_elements(By.TAG_NAME, "script")
            pattern = r'UC[0-9A-Za-z_-]{22}'

            for script in scripts:
                script_content = script.get_attribute("innerHTML")
                matches = re.findall(pattern, script_content)

                # Construct the channel URLs and add only unique ones
                for match in matches:
                    channel_link = f"https://www.vidiq.com/youtube-stats/channel/{match}"
                    if channel_link not in urls:
                        urls.add(channel_link)

                print(f"Collected {len(matches)} additional links from script tags. Total unique URLs: {len(urls)}", flush=True)

                if len(urls) >= target_count:
                    print(f"Target of {target_count} channel URLs reached.", flush=True)
                    break

        except Exception as e:
            print(f"Error parsing script tags: {e}", flush=True)

    print(f"Final count of unique channel URLs: {len(urls)}", flush=True)
    return list(urls)  # Convert set to list for further processing

def save_to_json(urls, filename="channel_urls.json"):
    # Save to a JSON file in the '/outputs' directory
    output_file = f"/outputs/{filename}"

    # Convert the list of URLs to the required JSON format
    json_data = [{"url": url} for url in urls]

    # Save to a JSON file inside the container
    with open(output_file, "w") as json_file:
        json.dump(json_data, json_file, indent=4)

    print(f"Saved {len(urls)} URLs to {output_file}.", flush=True)


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

def check_duplicates(urls):
    # Convert set to list to check for duplicates
    url_list = list(urls)
    
    # Check for duplicates by comparing the length of the list and the set
    if len(url_list) != len(set(url_list)):
        print("Duplicates found in the collected URLs.", flush=True)
        # Optionally, log or print out the duplicates
        seen = set()
        duplicates = [url for url in url_list if url in seen or seen.add(url)]
        print(f"Duplicate URLs: {duplicates}", flush=True)
    else:
        print("No duplicates found in the collected URLs.", flush=True)

def scrape_channel_data(driver, channel_url):
    channel_data = {
        "url": channel_url,
        "name": None,  # Field for channel name
        "subscribers": None,
        "video_views": None,
        "estimated_monthly_earnings": None,
        "engagement_rate": None,
        "video_upload_frequency": None,
        "average_video_length": None,
        "location": None,  # New field for location
        "category": None,  # New field for category
    }

    try:
        # Load the channel page
        driver.get(channel_url)

        # Wait for the necessary elements to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'lg:border-vidiq-dark-300')]"))
        )

        # Extract the channel name
        try:
            name_elem = driver.find_element(By.CSS_SELECTOR, "div.flex.flex-col.gap-2.md\\:gap-3 h1")
            channel_data["name"] = name_elem.text.strip() if name_elem else "N/A"
        except Exception as e:
            print(f"Error scraping channel name for {channel_url}: {e}", flush=True)
            channel_data["name"] = "N/A"
            
        # Extract stats divs
        stats_divs = driver.find_elements(By.XPATH, "//div[contains(@class, 'lg:border-vidiq-dark-300')]")

        if stats_divs:
            if len(stats_divs) >= 1:
                channel_data["subscribers"] = stats_divs[1].text.strip()
            if len(stats_divs) >= 2:
                channel_data["video_views"] = stats_divs[2].text.strip()
            if len(stats_divs) >= 3:
                channel_data["estimated_monthly_earnings"] = stats_divs[3].text.strip()
            if len(stats_divs) >= 4:
                channel_data["engagement_rate"] = stats_divs[4].text.strip()
            if len(stats_divs) >= 5:
                channel_data["video_upload_frequency"] = stats_divs[5].text.strip()
            if len(stats_divs) >= 6:
                channel_data["average_video_length"] = stats_divs[6].text.strip()

        # Extract the location using JavaScript execution
        location_script = """
        return [...document.querySelectorAll('div.flex.flex-col.gap-4 > div')].find(div =>
            div.querySelector('p.mb-0')?.textContent.trim() === 'Location'
        )?.querySelector('p.mb-0.text-right.text-white')?.textContent.trim();
        """

        location = driver.execute_script(location_script)
        #print("Location:", location)

        # Extract the category using JavaScript execution
        category_script = """
        return [...document.querySelectorAll('div.flex.flex-col.gap-4 > div')].find(div =>
            div.querySelector('p.mb-0')?.textContent.trim() === 'Category'
        )?.querySelector('p.mb-0.text-right.text-white')?.textContent.trim();
        """

        category = driver.execute_script(category_script)
        #print("Category:", category)

        # Extract Location
        try:
            #location_elem = driver.find_element(By.XPATH, "//div[contains(text(), 'Location')]/following-sibling::div")
            channel_data["location"] = location#location_elem.text.strip() if location_elem else "N/A"
        except Exception as e:
            print(f"Error scraping location for {channel_url}: {e}", flush=True)
            channel_data["location"] = "N/A"

        # Extract Category
        try:
            #category_elem = driver.find_element(By.XPATH, "//div[contains(text(), 'Category')]/following-sibling::div")
            channel_data["category"] = category#category_elem.text.strip() if category_elem else "N/A"
        except Exception as e:
            print(f"Error scraping category for {channel_url}: {e}", flush=True)
            channel_data["category"] = "N/A"

    except Exception as e:
        print(f"Error scraping channel data for {channel_url}: {e}", flush=True)

    # Return the collected data for the channel
    return channel_data


# Example usage in your main scraping function
def scrape_channels(driver, urls):
    all_channel_data = []
    for channel_url in urls:
        print(f"Scraping data for channel: {channel_url}", flush=True)
        channel_data = scrape_channel_data(driver, channel_url)
        if channel_data:
            all_channel_data.append(channel_data)
    return all_channel_data

# Main execution
if __name__ == "__main__":
    try:
        display = Display(visible=0, size=(1920, 1080))
        display.start()
    except Exception as e:
        print(e, flush=True)
        raise Exception("Error initializing display")

    driver = get_driver()

    try:
        # Collect the channel URLs
        urls = get_channel_urls(driver)

        # Check for duplicates after collecting all URLs
        check_duplicates(urls)

        channel_data = scrape_channels(driver, urls)

        # Save collected data to a JSON file
        save_to_json(channel_data)  # Save scraped data to a JSON file
        print(f'Collected data for {len(channel_data)} channels. Process completed.', flush=True)


    finally:
        driver.quit()

    exit(0)
