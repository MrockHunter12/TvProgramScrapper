from TvScapperClass import TVProgram
import datetime

def main():
    url = "https://www.hoerzu.de/text/tv-programm/sender.php"
    #time = datetime.datetime.now().time()
    time = datetime.time(3, 52)
    program = TVProgram()
    program.setChannel("arte")
    program.setUrl(url)
    print(program.get_program(time))

# Run the main function
if __name__ == "__main__":
    main()