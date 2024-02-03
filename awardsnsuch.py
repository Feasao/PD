import requests
from bs4 import BeautifulSoup
import json
import re
import bs4
def get_wikipedia_page_content(wikipedia_url):
    response = requests.get(wikipedia_url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch Wikipedia content for {wikipedia_url}")
        return None

def extract_info_from_wikipedia(wikipedia_content):
    soup = BeautifulSoup(wikipedia_content, 'html.parser')

    awards = 0
    education_text = "No recorded education"
    dblp_link = None
    # Find the main content div
    body_content = soup.find('div', {'id': 'bodyContent'})
    
    if body_content:
        # Extract awards from the section containing the word "awards" in the title
        awards_section = body_content.find('span', string=lambda s: isinstance(s, str) and 'awards' in s.lower())
        if awards_section:
            awards_list = awards_section.find_next('ul')
            if awards_list:
                # Get all list items as awards
                awards_elements = awards_list.find_all('li')
                # Count the number of list items as awards
                awards = len(awards_elements)

        # Extract education from the section with the heading "Education"
        education_heading = soup.find('span', string=lambda s: isinstance(s, str) and 'education' in s.lower())
        # If the heading is found, extract the education information
        if education_heading:
            education_text = ''
            current_node = education_heading.find_next()
        
            # Iterate through the next siblings until a new heading is encountered
            while current_node and not (current_node.name and current_node.name.startswith('h')):
                if current_node.name == 'p':
                    education_text += current_node.get_text() + ' '

                current_node = current_node.find_next()
                
        # Search for the DBLP link below the Education section
        dblp_link = find_dblp_link(body_content)
    return awards, education_text.strip(), dblp_link

def find_dblp_link(body_content):
    # Find all links in the content
    all_links = body_content.find_all('a', href=True)
    for link in all_links:
        href = link.get('href', '').lower()
        # Check if the link contains 'dblp.org'
        if 'dblp.org' in href:
            print(link.get('href'))
            return link.get('href')   
    return None
def count_dblp_publications(dblp_link,name):
    if dblp_link:
        try:
            response = requests.get(dblp_link)
            if response.status_code == 200:
                dblp_content = response.text
                dblp_soup = BeautifulSoup(dblp_content, 'html.parser')

                # Find all sections containing the list of publications
                publication_sections = dblp_soup.find_all('ul', class_='publ-list')
                publications_count = 0

                for section in publication_sections:
                    # Count the number of publication entries in each section
                    publications_count += len(section.find_all('li', class_='entry'))

                print(f"Found {publications_count} publications")
                return publications_count

        except requests.exceptions.RequestException as e:
            print(f"Error fetching DBLP content for {dblp_link}: {e}")
    else:
        # If DBLP link is not available, perform a search on DBLP and pick the exact match
        dblp_search_url = f'https://dblp.org/search?q={name.strip().replace(" ", "/%20")}'
        print(f"Searching DBLP for {name} - {dblp_search_url}")
        try:
            search_response = requests.get(dblp_search_url)
            if search_response.status_code == 200:
                print(f"Search successful for {name}")
                search_content = search_response.text
                search_soup = BeautifulSoup(search_content, 'html.parser')

                # Find the first result in the search page
            first_result = search_soup.find('ul', class_='result-list')
            if first_result:
                # Get the first result's DBLP link
                dblp_link_element = first_result.find('a', itemprop='url')
                if dblp_link_element:
                    dblp_link = dblp_link_element['href']
                    print(f"Found DBLP link: {dblp_link}")

                    # Now you can call count_dblp_publications recursively with the found DBLP link
                    return count_dblp_publications(dblp_link,name)
            else:    
                print(f"No results found for {name} on DBLP")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching DBLP search results for {name}: {e}")

    return 0






def process_names_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as names_file:
        names_list = json.load(names_file)

    result = {}

    for name in names_list:
        wikipedia_url = f'https://en.wikipedia.org/wiki/{name.replace(" ", "_")}'
        print(f"Processing {name} - {wikipedia_url}")

        wikipedia_content = get_wikipedia_page_content(wikipedia_url)

        if wikipedia_content:
            awards, education, dblp_link = extract_info_from_wikipedia(wikipedia_content)
            publications_count = count_dblp_publications(dblp_link,name)
            result[name] = {
                "Awards": awards,
                "Education": education,
                "DBLP Publications": publications_count
            }
        else:
            result[name] = {
                "Awards": 0,
                "Education": "Failed to fetch Wikipedia content.",
                "DBLP Publications": 0
            }

    return result

# Example usage with a list of names read from the file
result = process_names_from_file("computer_scientists_names.json")

# Save the result to a JSON file
with open("final_output.json", "w", encoding="utf-8") as output_file:
    json.dump(result, output_file, indent=4, ensure_ascii=False)
