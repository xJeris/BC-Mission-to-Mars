# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt
import time

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)

    news_title, news_paragraph = mars_news(browser)
    
    # Run all scraping functions and store results in dictionary
    data = {
      "news_title": news_title,
      "news_paragraph": news_paragraph,
      "featured_image": featured_image(browser),
      "facts": mars_facts(),
      "last_modified": dt.datetime.now(),
      "hemispheres": mars_images(browser) 
    }

    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):
   # Visit the mars nasa news site
   url = 'https://redplanetscience.com/'
   browser.visit(url)

   # Optional delay for loading the page
   browser.is_element_present_by_css('div.list_text', wait_time=1)

   # Convert the browser html to a soup object and then quit the browser
   html = browser.html
   news_soup = soup(html, 'html.parser')

   # Add try/except for error handling
   try:
       slide_elem = news_soup.select_one('div.list_text')

       # Use the parent element to find the first <a> tag and save it as  `news_title`
       news_title = slide_elem.find('div', class_='content_title').get_text()

       # Use the parent element to find the paragraph text
       news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
   except AttributeError:
        return None, None

   return news_title, news_p


def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    
    return img_url


def mars_facts():
    try:
        # use 'read_html" to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
      return None

    # Assign columns and set index of dataframe
    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)
    
    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()

if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())


def mars_images(browser):
    # Visit the mars image site
    base_url = 'https://astrogeology.usgs.gov'
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # Optional delay for loading the page
    time.sleep(1)

    # Convert the browser html to a soup object
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Create dictionary to hold image URLs
    hemispheres = []

    hemi_urls = []
    for link in img_soup.find_all('a', class_='itemLink'):
        hemi_urls.append(base_url + link.get('href')) if base_url + link.get('href') not in hemi_urls else hemi_urls

    x = 0
    
    # Use for loop to retrieve URLs and append them to the dictionary
    for hemi_url in hemi_urls:
    
        # find link on main page and click it
        browser.visit(hemi_urls[x])
        time.sleep(1)
    
        # Recall parser for new page
        html = browser.html
        img_soup = soup(html, 'html.parser')

        # Get image page result
        hemi_img_url = img_soup.find('a', string='Sample').get('href')
        hemi_title = img_soup.find('h2', class_='title').get_text()

        # Identify and append URL to the dictionary
        hemispheres.append({"img_url" : hemi_img_url, "title" : hemi_title})
    
        x = x + 1
    
        # Return to previous page
        browser.back()

    return hemispheres
