from selenium_driverless import webdriver
from selenium_driverless.types.by import By
import asyncio
from bs4 import BeautifulSoup
import pandas as pd


async def get_coffee_urls():
    options = webdriver.ChromeOptions()
    async with webdriver.Chrome(options=options) as browser:
        # Open the selection page
        await browser.get("https://www.beanz.com/en-us/coffee")
        # Wait for page to load
        await asyncio.sleep(3)

        last_height = await browser.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll to above the footer to load coffees
            await browser.execute_script(f"window.scrollTo(0, {last_height - 1300});")
            # Wait for new items to load
            await asyncio.sleep(1)

            # Calculate new scroll height and compare with last scroll height
            new_height = await browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Extract the page's full HTML
        html = await browser.page_source

        # Quit the driver
        await browser.quit()

    # Parse the HTML to find coffee URLs
    soup = BeautifulSoup(html, 'html.parser')
    coffee_links = soup.find_all('a', class_='InfiniteHits_product-tile__tTYTU')

    # Extract the href attributes
    coffee_urls = ["https://www.beanz.com" + link.get('href') for link in coffee_links]
    return coffee_urls

# Function to scrape the coffee page for details
async def scrape_coffee_page(target, url):
    await target.get(url)
    await asyncio.sleep(1)
    html = await target.page_source

    # Parse the HTML
    soup = BeautifulSoup(html, 'html.parser')

    # Extract vendor name
    vendor_tag = soup.find('p', class_='xps-text xps-text-p2 product-info__vendor')
    vendor = vendor_tag.get_text() if vendor_tag else 'N/A'

    # Extract coffee bag name
    bag_name_tag = soup.find('h1', class_='xps-text xps-text-h2 product-info__product-name')
    bag_name = bag_name_tag.get_text() if bag_name_tag else 'N/A'

    # Extract coffee notes
    notes_tag = soup.find('p', class_='xps-text xps-text-p2-bold product-info__tasting-notes')
    notes = notes_tag.get_text() if notes_tag else 'N/A'

    # Extract bag details
    detail_tags = soup.find_all('p', class_='xps-text xps-text-p2-bold CoffeeInfo_roaster--detail__KLFjm')
    details = [tag.get_text() for tag in detail_tags] if detail_tags else ['N/A']

    # Extract bag size and cost
    bag_size_tag = soup.find('span', class_='xps-text xps-text-p3 option__text', string=lambda text: '|' in text)
    # Bag size and cost are separated by '|', split the text
    if bag_size_tag:
        split = bag_size_tag.get_text().split('|')
        if len(split) == 2:
            size = split[0].strip()
            price = split[1].strip()
        else:
            size = 'N/A'
            price = 'N/A'
    else:
        size = 'N/A'
        price = 'N/A'

    return {
        'vendor': vendor,
        'bag_name': bag_name,
        'notes': notes,
        'details': details,
        'size': size,
        'price': price
    }

# For faster parsing, load multiple tabs at once
async def batch_load_coffee_pages(coffee_urls, batch_size):
    options = webdriver.ChromeOptions()
    # Store coffee data
    all_coffee_data = []
    # Create a set to ensure no page is loaded twice
    processed_urls = set()

    # Loop through each coffee urls, according to batch size
    for i in range(0, len(coffee_urls), batch_size):
        # Get the batch that will be loaded
        batch = coffee_urls[i:i + batch_size]

        # Load the pages
        async with webdriver.Chrome(options=options) as browser:
            tasks = []
            for url in batch:
                if url not in processed_urls:
                    # Scrape each coffee page
                    target = await browser.new_window('tab', activate=False)
                    tasks.append(scrape_coffee_page(target, url))
                    processed_urls.add(url)

            batch_data = await asyncio.gather(*tasks)
            all_coffee_data.extend(batch_data)
    return all_coffee_data


async def main():
    # Get the URLs of individual coffee pages
    coffee_urls = await get_coffee_urls()

    # Test on a small batch
    #coffee_urls = coffee_urls[:10]
    # Send urls to batch loader function
    coffee_data_list = await batch_load_coffee_pages(coffee_urls, batch_size=10)

    return coffee_data_list


# Run the main function
coffee_data_list = asyncio.run(main())

# Create a DataFrame from the scraped data
df = pd.DataFrame(coffee_data_list)

# Save the DataFrame to a CSV file
df.to_csv('coffee_data.csv', index=False)

# Print the DataFrame
print(df)
