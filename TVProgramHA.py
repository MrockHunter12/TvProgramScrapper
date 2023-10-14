from TvScapperClass import TVProgram
import datetime

def get_program(channel_name):
    url = "https://www.hoerzu.de/text/tv-programm/sender.php"
    time = datetime.datetime.now().time()
    response="Jetzt: ** no Info ** Danach: ** no Info **"
    program = TVProgram()
    program.setChannel(channel_name)
    program.setUrl(url)
    response = program.get_program(time)
    return response

# Run the main function
if __name__ == "__main__":
    import sys
    print(get_program(sys.argv[1]))