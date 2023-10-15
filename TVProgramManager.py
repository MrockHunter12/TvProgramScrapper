import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, time
from enum import Enum
import sqlite3
import os

class ProgramDay(Enum):
    YESTERDAY = -1
    TODAY = 0
    TOMORROW = 1

class TVProgramManager:
    def __init__(self):
        self.url = "https://www.hoerzu.de/text/tv-programm/sender.php"
        self.selected_channel_name = ""
        self.channel_name_to_id = {}
        self.channel_id = None
        self.selected_day = None

    def setDay(self, day):
        self.selected_day = day

    def setChannel(self, channelName):
        self.selected_channel_name = channelName

    def setUrl(self, url):
        self.url = url

    def getChannelDictionary(self):
        dictionary=""
        channel_name_to_id = {}
        response = requests.get(self.url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            select_element = soup.find('select', {'name': 'tvchannelid'})
            if select_element:
                for option in select_element.find_all('option'):
                    channel_id = option['value']
                    channel_name = option.get_text()
                    if channel_id and channel_name:
                        channel_name_to_id[channel_name.lower()] = channel_id
            else:
                print("Failed to fetch channel data.")
        else:
            print(f"Failed to fetch the page. Status code: {response.status_code}")
        self.channel_name_to_id = channel_name_to_id
        return self.channel_name_to_id

    def getIdFromChannelName(self):
        self.getChannelDictionary()
        channel_id = None
        if self.selected_channel_name.lower() in self.channel_name_to_id:
            channel_id = self.channel_name_to_id[self.selected_channel_name.lower()]
        self.channel_id = channel_id
        return self.channel_id
    
    def getProgramInfoList(self, programDay):
        conn = sqlite3.connect('program_database.db')
        cursor = conn.cursor()

        # Create the table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS program (
                channel TEXT,
                timestamp TIMESTAMP,
                program TEXT
            )
        ''')

        dateToday = datetime.now().strftime("%d-%m-%y")
        dateTomorrow = (datetime.now() + timedelta(days=1)).strftime("%d-%m-%y")
        dateYesterday = (datetime.now() + timedelta(days=-1)).strftime("%d-%m-%y")
        if programDay == ProgramDay.TODAY:
            dayRequest = 0
            current_date = dateToday
        elif programDay == ProgramDay.TOMORROW:
            dayRequest = 1
            current_date = dateTomorrow
            dateTomorrow = (datetime.now() + timedelta(days=2)).strftime("%d-%m-%y")
        elif programDay == ProgramDay.YESTERDAY:
            dayRequest = -1
            dateTomorrow = dateToday
            current_date = dateYesterday 
        program_info = []
        self.getIdFromChannelName()
        if self.channel_id != None:
            params = {
                "newday": dayRequest,
                "tvchannelid":  self.channel_id,
                "timeday": 1
            }
            response = requests.post(self.url, data=params)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                program_items = soup.find_all('a', href=True)
                for item in program_items:
                    info = item.text.strip()
                    if info[0].isdigit():
                        time_string = info.split(',')[0].split(' ')[0].strip()
                        program_string = info.split(',')[1].strip() + ", " + info.split(',')[2].strip()
                        time_obj = datetime.strptime(time_string, "%H:%M").time()
                        if time(0, 0) <= time_obj < time(5, 0):
                            dateTomorrowObj = datetime.strptime(dateTomorrow, "%d-%m-%y")
                            timestampTomorrow = datetime.combine(dateTomorrowObj.date(), time_obj)
                            info = f"{timestampTomorrow} {program_string}"
                            cursor.execute('''
                                INSERT INTO program (channel, timestamp, program)
                                VALUES (?, ?, ?)
                            ''', (self.selected_channel_name, timestampTomorrow, program_string))
                        else:
                            dateCurrentObj = datetime.strptime(current_date, "%d-%m-%y")
                            timestampToday = datetime.combine(dateCurrentObj.date(), time_obj)
                            info = f"{timestampToday} {program_string}"
                            cursor.execute('''
                                INSERT INTO program (channel, timestamp, program)
                                VALUES (?, ?, ?)
                            ''', (self.selected_channel_name, timestampToday, program_string))
                        program_info.append(info)
            else:
                raise ValueError('could not fetch site')
        conn.commit()
        conn.close()
        return program_info
    
    def saveProgramData(self):
        self.getChannelDictionary()
        today = self.getProgramInfoList(ProgramDay.TODAY)
        tomorrow = self.getProgramInfoList(ProgramDay.TOMORROW)

    def getCurrentRunningProgram(self, channelName):
        current_timestamp = datetime.now()
        #current_timestamp = datetime(2023, 10, 16 ,4, 11)
        conn = sqlite3.connect('program_database.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT program, timestamp
            FROM program
            WHERE channel = ? AND time(timestamp) <= time(?) AND date(timestamp) = date(?)
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (channelName.lower(), current_timestamp, current_timestamp))
        result1 = cursor.fetchone()
        if result1 is not None:
            current_program, timestampCurrent = result1

        cursor.execute('''
            SELECT program, timestamp
            FROM program
            WHERE channel = ? AND timestamp > ?
            ORDER BY timestamp ASC
            LIMIT 1
        ''', (channelName.lower(), current_timestamp))
        result2 = cursor.fetchone()
        if result2 is not None:
            next_program, timestampNext = result2
        #next_program = cursor.fetchone()[0]
        #return current_program
        timestampCurrent = datetime.strptime(timestampCurrent, "%Y-%m-%d %H:%M:%S")
        timestampNext = datetime.strptime(timestampNext, "%Y-%m-%d %H:%M:%S")

        formatted_current = timestampCurrent.strftime("%H:%M")
        formatted_next = timestampNext.strftime("%H:%M")

        response = f"Jetzt: {formatted_current} {current_program} Danach: {formatted_next} {next_program}"
        return response
    
    def fetchAllProgramms(self):
        dic= self.getChannelDictionary()
        self.clearDatabase()
        for channel_name, channel_id in dic.items():
            self.setChannel(channel_name)
            self.getProgramInfoList(ProgramDay.YESTERDAY)
            self.getProgramInfoList(ProgramDay.TODAY)
            self.getProgramInfoList(ProgramDay.TOMORROW)

    def clearDatabase(self):
        os.remove('program_database.db')

