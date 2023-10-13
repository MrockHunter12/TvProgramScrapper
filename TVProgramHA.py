from TvScapperClass import TVProgram
import datetime

def get_program(channel_name):
    url = "https://www.hoerzu.de/text/tv-programm/sender.php"
    time = datetime.datetime.now().time()
    resoponse="Jetzt: ** no Info ** Danach: ** no Info **"
    program = TVProgram()
    channel_name_to_id = program.get_channel_dic(url)
    # day = 0 -> today
    programInfoList = program.getProgramInfoList(0,channel_name, channel_name_to_id)
    try:
        resoponse = program.get_program(programInfoList, time)
    except ValueError as e:
        programInfoListToday = program.getProgramInfoList(0,channel_name, channel_name_to_id)
        programInfoListLastDay = program.getProgramInfoList(-1,channel_name, channel_name_to_id)
        resoponse = program.get_program_betweenDays(programInfoListLastDay, programInfoListToday)
    return resoponse

# Run the main function
if __name__ == "__main__":
    import sys
    print(get_program(sys.argv[1]))