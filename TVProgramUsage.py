from TVProgramManager import TVProgramManager
import datetime

def main():
    url = "https://www.hoerzu.de/text/tv-programm/sender.php"
    time = datetime.datetime.now().time()
    response="Jetzt: ** no Info ** Danach: ** no Info **"
    program = TVProgramManager()
    program.setUrl(url)
    program.fetchAllProgramms()
    print(program.getCurrentRunningProgram('rtl'))

# Run the main function
if __name__ == "__main__":
    main()