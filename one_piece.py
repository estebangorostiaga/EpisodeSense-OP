import requests
import re
import sys
import json
from tqdm import tqdm
from tabulate import tabulate
from html.parser import HTMLParser

class TitleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.data_list = []

    def handle_data(self, data):
        data = data.strip()
        self.data_list.append(data)

# Get the URL ID for each Episode
def get_ids(html_code):
	id_regex = r'data-tconst="(\w+)"'
	ids = []
	encountered_ids = set()

	matches = re.findall(id_regex, html_code)
	for id in matches:
		if id not in encountered_ids:
			ids.append(id)
			encountered_ids.add(id)
	return ids

# Request and Update IMDB Top 250 Data
def data_request(url):
	html_response = requests.get(url)

	with open("file.html", "w", encoding="utf-8") as file:
		file.write(html_response.text)
	file.close
  
	with open('file.html', 'r') as file:
		html_code = file.read()
	file.close
	ids = get_ids(html_code)
	episode_request(ids)
	
	return 0
  
# Returns List of Episodes from Last Update
def get_episode_list():
    with open('episode_numbers.json', 'r') as file:
        episode_list = json.load(file)
    return episode_list

# Get Episode # from each Episode ID
def episode_request(episode_ids):

    headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"
	}
    
    ep_num_list = []
    total_iterations = len(episode_ids)
    progress_bar = tqdm(total=total_iterations, desc='Progress', unit='episode')
    
    for id in episode_ids:
        url = f"https://www.imdb.com/title/{id}/"
        episode_response = requests.get(url, headers=headers)
        with open("file2.html", "w", encoding="utf-8") as file:
            file.write(episode_response.text)
        episode_number_match = re.search(r'"episodeNumber":(\d+)', episode_response.text)
        episode_number = episode_number_match.group(1) if episode_number_match else None
        progress_bar.update(1)
        ep_num_list.append(episode_number)
    
    progress_bar.close()
    with open('episode_numbers.json', 'w') as file:
        json.dump(ep_num_list, file, indent=2)
    file.close

# Creates Episodes List from Parser Data
def create_list(parser):
	data_list = [item for item in parser.data_list if item != '']
	episode_data = []
 
	for i in range(len(data_list) - 2):
		if data_list[i] == 'Episode:':
			episode_data.append(data_list[i+1:i+4])
				
	for sublist in episode_data:
		sublist[1] = sublist[1].strip('()')
	return episode_data
		
# Convert List to Json Output
def list_to_json(new_list, ids, episode_numbers):
	episode_dict = {}
	for idx, episode in enumerate(new_list):
		title, year, rating = episode
		episode_dict[f'episode{idx+1}'] = {
			'Title': title,
			'Episode #': episode_numbers[idx],
			'Year': year,
			'Rating': rating,
			'ID': ids[idx],
			'Ranking': str(idx + 1)
		}

	# Write to a JSON file
	with open('my_list.json', 'w') as f:
		json.dump(episode_dict, f, indent=4)
	f.close

# Print Table in Nice looking format
def pretty_print(episodes):
    table = []
    for episode in episodes:
        episode_data = [
			episode['Episode #'],
   			episode['Title'],
   			episode['Rating'],
   			episode['Year'],
			episode['Ranking']
		]
        table.append(episode_data)
    headers = ['Episode Number', 'Episode Title', 'Rating', 'Year', 'Ranking']
    print(tabulate(table, headers=headers, tablefmt='fancy_grid', stralign='center', numalign='center', floatfmt=".2f"))  

def validate_items():
    valid_range = range(1, 251)
    while True:
        items_displayed = input("Select the number of choices displayed (Min. 1 = Top 1, Max. 250 = Top 250): ")
        if items_displayed.isdigit() and int(items_displayed) in valid_range:
            return int(items_displayed)
        else:
            print("Invalid Input. Please try again!")
    
# Get All-Time Top Episodes
def all_time_func():
    with open('my_list.json', 'r') as file:
        data = json.load(file)
    
    items_displayed = validate_items()

    filtered_list = []
    
    for episode_number, episode_data in data.items():
        filtered_list.append(episode_data)
            
    pretty_print(filtered_list[:items_displayed]) 

# Get Top Unwatched Episodes
def unwatched_func():
    with open('my_list.json', 'r') as file:
        data = json.load(file)
        
    
    # Need to do a get request for latest total episodes
    episode_range = range(1, 1062)
    while True:
        current_episode = input("Enter the number of the last episode you watched: ")  # Year value to match
        if current_episode.isdigit() and int(current_episode) in episode_range:
            break
        else:
            print("Invalid Input. Please try again!")
    
    items_displayed = validate_items()
    filtered_list = []
    
    for episode_number, episode_data in data.items():
        if 'Episode #' in episode_data and int(episode_data['Episode #']) > int(current_episode):
            filtered_list.append(episode_data)
            
    pretty_print(filtered_list[:items_displayed]) 

# Get Top Episodes by Year
def top_by_year_func():

    with open('my_list.json', 'r') as file:
        data = json.load(file)
    
    # Need to Change to Avoid Hardcoding
    year_range = range(1999, 2024)
    while True:
        year_to_match = input("Enter your desired year (1999-Present): ")
        if year_to_match.isdigit() and int(year_to_match) in year_range:
            break
        else:
            print("Invalid Input. Please try again!")
    
    filtered_list = []
    
    for episode_number, episode_data in data.items():
        if 'Year' in episode_data and episode_data['Year'] == year_to_match:
            filtered_list.append(episode_data)
    
    pretty_print(filtered_list) 

# Create a custom HTML parser
def parser_func():
	
	# Read the HTML file
	with open('file.html', 'r') as file:
		html_code = file.read()
 
 	# Create an instance of the custom HTML parser
	parser = TitleParser()

	# Feed the HTML code to the parser
	parser.feed(html_code)

	ids = get_ids(html_code)

	# Get Episode Numbers from JSON File
	episode_numbers = get_episode_list()

	# Creates list from Title, Year, Rating, and Ranking 
	episode_data = create_list(parser)
 
	list_to_json(episode_data, ids, episode_numbers)

	if(sys.argv[1] == 'all_time_episodes'):
		all_time_func()
	elif(sys.argv[1] == 'unwatched_episodes'):
		unwatched_func()
	else:
		top_by_year_func()

if __name__ == '__main__':
    if(sys.argv[1] == 'update_data'):
        url = "https://www.imdb.com/search/title/?series=tt0388629&sort=user_rating,desc&count=250&view=simple"
        data_request(url)
    else:
        parser_func()