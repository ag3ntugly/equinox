#!/usr/bin/python3

import hashlib
import os
import platform
import sys
from datetime import datetime

start_time = datetime.now()

def usage():
    message = '''
 _______   ________  ___  ___  ___  ________   ________     ___    ___ 
|\  ___ \ |\   __  \|\  \|\  \|\  \|\   ___  \|\   __  \   |\  \  /  /|
\ \   __/|\ \  \|\  \ \  \\\\\  \ \  \ \  \\\\ \  \ \  \|\  \  \ \  \/  / /
 \ \  \_|/_\ \  \\\\\  \ \  \\\\\  \ \  \ \  \\\\ \  \ \  \\\\\  \  \ \    / / 
  \ \  \_|\ \ \  \\\\\  \ \  \\\\\  \ \  \ \  \\\\ \  \ \  \\\\\  \  /     \/  
   \ \_______\ \_____  \ \_______\ \__\ \__\\\\ \__\ \_______\/  /\   \  
    \|_______|\|___| \__\|_______|\|__|\|__| \|__|\|_______/__/ /\ __\ 
                    \|__|                                  |__|/ \|__| 
                                                                       
                                                                       
Equinox - a terrible file encryption utility by ag3ntugly

Usage: equinox.py <password> <path_to_file>

Password can be any length, anything you can type, the longer the better.
File can be any old file you have need to obscure from eavesdroppers.
Produces a new file with .eqx appended to the end

The process for decrypting the file is identical to encrypting
just specify the .eqx file, and the origianl file will be unscrambulated.

If the wrong password is supplied, the result will be garbage.

This is neither fast nor efficient and takes a long time for large files.

It is probably also not very secure so you should not trust it with state secrets.
'''
    print(message)
    sys.exit(1)

def open_input_file(input_file):
    #open the original input_file for reading
    with open(input_file, 'rb',) as input:
        input_bytes = input.read()
    return input_bytes

def write_output_file(output_file, cypher_bytes):
    with open(output_file, 'wb') as output:
        output.write(cypher_bytes)

def generate_key_stream(password, input_filesize):
    keystream = ""
    #create a Blake2b of the input string
    hash = hashlib.blake2b(password.encode())
    keystream = hash.digest()
    #use the last 32 bytes of the initial hash as the seed for the next hash, add it to the first hash, and repeat untill it's as big as in the input file
    while len(keystream) <= input_filesize:
        next_hash = hashlib.blake2b(keystream[-32:])
        keystream = keystream + next_hash.digest()
    return keystream[:input_filesize]

def convert_bytes(size):
    #i stole this from stack overflow ngl
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return "%3.1f %s" % (size, x)
        size /= 1024.0

    return size

if __name__ == "__main__":
    if len(sys.argv) != 3: usage()
    

    password = sys.argv[1]
    input_file = sys.argv[2]
    if ".eqx" in input_file:
        output_file = input_file[:-4]
    else:
        output_file = input_file + ".eqx"
    print("[-] Beginning file encryption/decryption...")
    print("[-] Reading input file...")
    input_bytes = open_input_file(input_file)
    print("[-] Generating key...")
    key_bytes = generate_key_stream(password, len(input_bytes))    
    print("[-] Encrypting input file...")
    cipher_bytes = bytearray(a ^ b for a, b in zip(input_bytes, key_bytes))
    print("[-] Writing output file...")
    write_output_file(output_file, cipher_bytes)

    #lets have some status messages right here 
    print(f"input  bytes: {convert_bytes(len(input_bytes))}")
    print(f"key    bytes: {convert_bytes(len(key_bytes))}")
    print(f"cipher bytes: {convert_bytes(len(cipher_bytes))}")
    print(f"input filename is {input_file}")
    print(f"output filename is: {output_file}")
    print(f"Encryption/Decryption completed in {datetime.now() - start_time}")
