import requests
from bs4 import BeautifulSoup
import datetime
import re

# The URL of the website
url = "https://www.hoerzu.de/text/tv-programm/sender.php"  # Replace with the actual URL

# Send a GET request to the website to fetch the page
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find and extract the current time (or time of day) from the website
    # You'll need to inspect the HTML source to find the relevant element
    # Example: current_time_element = soup.find('div', class_='current-time')
    #current_time_element = soup.find('div', class_='current-time')

    current_time = datetime.datetime.now().strftime("%H:%M")

    # Print the current time
    print(f"Current Time: {current_time}")

    # Define the parameters to send in the POST request
    selected_day = "Samstag, 07.10."  # Change this to your desired day

    # Create a dictionary to map channel names to IDs
    channel_name_to_id = {}
    select_element = soup.find('select', {'name': 'tvchannelid'})
    if select_element:
        for option in select_element.find_all('option'):
            channel_id = option['value']
            channel_name = option.get_text()
            if channel_id and channel_name:
                channel_name_to_id[channel_name] = channel_id

    # Check if the selected channel name is in the dictionary
    selected_channel_name = "Das Erste"  # Change this to your desired channel name
    if selected_channel_name in channel_name_to_id:
        # Get the corresponding channel ID
        channel_id = channel_name_to_id[selected_channel_name]

        # Define the parameters to send in the POST request
        params = {
            "newday": selected_day,
            "tvchannelid": channel_id,
            "timeday": current_time  # Use the current time extracted from the website
        }

        # Send a POST request to the website
        response = requests.post(url, data=params)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, 'html.parser')
            #print(soup)
            # Find and extract the TV program data
            program_items = soup.find_all('a', href=True)
            schedule = []
            program_info = []            
            now = datetime.datetime.now()
            today = datetime.date.today()
            current_program = None
            next_program = None
            # Process and print the TV program schedule
            for item in program_items:
                info = item.text.strip()  # Get the stripped text
                program_info.append(info)  # Append the info to the list
                #print([program_info])
                
            for i, line in enumerate(program_info):
                # Split the line into components
                #print(str(line))
                components = line.split(' ', 2)
                print(i)
                if i == len(program_info) - 1:
                    break
                # Check if the first component is a time
                if len(components[0]) == 5 and ':' in components[0]:
                    # Convert the time to a datetime object
                    program_time = datetime.datetime.strptime(components[0], '%H:%M').time()
                    now_time = now.time()
                    # Check if the program time is less than or equal to the current time
                    if program_time <= now_time:
                        current_program = line
                    elif next_program is None or program_time < datetime.datetime.strptime(next_program.split(' ', 2)[0], '%H:%M').time():
                        # This program is the next one to be broadcasted
                        next_program = line
                        break
            print(f'The current program is: {current_program}')
            print(f'The next program is: {next_program}')
            # Extract the TV program data you need from the parsed HTML
            # You'll need to inspect the actual HTML structure to find the relevant elements and classes/ids
            # Example: tv_program = soup.find('div', class_='program')

            # Print or process the extracted TV program data as needed
            # Example: print(tv_program.text)
        else:
            print(f"Failed to fetch the page. Status code: {response.status_code}")
    else:
        print(f"Selected channel name '{selected_channel_name}' is not in the dictionary.")
else:
    print(f"Failed to fetch the page. Status code: {response.status_code}")
