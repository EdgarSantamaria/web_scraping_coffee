# Beanz.com Coffee Data Scraper
## Project Overview
This project is a web scraping tool designed to extract coffee data from Beanz.com. The website's filters were not helpful for finding specific coffee types, so I developed this scraper to gather information about each coffee on the site.

## Features
 - Scrapes coffee data including vendor name, coffee bag name, tasting notes, size, price, and other details such as elevation, certifications, region, and country of origin.
 - Uses Selenium driverless approach for web scraping.
 - Uses BeautifulSoup for HTML parsing.
 - Compiles the extracted data into a Pandas DataFrame.
 - Saves the data to a CSV file for further analysis.
 - Scrapes 257 pages in 5 minutes.

## Requirements
- Python 3.6+
- BeautifulSoup
- Pandas
- asyncio
- selenium-driverless

## Installation
Clone the repository:
```
git clone https://github.com/EdgarSantamaria/web_scraping_coffee.git
```

Install required packages:
```
pip install beautifulsoup4 pandas asyncio selenium-driverless
```
## Usage
```
python coffee_selenium.py
```
## Output
The script outputs a CSV file (coffee_data.csv) containing detailed information about each coffee available on Beanz.com.

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.


