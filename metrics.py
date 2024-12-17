import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import re
import json

# Load the JSON file
file_path = 'outputs/channel_urls.json'
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Helper functions
def clean_numeric(value):
    """Extract numeric values from strings and convert them to float."""
    if not isinstance(value, str):  # Ensure value is a string
        return None

    matches = re.findall(r'[\d.]+', value.split('\n')[1] if '\n' in value else value)
    return float(matches[0]) if matches else None

def clean_range(value):
    """Extract min and max values from a range like '$256.2K - $768.6K'."""
    if not isinstance(value, str):  # Ensure value is a string
        return None, None
    
    # Match numbers with optional decimal places
    matches = [m for m in re.findall(r'[\d.]+', value) if m.replace('.', '', 1).isdigit()]
    
    # Convert to float and handle 'K' multiplier
    min_val = float(matches[0]) * 1_000 if matches else None
    max_val = float(matches[1]) * 1_000 if len(matches) > 1 else None
    
    return min_val, max_val

def extract_subscribers(value):
    """Extract total subscribers and percentage increase for last 30 days."""
    if not isinstance(value, str):  # Ensure value is a string
        return None, None

    lines = value.split('\n')
    total_subs = float(re.sub(r'[^\d.]', '', lines[1])) * 1_000_000 if len(lines) > 1 else None
    last_30_days = float(lines[2].replace('%', '')) if len(lines) > 2 else None

    return total_subs, last_30_days

# Extract relevant information and clean the data
channels = []
for entry in data:
    channel_info = entry.get('url', {})

    # Process Subscribers
    total_subs, last_30_days_subs = extract_subscribers(channel_info.get('subscribers', ''))

    # Process Video Views
    video_views = clean_numeric(channel_info.get('video_views', ''))
    video_views_total = video_views * 1_000_000_000 if video_views is not None else None

    # Process Estimated Monthly Earnings
    monthly_min, monthly_max = clean_range(channel_info.get('estimated_monthly_earnings', ''))

    # Append to list
    channels.append({
        'Channel Name': (channel_info.get('name') or 'Unknown Channel').replace('YouTube Channel Stats', '').strip(),
        'Subscribers Total': total_subs,
        'Subscribers Last 30 Days (%)': last_30_days_subs,
        'Video Views Total (B)': video_views_total,
        'Monthly Earnings Min (K)': monthly_min,
        'Monthly Earnings Max (K)': monthly_max,
        'Engagement Rate (%)': clean_numeric(channel_info.get('engagement_rate', '')),
        'Upload Frequency (/week)': float(re.search(r'[\d.]+', str(channel_info.get('video_upload_frequency', '0'))).group()) if re.search(r'[\d.]+', str(channel_info.get('video_upload_frequency', '0'))) else 0,
        'Average Video Length (Min)': clean_numeric(channel_info.get('average_video_length', '')),
        'Location': channel_info.get('location', 'Unknown'),
        'Category': channel_info.get('category', 'Unknown')
    })

# Create a DataFrame
df = pd.DataFrame(channels)

# Drop rows with missing data
df = df.dropna()

# Show DataFrame
print(df.head())

# Plot Top 10 Channels by Subscribers
top_subs = df.sort_values(by='Subscribers Total', ascending=False).head(10)
plt.figure(figsize=(12, 6))
plt.bar(top_subs['Channel Name'], top_subs['Subscribers Total'], color='skyblue')
plt.title('Top 10 Channels by Subscribers (Total)')
plt.xticks(rotation=45, ha='right')
plt.ylabel('Subscribers (Total)')
plt.tight_layout()
plt.show()

# Plot Top 10 Channels by Video Views
top_views = df.sort_values(by='Video Views Total (B)', ascending=False).head(10)
plt.figure(figsize=(12, 6))
plt.bar(top_views['Channel Name'], top_views['Video Views Total (B)'], color='lightgreen')
plt.title('Top 10 Channels by Video Views (in Billions)')
plt.xticks(rotation=45, ha='right')
plt.ylabel('Video Views (B)')
plt.tight_layout()
plt.show()

# Set up seaborn for better aesthetics
sns.set(style="whitegrid")

# 1. Category-wise comparisons
plt.figure(figsize=(12, 6))
sns.boxplot(x='Category', y='Subscribers Total', data=df, palette='Set2')
plt.title('Subscribers Total by Category')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

plt.figure(figsize=(12, 6))
sns.boxplot(x='Category', y='Engagement Rate (%)', data=df, palette='Set2')
plt.title('Engagement Rate by Category')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

plt.figure(figsize=(12, 6))
sns.boxplot(x='Category', y='Video Views Total (B)', data=df, palette='Set2')
plt.title('Video Views by Category')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# 2. Location-wise comparisons
plt.figure(figsize=(12, 6))
sns.boxplot(x='Location', y='Subscribers Total', data=df, palette='Set1')
plt.title('Subscribers Total by Location')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

plt.figure(figsize=(12, 6))
sns.boxplot(x='Location', y='Engagement Rate (%)', data=df, palette='Set1')
plt.title('Engagement Rate by Location')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# 3. Upload Frequency vs Subscribers (Scatter Plot)
plt.figure(figsize=(12, 6))
sns.scatterplot(x='Upload Frequency (/week)', y='Subscribers Total', data=df, color='b', alpha=0.6)
plt.title('Upload Frequency vs Subscribers Total')
plt.xlabel('Upload Frequency (/week)')
plt.ylabel('Subscribers Total')
plt.tight_layout()
plt.show()

# Upload Frequency vs Engagement Rate (Scatter Plot)
plt.figure(figsize=(12, 6))
sns.scatterplot(x='Upload Frequency (/week)', y='Engagement Rate (%)', data=df, color='r', alpha=0.6)
plt.title('Upload Frequency vs Engagement Rate')
plt.xlabel('Upload Frequency (/week)')
plt.ylabel('Engagement Rate (%)')
plt.tight_layout()
plt.show()

# 4. Video Length vs Subscribers (Scatter Plot)
plt.figure(figsize=(12, 6))
sns.scatterplot(x='Average Video Length (Min)', y='Subscribers Total', data=df, color='g', alpha=0.6)
plt.title('Average Video Length vs Subscribers Total')
plt.xlabel('Average Video Length (Min)')
plt.ylabel('Subscribers Total')
plt.tight_layout()
plt.show()

# Video Length vs Engagement Rate (Scatter Plot)
plt.figure(figsize=(12, 6))
sns.scatterplot(x='Average Video Length (Min)', y='Engagement Rate (%)', data=df, color='purple', alpha=0.6)
plt.title('Average Video Length vs Engagement Rate')
plt.xlabel('Average Video Length (Min)')
plt.ylabel('Engagement Rate (%)')
plt.tight_layout()
plt.show()


