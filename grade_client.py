from cryptography.fernet import Fernet
from grades_ClientServer import Client

import socket
import argparse
import sys
import csv



if __name__ == '__main__':


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

