#!/usr/bin/python3

"""
Echo Client and Server Classes

T. D. Todd
McMaster University Group

to create a Client: "python EchoClientServer.py -r client" 
to create a Server: "python EchoClientServer.py -r server" 

or you can import the module into another file, e.g., 
import EchoClientServer
e.g., then do EchoClientserver.Server()

"""

########################################################################

import socket
import argparse
import sys
import csv
from cryptography.fernet import Fernet

########################################################################
# Echo Server class
########################################################################

class Server:

    # Set the server hostname used to define the server socket address
    # binding. Note that "0.0.0.0" or "" serves as INADDR_ANY. i.e.,
    # bind to all local network interfaces.
    # HOSTNAME = "192.168.1.22" # single interface    
    # HOSTNAME = "hornet"       # valid hostname (mapped to address/IF)
    # HOSTNAME = "localhost"    # local host (mapped to local address/IF)
    # HOSTNAME = "127.0.0.1"    # same as localhost
    HOSTNAME = "0.0.0.0"      # All interfaces.
    
    # Server port to bind the listen socket.
    PORT = 50000
    
    RECV_BUFFER_SIZE = 1024 # Used for recv.
    MAX_CONNECTION_BACKLOG = 10 # Used for listen.

    # We are sending text strings and the encoding to bytes must be
    # specified.
    MSG_ENCODING = "ascii" # ASCII text encoding.
    # MSG_ENCODING = "utf-8" # Unicode text encoding.

    # Create server socket address. It is a tuple containing
    # address/hostname and port.
    SOCKET_ADDRESS = (HOSTNAME, PORT)

    def __init__(self):
        file_path = 'course_grades_2024.csv'
        self.print_rows(file_path)
        self.create_listen_socket()
        self.process_connections_forever()

    def create_listen_socket(self):
        try:
            # Create an IPv4 TCP socket.
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Set socket layer socket options. This one allows us to
            # reuse the socket address without waiting for any timeouts.
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Bind socket to socket address, i.e., IP address and port.
            self.socket.bind(Server.SOCKET_ADDRESS)

            # Set socket to listen state.
            self.socket.listen(Server.MAX_CONNECTION_BACKLOG)
            print("Listening on port {} ...".format(Server.PORT))
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def process_connections_forever(self):
        try:
            while True:
                # Block while waiting for accepting incoming TCP
                # connections. When one is accepted, pass the new
                # (cloned) socket info to the connection handler
                # function. Accept returns a tuple consisting of a
                # connection reference and the remote socket address.
                self.connection_handler(self.socket.accept())
        except Exception as msg:
            print(msg)
        except KeyboardInterrupt:
            print()
        finally:
            # If something bad happens, make sure that we close the
            # socket.
            self.socket.close()
            sys.exit(1)

    def connection_handler(self, client):
        # Unpack the client socket address tuple.
        connection, address_port = client
        print("-" * 72)
        print("Connection received from {}.".format(address_port))
        # Output the socket address.
        print(client)
        
        try:
            # Receive bytes over the TCP connection. This will block
            # until "at least 1 byte or more" is available.
            recvd_bytes = connection.recv(Server.RECV_BUFFER_SIZE)

            # If recv returns with zero bytes, the other end of the
            # TCP connection has closed (The other end is probably in
            # FIN WAIT 2 and we are in CLOSE WAIT.). If so, close the
            # server end of the connection and get the next client
            # connection.
            if len(recvd_bytes) == 0:
                print("Closing client connection ... ")
                connection.close()
                
                        
            search_ID,command = self.decode_message(recvd_bytes)

            file_path = 'course_grades_2024.csv'


            matching_row = self.find_row_by_ID(file_path, search_ID)

            if matching_row:
                print("User Found: ", matching_row)
            else:
                print("User Not found Closing Connection")
                connection.close()
                return



            match command:
                case "GMA":
                    print("Fetching Midterm average.")
                    data = self.get_averages(file_path)[4]
                case "GL1A":
                    print("Fetching Lab 1 average.")
                    data = self.get_averages(file_path)[0]                    
                case "GL2A":
                    print("Fetching Lab 2 average.")
                    data = self.get_averages(file_path)[1] 
                case "GL3A":
                    print("Fetching Lab 3 average.")
                    data = self.get_averages(file_path)[2] 
                case "GL4A":
                    print("Fetching Lab 4average.")
                    data = self.get_averages(file_path)[3] 
                case "GEA":
                    print("Fetching Exam average.")
                    data = self.get_averages(file_path)[5] 
                case "GG":
                    print("Getting Grades.")
                    data = matching_row
                case _:
                    print("Invalid command entered.")
                    print("Closing client connection ... ")
                    connection.close()


            encryption_key_bytes= matching_row[2].encode('ascii')
            fernet = Fernet(encryption_key_bytes)
            data_str = str(data)  
            data_bytes = data_str.encode('ascii')
            encrypted_message_bytes = fernet.encrypt(data_bytes)

            # Send the received bytes back to the client. We are
            # sending back the raw data.
            connection.sendall(encrypted_message_bytes)
            print("Sent: ", encrypted_message_bytes)

        except KeyboardInterrupt:
            print()
            print("Closing client connection ... ")
            connection.close()
    
    def decode_message(self, message):

        # Decode the message (if necessary)
        decoded_message = message.decode('ascii')

        # Parsing the ID and command
        id_number = decoded_message[:7]  # first 7 bytes is the id number
        command = decoded_message[7:]    

        # Printing the results
        print("Full Message :", decoded_message)
    #    print("Command:", command)

        return id_number, command
    

    def find_row_by_ID(self, file_path, search_ID):

        with open(file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip the header row
            for row in reader:
                if row[1] == search_ID:
                    return row
        return None
    
    def get_averages(self,file_path):
        '''
        Array contents = [Lab 1,Lab 2,Lab 3,Lab 4,Midterm,Exam 1,Exam 2,Exam 3,Exam 4]
        '''
        grades = [0] * 9

        i = 3
        count =0
        with open(file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip the header row
            for row in reader:
                i = 3
                count = count + 1
                for j in range(9):
                    grades[j] += int(row[i])
                    #print(j)
                    i = i + 1

        
        for i in range (len(grades)):
            grades[i] = grades[i] / count


        return grades

    
    def print_rows(self, file_path):
        print('Data read from CSV file: \n')
        with open(file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip the header row
            for row in reader:
                print(row)
                    
        return None
########################################################################
# Echo Client class
########################################################################

class Client:

    # Set the server to connect to. If the server and client are running
    # on the same machine, we can use the current hostname.
    # SERVER_HOSTNAME = socket.gethostname()
    # SERVER_HOSTNAME = "192.168.1.22"
    SERVER_HOSTNAME = "localhost"
    
    # Try connecting to the compeng4dn4 echo server. You need to change
    # the destination port to 50007 in the connect function below.
    # SERVER_HOSTNAME = 'compeng4dn4.mooo.com'

    RECV_BUFFER_SIZE = 1024 # Used for recv.    
    # RECV_BUFFER_SIZE = 5 # Used for recv.    


    def __init__(self,message,id):
        self.ID_num = id
        self.full_message = message
        self.get_socket()
        self.connect_to_server()
        self.send_message()

    def get_socket(self):
        try:
            # Create an IPv4 TCP socket.
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Allow us to bind to the same port right away.            
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Bind the client socket to a particular address/port.
            # self.socket.bind((Server.HOSTNAME, 40000))
                
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def connect_to_server(self):
        try:
            # Connect to the server using its socket address tuple.
            self.socket.connect((Client.SERVER_HOSTNAME, Server.PORT))
            print("Connected to \"{}\" on port {}".format(Client.SERVER_HOSTNAME, Server.PORT))
        except Exception as msg:
            print(msg)
            sys.exit(1)

    
    def send_message(self):
        
        try:
            self.connection_send()
            self.connection_receive()
            print("Closing server connection ... gravceful")
            self.socket.close()
        except (KeyboardInterrupt, EOFError):
            print()
            print("Closing server connection ... Special")
            # If we get and error or keyboard interrupt, make sure
            # that we close the socket.
            self.socket.close()
            sys.exit(1)
                
    def connection_send(self):
        try:
            # Send string objects over the connection. The string must
            # be encoded into bytes objects first.
            self.socket.sendall(self.full_message)
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def connection_receive(self):
        try:
            # Receive and print out text. The received bytes objects
            # must be decoded into string objects.
            recvd_bytes = self.socket.recv(Client.RECV_BUFFER_SIZE)

            # recv will block if nothing is available. If we receive
            # zero bytes, the connection has been closed from the
            # other end. In that case, close the connection on this
            # end and exit.
            if len(recvd_bytes) == 0:
                print("Closing server connection ... ")
                self.socket.close()
                return



            file_path = 'course_grades_2024.csv'


            matching_row = self.find_row_by_ID(file_path, self.ID_num)
            
            if not matching_row:
                print("User Not found closing connection.")
                self.socket.close()
                return
            
            encryption_key_bytes = matching_row[2].encode('ascii')
            
            self.decrypt_message(recvd_bytes,encryption_key_bytes)

            #print("Received: ", recvd_bytes.decode(Server.MSG_ENCODING))

        except Exception as msg:
            print(msg)
            sys.exit(1)


    def decrypt_message(self, encrypted_message_bytes,key):


        # Decrypt the message after reception at the client.

        fernet = Fernet(key)
        decrypted_message_bytes = fernet.decrypt(encrypted_message_bytes)
        decrypted_message = decrypted_message_bytes.decode('utf-8')
        print("decrypted_message = ", decrypted_message)


    def find_row_by_ID(self, file_path, search_ID):

        with open(file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip the header row
            for row in reader:
                if row[1] == search_ID:
                    return row
        return None



########################################################################
# Process command line arguments if this module is run directly.
########################################################################

# When the python interpreter runs this module directly (rather than
# importing it into another file) it sets the __name__ variable to a
# value of "__main__". If this file is imported from another module,
# then __name__ will be set to that module's name.

if __name__ == '__main__':
    roles = {'client': Client,'server': Server}
    parser = argparse.ArgumentParser()

    parser.add_argument('-r', '--role',
                        choices=roles, 
                        help='server or client role',
                        required=True, type=str)

    args = parser.parse_args()

    if (roles[args.role] == Client):
        while True:
            id_number_input = input("Please Enter ID Number: ")
            command_input = input("Please Enter Command: GMA, GL1A, GL2A, GL3A, GL4A, GEA, GG: ")


            # encoding
            id_number_bytes = id_number_input.encode('ascii')
            command_bytes = command_input.encode('ascii')
            full_message = id_number_bytes + command_bytes

            print("Full message to be sent (in bytes):", full_message)
            #creating a new instance of the client
            Client(full_message, id_number_input)
    else:
        roles[args.role]()



########################################################################






