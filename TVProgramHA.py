from TVProgramManager import TVProgramManager
from TVProgramManager import ProgramDay
import datetime

def get_program(program, channel_name):
    program.setChannel(channel_name)
    return(program.getCurrentRunningProgram(channel_name))

# Run the main function
if __name__ == "__main__":
    url = "https://www.hoerzu.de/text/tv-programm/sender.php"
    time = datetime.datetime.now().time()
    response="Jetzt: ** no Info ** Danach: ** no Info **"
    program = TVProgramManager()
    program.setUrl(url)
    import sys
    if sys.argv[1] == 'fetch':
        program.fetchAllProgramms()
        print('fetch done successuflly')
    else:
        print(get_program(program, sys.argv[1]))
    