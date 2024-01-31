import requests
import json
import re
# Wikipedia API endpoint URL
api_url = "https://en.wikipedia.org/w/api.php"

# Parameters for the API request
params = {
    "action": "query",
    "format": "json",
    "titles": "List_of_computer_scientists",
    "prop": "revisions",
    "rvprop": "content"
}

# Make the API request
response = requests.get(api_url, params=params)
data = response.json()

# Extract page content
page_id = next(iter(data["query"]["pages"]))
page_content = data["query"]["pages"][page_id]["revisions"][0]["*"]

# Save the content to a JSON file
output_filename = "computer_scientists.json"
with open(output_filename, "w", encoding="utf-8") as output_file:
    json.dump(page_content, output_file, indent=4, ensure_ascii=False)

print(f"Data saved to {output_filename}")

# Load the JSON data from the file
json_filename = "computer_scientists.json"
with open(json_filename, "r", encoding="utf-8") as json_file:
    data = json.load(json_file)

# Extract names of computer scientists
names = []
# Extract names using regular expressions
names = re.findall(r'^([^–]+)', data, re.MULTILINE)

#save the names to a json file

# Save the names to a JSON file
output_names_filename = "computer_scientists_names2.json"
with open(output_names_filename, "w", encoding="utf-8") as output_names_file:
    json.dump(names, output_names_file, indent=4, ensure_ascii=False)




# Print the extracted names
for name in names:
    print(name)

    
