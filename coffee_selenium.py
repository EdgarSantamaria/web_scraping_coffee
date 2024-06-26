from selenium_driverless import webdriver
import asyncio
from bs4 import BeautifulSoup
import pandas as pd

async def get_coffee_urls():
    async with webdriver.Chrome() as browser:
        # Open the selection page
        await browser.get("https://www.beanz.com/en-us/coffee")

        last_height = await browser.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down to the bottom
            await browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait for new items to load
            await asyncio.sleep(100)

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


async def scrape_coffee_page(url):
    async with webdriver.Chrome() as browser:
        # Open the coffee page
        await browser.get(url)

        # Wait for the page to load
        await asyncio.sleep(3)

        # Extract the page's full HTML
        html = await browser.page_source

        # Quit the driver
        await browser.quit()

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

    # Extract country origin
    detail_tags = soup.find_all('p', class_='xps-text xps-text-p2-bold CoffeeInfo_roaster--detail__KLFjm')
    details = [tag.get_text() for tag in detail_tags] if detail_tags else ['N/A']

    return {
        'vendor': vendor,
        'bag_name': bag_name,
        'notes': notes,
        'details': details
    }


async def main():
    # Get the URLs of individual coffee pages
    coffee_urls = await get_coffee_urls()

    all_coffee_data = []
    for url in coffee_urls:
        # Scrape each coffee page
        coffee_data = await scrape_coffee_page(url)
        all_coffee_data.append(coffee_data)

    return all_coffee_data


# Run the main function
coffee_data_list = asyncio.run(main())

# Create a DataFrame from the scraped data
df = pd.DataFrame(coffee_data_list)

# Save the DataFrame to a CSV file
df.to_csv('coffee_data.csv', index=False)

# Print the DataFrame
print(df)
