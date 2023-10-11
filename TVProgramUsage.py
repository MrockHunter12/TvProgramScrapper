from TvScapperClass import TVProgram
import datetime

def main():
    url = "https://www.hoerzu.de/text/tv-programm/sender.php"
    time = datetime.datetime.now().time()
    #time = datetime.time(5, 30)
    program = TVProgram()
    channel_name_to_id = program.get_channel_dic(url)
    # day = 0 -> today
    programInfoList = program.getProgramInfoList(0,"ZDF", channel_name_to_id)
    try:
        print(program.get_program(programInfoList, time))
    except ValueError as e:
        programInfoListToday = program.getProgramInfoList(0,"ZDF", channel_name_to_id)
        programInfoListLastDay = program.getProgramInfoList(-1,"ZDF", channel_name_to_id)
        print(program.get_program_betweenDays(programInfoListLastDay, programInfoListToday))

# Run the main function
if __name__ == "__main__":
    main()