#!/usr/bin/env python3

import hashlib
import os
import platform
import sys
import argparse
from datetime import datetime
from datetime import timedelta
from datetime import time as dtime
import time
#import math
from math import trunc

#record the time, for later...
total_start_time = datetime.now()
#a randomly generated 32 byte number to be used as known plaintext for identification and verification
magic_number = bytes.fromhex("84c399b360db6ef2757f40655ae66ad5fd8569f5e88d226d2307a7f38594217e")
#some color codes so i dont have to remember this nonsense
R = "\033[0;91m"
G = "\033[0;32m"
LG = "\033[0;92m"
BLG = "\033[1;92m"
Y = "\033[0;93m"
B = "\033[0;94m"
M =  "\033[0;95m"
C = "\033[0;96m"
W = "\033[0;97m"
RS = "\033[0;0m"
P = G
A = BLG
#terminal wizardy
UP = "\033[F"
CHIDE = "\033[?25l"
CSHOW = "\033[?25h"
#help messages
usage_text = f"{P}python equinox.py [-h/--help] -p/--password {A}PASSWORD{P} -i/--input {A}INPUT_FILE_PATH{P} [-o/--output {A}OUTPUT_FILE_PATH{P}]{RS}"
help_text = f'''
{P} _______   ________  ___  ___  ___  ________   ________     ___    ___ 
{A}|{P}\\  ___ \\ {A}|{P}\\   __  \\{A}|{P}\\  \\{A}|{P}\\  \\{A}|{P}\\  \\{A}|{P}\\   ___  \\{A}|{P}\\   __  \\   {A}|{P}\\  \\  /  /{A}|{P}
{A}\\ {P}\\   __/|{A}\\{P} \\  \\{A}|{P}\\  \\ \\  \\{A}\\{P}\\  \\ \\  \\ \\  \\{A}\\{P} \\  \\ \\  \\{A}|{P}\\  \\  {A}\\{P} \\  \\/  / {A}/
{A} \\ {P}\\  \\_|/_{A}\\{P} \\  \\{A}\\{P}\\  \\ \\  \\{A}\\{P}\\  \\ \\  \\ \\  \\{A}\\{P} \\  \\ \\  \\{A}\\{P}\\  \\  {A}\\{P} \\    / {A}/ 
{A}  \\ {P}\\  \\_|\\ {A}\\{P} \\  \\{A}\\{P}\\  \\ \\  \\{A}\\{P}\\  \\ \\  \\ \\  \\{A}\\{P} \\  \\ \\  \\{A}\\{P}\\  \\  /     \\{A}/  
{A}   \\ {P}\\_______{A}\\{P} \\_____  \\ \\_______\\ \\__\\ \\__\\\\ \\__\\ \\_______\\/  /\\   \\  
{A}    \\{A}|_______|\\|___| {P}\\__\\{A}|_______|\\|__|\\|__| \\|__|\\|_______{P}/__/ {A}/{P}\\ __\\ 
                    {A}\\|__|{P}                                 {A}|__|/ \\|__| 
                                                                       
      Equinox{P} a terrible file encryption utility by {P}ag3ntugly
     {A}Password{P} can be any length, whatever you want, the {A}longer{P} the {A}better{P}.
   {A}Input file{P} can be any old {A}file{P} you have need to {A}obscure{P} from {A}eavesdroppers{P}.
  {A}Output file{P} is a new file with {A}.eqx{P} appended to the name, created in the current
              directory unless an output file name/path is specified.

The process for {A}decrypting{P} the file is identical to {A}encrypting{P},
just specify the {A}.eqx{P} file as the input, and a new file without the {A}.eqx{P} extension
will be created in the current directory, unless an output file name/path is specified

This is {A}slow{P} and {A}iefficient{P} so it takes a long time for large files!
It is probably not very secure so you should not trust it with state secrets.
'''
def clear_screen():
    # Check the operating system and issue the appropriate command
    if platform.system().lower() == "windows":
        os.system("cls")  # Windows command to clear the screen
    else:
        os.system("clear")  # Linux or macOS command to clear the screen

def m_and_s (time):
    #this is just a thing to turn a time object into minutes and seconds
    minutes_and_seconds = f"{str(trunc(time.seconds / 60))}:{str((trunc(time.seconds % 60))).zfill(2)}"
    return minutes_and_seconds

