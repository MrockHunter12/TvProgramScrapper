import requests
from bs4 import BeautifulSoup
import datetime
import re

class TVProgram:
    def __init__(self):
        self.url = "https://www.hoerzu.de/text/tv-programm/sender.php"
    def setDay(self, day):
        self.selected_day = day
    def setChannel(self, channelName):
        self.selected_channel_name = channelName
    def setUrl(self, url):
        self.url = url
    def get_channel_dic(self, url):
        response=""
        channel_name_to_id = {}
        response = requests.get(url)
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
                        channel_name_to_id[channel_name.lower()] = channel_id
            else:
                print("Failed to fetch channel data.")
        else:
            print(f"Failed to fetch the page. Status code: {response.status_code}")
        return channel_name_to_id
    
    def getProgramInfoList(self, day, channelName, channel_name_to_id):
        program_info = []
        if channelName.lower() in channel_name_to_id:
            channel_id = channel_name_to_id[channelName.lower()]
            params = {
                "newday": day,
                "tvchannelid": channel_id,
                "timeday": 1
            }
            response = requests.post(self.url, data=params)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                program_items = soup.find_all('a', href=True)
                for item in program_items:
                    info = item.text.strip()
                    program_info.append(info)
            else:
                raise ValueError('could not fetch site')
        return program_info

    def get_program(self, program_info=None, selectedTime=None):
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
                if selectedTime < program_time and selectedTime < next_program_time and selectedTime>= datetime.time(5, 00):
                    raise ValueError('selected time is not inside current day')
                if program_time > next_program_time:
                    if selectedTime > program_time:
                        break
                elif program_time <= selectedTime and next_program_time > selectedTime :
                    break
        response = f'Jetzt: {current_program}' + "\n" + f'Danach: {next_program}'
        return(response)
    
    def get_program_betweenDays(self, program_info_lastday = None,program_info = None ):
            current_program = program_info_lastday[-3]
            next_program = program_info[1]
            response = f'Jetzt: {current_program}' + "\n" + f'Danach: {next_program}'
            return response