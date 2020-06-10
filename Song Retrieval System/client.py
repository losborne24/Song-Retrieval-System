import socket
import pickle
import sys
import datetime
import os

def main():
    
    client_file = open(os.path.abspath(os.path.join(os.path.dirname( __file__ ), "./logs/client.log")), "a")
    try:
        s = socket.socket()
    except socket.error:
        s = None
    port = 3125
    try:
        s.connect(('localhost', port))          # connect to server
    except socket.error:                        # e.g. server not running
        s.close()
        s = None
    if s is None:
        print("Could not open socket")
        sys.exit(1)
    z = input("Enter name of artist: ")
    while not z:
        print("No artist has been entered!")
        z = input("Enter name of artist: ")
    try:
        s.sendall(z.encode())
        send_time = datetime.datetime.now()
        re_req = s.recv(1024)                   # Successfully response received
        re_req = re_req.decode()
        print(re_req)
        songs = pickle.loads(s.recv(1024))
        receive_time = datetime.datetime.now()  # calculate latency
        client_file.write(str(receive_time) + " - Server response received \n")
        time_diff = receive_time - send_time
        client_file.write(
            str(receive_time) + " - Response time from server for the request to get songs by " + z + ": " + str(
                time_diff) + "\n")
        total_bytes = 0
        for song in songs:
            total_bytes += len(song)
            song = song.decode()
            print(song)
        client_file.write(str(receive_time) + " - Response length (in bytes): " + str(total_bytes) + "\n")
        q = ""
        while q != "quit":                      # terminate connection when 'quit' is entered
            q = input("Type 'quit' to disconnect from server. ")
        s.sendall(q.encode())
        term_conn = s.recv(1024)
        term_conn = term_conn.decode()
        print(term_conn)
        s.close()
        client_file.close()
    except socket.error:                        # e.g. server disconnects mid communication
        print("Connection to the server has been lost.")
        client_file.close()
        sys.exit(1)


if __name__ == '__main__':
    main()
