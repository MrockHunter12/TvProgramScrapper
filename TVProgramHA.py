from TvScapperClass import TVProgram

def get_program(channel_name):
    program = TVProgram()
    program.fetch_channel_data()
    return program.get_program(channel_name)

# Run the main function
if __name__ == "__main__":
    import sys
    print(get_program(sys.argv[1]))