import requests
from bs4 import BeautifulSoup
import json

def scrape_computer_scientists_names(wikipedia_url):
    response = requests.get(wikipedia_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the main content div
        body_content = soup.find('div', {'id': 'mw-content-text'})

        if body_content:
            scientists_names = []

            # Iterate through the headings (H2 and H3)
            for heading in body_content.find_all(['h2', 'h3']):
                if heading.name == 'h2' and heading.get_text().strip().lower() == 'z':
                    break

                if heading.name == 'h3':
                    # Find the associated ul element under each heading
                    ul_element = heading.find_next('ul')
                    if ul_element:
                        # Extract names from li elements under ul
                        names = [li.get_text(strip=True) for li in ul_element.find_all('li')]
                        scientists_names.extend(names)

            return scientists_names

    return None

# URL of the "List of computer scientists" Wikipedia page
wiki_url = 'https://en.wikipedia.org/wiki/List_of_computer_scientists'

# Scrape computer scientists' names
scientists_names = scrape_computer_scientists_names(wiki_url)

if scientists_names:
    # Save names to a JSON file
    with open("computer_scientists_titles.json", "w", encoding="utf-8") as names_file:
        json.dum