def open_input_file(input_file):
    #open the original input_file for reading as bytes and return said bytes
    try:
        with open(input_file, 'rb',) as ifile:
            file_bytes = ifile.read()
    except FileNotFoundError:
        error("File Not Found")
        sys.exit()
    except IOError:
        error("Input/Output Error")
        sys.exit()
    except Exception as e:
        error(f"An unexpected error has occured: {R}{e}{RS}")
        sys.exit()
    return file_bytes

def inspect(input_bytes):
    #read the first 32 bytes and check for the magic number
    sample = input_bytes[:64]
    if sample[:32] == magic_number:
        #if we find it, check the password by decrypting the last 32 bytes
        message("Encrypted input detected - Checking Password")
        hash = hashlib.blake2b(password.encode())
        sample_decrypted = bytearray(a ^ b for a, b in zip(sample[-32:], hash.digest()))
        #check for magic number to verify the password
        if sample_decrypted == magic_number:
            #if we find the magic number again, return true
            message("Password Verified{RS}")
            return True
        else:
            #if we dont find the magic number again, exit
            error("Password Verification Failed")
            exit()
    else:
        #if we didnt find the magic number the first time, return false
        return False

def write_output_file(file_name, file_data):
    #open output file for writing as bytes and write said bytes, with the magic number prepended to it
    try:
        with open(file_name, 'wb') as ofile:
            ofile.write(file_data)
    except Exception as e:
        error(f"An unexpected error has occured: {R}{e}")

def generate_key(password, input_filesize):
    #record the time, set counter to 0
    key_start_time = datetime.now()
    lastupdate = datetime.now()
    count = 0
    #hide the cursor so we dont see it whipping around every time the progress bar updates
    print(CHIDE)
    #create a blake2b hash of the input string
    hash = hashlib.blake2b(password.encode())
    key = hash.digest()
    #use the last 32 bytes of the initial hash as the seed for the next hash, add that hash to the first hash, and repeat untill it's as big as in the input file
    while len(key) <= (input_filesize):        
        next_hash = hashlib.blake2b(key[-32:])
        key = key + next_hash.digest()
        count += 1
        timesince = datetime.now() - lastupdate
        #every .01 seconds, update the progress bar and status messages
        if (((timesince.total_seconds()) >= .01) or (len(key) >= input_filesize)):
            progress_percent = round(((len(key) / input_filesize) * 100))
            progress_blocks = int(progress_percent / 3)
            progress_bar = ("#" * progress_blocks) + (" " * (33 - progress_blocks))
            keytime_elapsed = (datetime.now() - key_start_time)
            hashes_per_second = round(count / (keytime_elapsed.seconds + 1))
            bytes_per_second = (round((count * 64) / (keytime_elapsed.seconds + 1)))
            keytime_total = timedelta(seconds=(round(input_filesize / bytes_per_second))) 
            keytime_remaining = keytime_total - keytime_elapsed            
            lastupdate = datetime.now()
            size = convert_bytes(len(key))
            print(f"{UP}{UP}{P}[{A}-{P}] Generating Key: {P}<{A}{progress_bar}{P}> {A}{" " * (4 - len(str(progress_percent)))}{progress_percent}{P}%{A}{" " * (14 - (len(size)))}{size}")
            print(f"{P}[{A}-{P}] {A}{m_and_s(keytime_elapsed)}{P} elapsed | {A}{m_and_s(keytime_total)}{P} total | {A}{m_and_s(keytime_remaining)}{P} remaining | {A}{" " * (13 - len(str(convert_bytes(bytes_per_second))))} {str(convert_bytes(bytes_per_second))}{P}/s |{" " * (5 - len(str(hashes_per_second)))}{A}{hashes_per_second}{P}H/s         {RS}")
        
    #calculate the key generation time    
    total_keytime = datetime.now() - key_start_time  
    #unhide the cursor/print a newline, then a status message
    print(CSHOW + UP)
    message(f"Key Generated")
    #return the key
    return key[:input_filesize], total_keytime

