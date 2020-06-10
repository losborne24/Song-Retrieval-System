import socket
import pickle       # allows lists to be sent to client.
import sys
import datetime


def main():
    hash_music = read_file("100worst.txt")
    setup_connection(hash_music, "server.log")


def read_file(filename):
    hash_music = {}
    server_file = open(filename, "r")
    lines = server_file.readlines()                # put each line into list
    for i in range(0, len(lines)):
        line = lines[i]
        if line[0].isdigit():               # if first char is digit
            entry_no = line[:2]             # set digit as hash key.
            entry_no = entry_no.rstrip()
            line = line[4:-1]               # remove first four characters (used for the hash key) and new line from string
            if line[-1].isdigit():          # if last char is digit, then artist and song is on same line
                song = line[:30]            # get first 30 characters (representing song) and removes whitespace
                song = song.rstrip()
                artist = line[31:-4]        # gets last 31 characters (representing artist and excluding date). Removes whitespace
                artist = artist.rstrip()
                hash_music[entry_no] = (artist, song) # stores value as tuple in hash table.
            else:
                song = line                 # if artist and song are on separate lines, the current line is holds song
                artist = lines[i+1]         # and the following line stores artist
                artist = artist[:-5]        # -5 instead of -4 as looking at a different line so \n needs to be removed once more
                artist = artist.lstrip()    # remove whitespace
                artist = artist.rstrip()
                hash_music[entry_no] = (artist, song)
    return hash_music


def setup_connection(hash_music, filename):
    server_file = open(filename, "a")                                  # append to log server_file
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # create socket
    except socket.error:
        s = None
    port = 3125
    try:
        start_time = datetime.datetime.now()
        server_file.write(str(start_time) + " - Server started \n")    # log start time
        s.bind(('localhost', port))                             # Bind socket to port
        print("Socket binded to port " + str(port))
        s.listen(3)                                             # Wait for client connection.
        print("Waiting for a connection")
    except socket.error :                                       # eg. socket address already in use.
        s.close()
        s = None
    if s is None:                                               # end program if socket is none
        print("Could not open socket")
        sys.exit(1)
    while True:
        try:
            server_file.close()
            c, address = s.accept()                                 # Establish connection with client.
            server_file = open(filename, "a")
            server_file.write(str(datetime.datetime.now()) + " - Incoming client connection request \n")
            server_file.write(str(datetime.datetime.now()) + " - Successful connection \n")
            print("Got connection from ", address)
            success = "Request received successfully. Songs associated with artist: "
            c.sendall(success.encode())                             # Request for artist from client
            user_input = c.recv(1024)
            user_input = user_input.decode()                        # Receive artist from client
            result = []
            server_file.write(str(datetime.datetime.now()) + " - Artist name received: " + user_input + "\n")
            for i in hash_music:                                    # get artist(s) and compare with user input
                track = hash_music.get(i)
                if "/" in track[0]:
                    artists = track[0].split("/")                   # '/' implies more than one artist
                    for x in artists:
                        if user_input == x:
                            result.append(track[1].encode())
                else:
                    if user_input == track[0]:
                        result.append(track[1].encode())
            if not result:                                          # send "No songs found" if no matches
                result.append("No songs found".encode())
                result = pickle.dumps(result)
                c.sendall(result)
            else:                                                   # otherwise send results
                result = pickle.dumps(result)
                c.sendall(result)
            c.recv(1024)                                            # wait for user to input 'quit'
            end_time = datetime.datetime.now()
            time_connected = end_time - start_time
            server_file.write(
                str(end_time) + " - Client disconnected. Length of time connected: " + str(time_connected) + "\n")
            terminate_conn = "The connection has been closed."
            c.sendall(terminate_conn.encode())
            c.close()
            server_file.close()
        except socket.error:                                        # e.g. client disconnects mid communication
            print("Connection to client has been lost")
            server_file.write(str(datetime.datetime.now()) + " - Connection error \n")
            server_file.write(
                str(end_time) + " - Client disconnected. Length of time connected: " + str(time_connected) + "\n")
            server_file.close()
            sys.exit(1)


if __name__ == '__main__':
    main()
