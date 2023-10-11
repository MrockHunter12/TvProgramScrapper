from TvScapperClass import TVProgram

def main():
    program = TVProgram()
    program.fetch_channel_data()
    print(program.get_program("prosieben"))


# Run the main function
if __name__ == "__main__":
    main()