def decrypt(input_bytes):
    #Generate the full key
    key_bytes, key_time = generate_key(password, len(input_bytes))
    message(f"Decrypting file")
    start = datetime.now()
    #Trim off the first magic number and trim the key to match
    input_bytes = input_bytes[32:]
    key_bytes = key_bytes[:len(input_bytes)]
    #XOR that thang
    cipher_bytes = bytearray(a ^ b for a, b in zip(input_bytes, key_bytes))
    finish = datetime.now() - start
    message(f"Decryption completed in {finish.total_seconds()} seconds")
    #Trim off the 2nd magic number
    cipher_bytes = cipher_bytes[32:]
    return key_bytes, key_time, cipher_bytes

def encrypt(input_bytes):
    #Generate the full key, 32 bytes bigger than the input file to account for the magic number
    key_bytes, key_time = generate_key(password, (len(input_bytes) + 32))
    message(f"Encrypting file")
    start = datetime.now()
    #add the magic number on the front
    input_bytes = magic_number + input_bytes
    #Trim the key to match in the input
    key_bytes = key_bytes[:len(input_bytes)]
    #XOR that thang
    cipher_bytes = bytearray(a ^ b for a, b in zip(input_bytes, key_bytes))
    finish = datetime.now() - start
    message(f"Encryption completed in {finish.total_seconds()} seconds")
    #prepend the magic number
    cipher_bytes = magic_number + cipher_bytes
    return key_bytes, key_time, cipher_bytes

def printslow(text,delay=0.002):
        for letter in text:
            print(letter, end='', flush=True)
            time.sleep(delay)
        print()

def message(message):
    printslow(f"{P}[{A}-{P}] {message}{RS}")

def error(error):
    printslow(f"{P}[{R}!{P}] {error}{RS}")
    exit()

def convert_bytes(size):
    #i stole this from stack overflow ngl
    for x in [f'{P}bytes', f'{P}KB', f'{P}MB', f'{P}GB', f'{P}TB']:
        if size < 1024.0:
            return "%3.1f %s" % (size, x)
        size /= 1024.0
    return size

if __name__ == "__main__":
    #parse the arguments andset variables from args and stuff
    parser = argparse.ArgumentParser(usage=usage_text,description=help_text,epilog=f"{RS}",formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-p", "--password", type=str, required=True)
    parser.add_argument("-i", "--input", type=str, required=True)
    parser.add_argument("-o", "--output", type=str, required=False)
    args = parser.parse_args()
    password = args.password
    input_file = args.input
    #if the user has specified an output file name, set it to that
    if args.output:
        output_file = args.output
    #if not, we check it for our magic extension indicating an already ecrypted file, and strip it off
    elif input_file.endswith(".eqx"): 
        output_file = input_file[:-4]
    #otherwise assume we are encrypting and set it to the input file name with .eqx appended to it
    else: 
        output_file = input_file + ".eqx"       
    #this is where actually do the thing
    print(help_text[:1256])
    try:
        #read in the input file
        input_bytes = open_input_file(input_file)
        message(f"Input file is {A}{convert_bytes(len(input_bytes))}")
        #determine if we're encrypting or decrypting and behave accordingly.
        if inspect(input_bytes) == True:
            #If True, we are de-crypting
            message("Encrypted input file detected")
            message("Initiating decryption")
            key_bytes, key_time, cipher_bytes = decrypt(input_bytes)
        else:
            #if False, we are encrypting
            message("Plaintext input file detected")
            message("Initiating encryption")
            key_bytes, key_time, cipher_bytes = encrypt(input_bytes)
        message("Writing output to file")
        write_output_file(output_file, cipher_bytes)
        #calculate total run time, see i told you we'd need it later
        total_run_time = datetime.now() - total_start_time        
        #lets print some status messages right here then exit
        message(f"Encryption/Decryption completed in: {A}{m_and_s(total_run_time)}{P}.{RS}")
        message(f" Input bytes: {P}{convert_bytes(len(input_bytes))} {A}-{P} Input file is: {A}{input_file}{RS}")
        message(f"   Key bytes: {P}{convert_bytes(len(key_bytes))} {A}-{P} generated in: {A}{m_and_s(key_time)}{P}.{RS}")
        message(f"Output bytes: {P}{convert_bytes(len(cipher_bytes))} {A}-{P} Output file is: {A}{output_file}{RS} ")
        exit()
    except KeyboardInterrupt:
        error("Operation terminated")

    
