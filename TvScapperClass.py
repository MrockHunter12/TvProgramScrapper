import requests
from bs4 import BeautifulSoup
import datetime
import re

class TVProgram:
    def __init__(self):
        self.url = "https://www.hoerzu.de/text/tv-programm/sender.php"
        self.selected_channel_name = ""
        self.channel_name_to_id = {}
        self.channel_id = None
    def setDay(self, day):
        self.selected_day = day
    def setChannel(self, channelName):
        self.selected_channel_name = channelName
    def setUrl(self, url):
        self.url = url
    def get_channel_dic(self):
        response=""
        channel_name_to_id = {}
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
                        channel_name_to_id[channel_name.lower()] = channel_id
            else:
                print("Failed to fetch channel data.")
        else:
            print(f"Failed to fetch the page. Status code: {response.status_code}")
        self.channel_name_to_id = channel_name_to_id
        return self.channel_name_to_id
    
    def getIdFromChannelName(self):
        self.get_channel_dic()
        channel_id = None
        if self.selected_channel_name.lower() in self.channel_name_to_id:
            channel_id = self.channel_name_to_id[self.selected_channel_name.lower()]
        self.channel_id = channel_id
        return self.channel_id
    
    def getProgramInfoList(self, day):
        program_info = []
        self.getIdFromChannelName()
        if self.channel_id != None:
            params = {
                "newday": day,
                "tvchannelid":  self.channel_id,
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

    def get_program(self, selectedTime=None):
        response="empty"
        programInfoListToday = self.getProgramInfoList(0)
        programInfoListLastDay = self.getProgramInfoList(-1)
        programInfoListNextDay = self.getProgramInfoList(1)
        debug = (len(programInfoListToday) - 3)
        for i, line in enumerate(programInfoListToday):
            if i == len(programInfoListToday) - 1:
                break
            components_NextDay_first = programInfoListNextDay[1].split(' ', 2)
            components_LastDay_last = programInfoListLastDay[len(programInfoListLastDay) - 3].split(' ', 2)
            components_current = programInfoListToday[i].split(' ', 2)
            components_next = programInfoListToday[i+1].split(' ', 2)
            if (len(components_current[0]) == 5 and ':' in components_current[0]) and (len(components_next[0]) == 5 and ':' in components_next[0]):
                program_time = datetime.datetime.strptime(components_current[0], '%H:%M').time()
                next_program_time = datetime.datetime.strptime(components_next[0], '%H:%M').time()
                last_program_last_day = datetime.datetime.strptime(components_LastDay_last[0], '%H:%M').time()
                first_program_next_day = datetime.datetime.strptime(components_NextDay_first[0], '%H:%M').time()
                current_program = programInfoListToday[i]
                next_program = programInfoListToday[i+1]
                if selectedTime < program_time and selectedTime < next_program_time and selectedTime <= datetime.time(5, 00) and selectedTime > last_program_last_day and i<=3:
                    #program_time_last_day_last_element = datetime.datetime.strptime(programInfoListLastDay[len(programInfoListLastDay)-3], '%H:%M').time()
                    if selectedTime < program_time and selectedTime>= last_program_last_day:
                        response = self.get_program_betweenDays(programInfoListLastDay, programInfoListToday)
                        break
                elif (selectedTime < first_program_next_day) and (selectedTime > program_time) and (selectedTime>= next_program_time) and (i >debug):
                     response = f'Jetzt: {next_program}' + "\n" + f'Danach: {programInfoListNextDay[1]}'
                     break
                elif (selectedTime >= program_time and selectedTime < next_program_time) or (next_program_time<program_time and selectedTime<next_program_time):
                    response = f'Jetzt: {current_program}' + "\n" + f'Danach: {next_program}'

        return(response)
    
    def get_program_betweenDays(self, program_info_lastday = None,program_info = None ):
            current_program = program_info_lastday[-3]
            next_program = program_info[1]
            response = f'Jetzt: {current_program}' + "\n" + f'Danach: {next_program}'
            return response