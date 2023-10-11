import requests
from bs4 import BeautifulSoup
import datetime
import re

class TVProgram:
    def __init__(self):
        self.url = "https://www.hoerzu.de/text/tv-programm/sender.php"
        self.current_time = datetime.datetime.now().strftime("%H:%M")
        self.channel_name_to_id = {}
        self.selected_channel_name = ""
        self.selected_day = ""
        response=""
        self.day_before_selcted = False

    def get_program_data_from_day_before(self):
        #self.selected_day = day or datetime.datetime.now().strftime("%A, %d.%m.")
        # Get the current date
        current_date = datetime.datetime.now()

        # Calculate the date one day before the current date
        day_before = current_date - datetime.timedelta(days=1)

        # Format the day_before date as per your requirement
        formatted_day_before = day_before.strftime("%A, %d.%m.")
        program_info = []
        if self.selected_channel_name.lower() in self.channel_name_to_id:
            channel_id = self.channel_name_to_id[self.selected_channel_name.lower()]
            params = {
                "newday": formatted_day_before,
                "tvchannelid": channel_id,
                "timeday": self.current_time
            }

            response = requests.post(self.url, data=params)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                program_items = soup.find_all('a', href=True)
                now = datetime.datetime.now()
                current_program = None
                next_program = None

                for item in program_items:
                    info = item.text.strip()
                    #if info[0].isdigit():
                    program_info.append(info)
        return program_info

    def fetch_channel_data(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            select_element = soup.find('select', {'name': 'tvchannelid'})
            if select_element:
                for option in select_element.find_all('option'):
                    channel_id = option['value']
                    channel_name = option.get_text()
                    # get channels debug
                    # print (channel_name)
                    if channel_id and channel_name:
                        self.channel_name_to_id[channel_name.lower()] = channel_id
            else:
                print("Failed to fetch channel data.")
        else:
            print(f"Failed to fetch the page. Status code: {response.status_code}")

    def get_program(self, channel_name, day=None):
        self.selected_channel_name = channel_name
        self.selected_day = day or datetime.datetime.now().strftime("%A, %d.%m.")
        if self.selected_channel_name.lower() in self.channel_name_to_id:
            channel_id = self.channel_name_to_id[self.selected_channel_name.lower()]
            params = {
                "newday": self.selected_day,
                "tvchannelid": channel_id,
                "timeday": self.current_time
            }

            response = requests.post(self.url, data=params)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                program_items = soup.find_all('a', href=True)
                if not self.day_before_selcted:
                    program_info = []
                now = datetime.datetime.now()
                current_program = None
                next_program = None

                for item in program_items:
                    info = item.text.strip()
                    #if info[0].isdigit():
                    if not self.day_before_selcted:
                        program_info.append(info)   
                for i, line in enumerate(program_info):

                    if i == len(program_info) - 1:
                        break
                    components_current = program_info[i].split(' ', 2)
                    components_next = program_info[i+1].split(' ', 2)
                    if (len(components_current[0]) == 5 and ':' in components_current[0]) and (len(components_next[0]) == 5 and ':' in components_next[0]):
                        program_time = datetime.datetime.strptime(components_current[0], '%H:%M').time()
                        next_program_time = datetime.datetime.strptime(components_next[0], '%H:%M').time()
                        current_program = program_info[i]
                        next_program = program_info[i+1]
                        now_time = now.time()
                        if now_time < program_time and now_time < next_program_time:
                            self.get_program_data_from_day_before()
                            self.day_before_selcted = True
                            self.get_program()
                        if program_time > next_program_time:
                            if now_time > program_time:
                                break
                        elif program_time <= now_time and next_program_time > now_time :
                            break
                #print (channel_name)                
                #print(f'The current program is: {current_program}')
                #print(f'The next program is: {next_program}')
                response = f'Jetzt: {current_program}' + "\n" + f'Danach: {next_program}'
            else:
                response = f"Failed to fetch the page. Status code: {response.status_code}"
        else:
            print(f"Selected channel name '{self.selected_channel_name}' is not in the dictionary.")
            response(f"Selected channel name '{self.selected_channel_name}' is not in the dictionary.")
        return(response)