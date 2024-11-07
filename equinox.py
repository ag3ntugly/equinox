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
R = "\033[91m"
G = "\033[92m"
LG = "\033[32m"
Y = "\033[93m"
B = "\033[94m"
M =  "\033[95m"
C = "\033[96m"
W = "\033[97m"
RS = "\033[0m"
#cursor hiding tomfoolery
CHIDE = "\033[?25l"
CSHOW = "\033[?25h"
#help messages
usage_text = f"{C}python equinox.py [-h/--help] -p/--password {M}PASSWORD{C} -i/--input {M}INPUT_FILE_PATH{C} [-o/--output {M}OUTPUT_FILE_PATH{C}]{RS}"
help_text = f'''
{C} _______   ________  ___  ___  ___  ________   ________     ___    ___ 
{M}|{C}\\  ___ \\ {M}|{C}\\   __  \\{M}|{C}\\  \\{M}|{C}\\  \\{M}|{C}\\  \\{M}|{C}\\   ___  \\{M}|{C}\\   __  \\   {M}|{C}\\  \\  /  /{M}|{C}
{M}\\ {C}\\   __/|{M}\\{C} \\  \\{M}|{C}\\  \\ \\  \\{M}\\{C}\\  \\ \\  \\ \\  \\{M}\\{C} \\  \\ \\  \\{M}|{C}\\  \\  {M}\\{C} \\  \\/  / {M}/
{M} \\ {C}\\  \\_|/_{M}\\{C} \\  \\{M}\\{C}\\  \\ \\  \\{M}\\{C}\\  \\ \\  \\ \\  \\{M}\\{C} \\  \\ \\  \\{M}\\{C}\\  \\  {M}\\{C} \\    / {M}/ 
{M}  \\ {C}\\  \\_|\\ {M}\\{C} \\  \\{M}\\{C}\\  \\ \\  \\{M}\\{C}\\  \\ \\  \\ \\  \\{M}\\{C} \\  \\ \\  \\{M}\\{C}\\  \\  /     \\{M}/  
{M}   \\ {C}\\_______{M}\\{C} \\_____  \\ \\_______\\ \\__\\ \\__\\\\ \\__\\ \\_______\\/  /\\   \\  
{M}    \\{M}|_______|\\|___| {C}\\__\\{M}|_______|\\|__|\\|__| \\|__|\\|_______{C}/__/ {M}/{C}\\ __\\ 
                    {M}\\|__|                                  |__|/ \\|__| 
                                                                       
      Equinox{C} a terrible file encryption utility by {C}ag3ntugly
     {M}Password{C} can be any length, whatever you want, the {M}longer{C} the {M}better{C}.
   {M}Input file{C} can be any old {M}file{C} you have need to {M}obscure{C} from {M}eavesdroppers{C}.
  {M}Output file{C} is a new file with {M}.eqx{C} appended to the name, created in the current
              directory unless an output file name/path is specified.

The process for {M}decrypting{C} the file is identical to {M}encrypting{C},
just specify the {M}.eqx{C} file as the input, and a new file without the {M}.eqx{C} extension
will be created in the current directory, unless an output file name/path is specified

This is {M}slow{C} and {M}iefficient{C} so it takes a long time for large files!
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
        #every hundredth iterations, update the progress bar and status messages
        if (((timesince.total_seconds()) >= .1) or (len(key) >= input_filesize)):
            progress_percent = ((len(key) / input_filesize) * 100)
            progress_blocks = round(progress_percent / 10)
            progress_bar = ("■" * progress_blocks) + (" " * (10 - progress_blocks))
            keytime_elapsed = (datetime.now() - key_start_time)
            hashes_per_second = round(count / (keytime_elapsed.seconds + 1))
            bytes_per_second = round((count * 64) / (keytime_elapsed.seconds + 1))
            keytime_total = timedelta(seconds=(round(input_filesize / bytes_per_second))) 
            keytime_remaining = keytime_total - keytime_elapsed
            
            lastupdate = datetime.now()
            print(f"\033[F{C}[{M}-{C}] Generating Key: {C}<{M}{progress_bar}{C}> {M}{round(progress_percent,1)}{C}% {M}{convert_bytes(len(key))} ({M}{m_and_s(keytime_elapsed)}{C}E | {M}{m_and_s(keytime_total)}{C}T | {M}{m_and_s(keytime_remaining)}{C}R) ({M}{convert_bytes(bytes_per_second)}{C}/s | {M}{hashes_per_second}{C}H/s)         {RS}")
    #calculate the key generation time    
    total_keytime = datetime.now() - key_start_time  
    #print a status message and show the cursor again
    message(f"Key Generated.{CSHOW}")
    #return the key
    return key[:input_filesize], total_keytime

def decrypt(input_bytes):
    #Generate the full key
    key_bytes, key_time = generate_key(password, len(input_bytes))
    #Trim off the first magic number and trim the key to match
    input_bytes = input_bytes[32:]
    key_bytes = key_bytes[:len(input_bytes)]
    #bitwise XOR that thang
    cipher_bytes = bytearray(a ^ b for a, b in zip(input_bytes, key_bytes))
    #Trim off the 2nd magic number
    cipher_bytes = cipher_bytes[32:]
    #Write the output to file
    #write_output_file(output_file, cipher_bytes)
    return key_bytes, key_time, cipher_bytes

def encrypt(input_bytes):
    #Generate the full key, 32 bytes bigger than the input file to account for the magic number
    key_bytes, key_time = generate_key(password, (len(input_bytes) + 32))
    #add the magic number on the front
    input_bytes = magic_number + input_bytes
    #Trim the key to match in the input
    key_bytes = key_bytes[:len(input_bytes)]
    #bitwise XOR that thang
    cipher_bytes = bytearray(a ^ b for a, b in zip(input_bytes, key_bytes))
    #write the output to a file with the magic number pre-pended in cleartext
    cipher_bytes = magic_number + cipher_bytes
    #write_output_file(output_file, cipher_bytes)
    return key_bytes, key_time, cipher_bytes

def printslow(text):
    delay = 0.002
    for letter in text:
        print(letter, end='', flush=True)
        #print("\a", end='', flush=True)
        time.sleep(delay)
    print()

def message(message):
    printslow(f"{C}[{M}-{C}] {message}{RS}")

def error(error):
    printslow(f"{C}[{R}!{C}] {error}{RS}")
    exit()

def convert_bytes(size):
    #i stole this from stack overflow ngl
    for x in [f'{C}bytes', f'{C}KB', f'{C}MB', f'{C}GB', f'{C}TB']:
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
    try:
        #read in the input file
        input_bytes = open_input_file(input_file)
        message(f"Input file is {M}{convert_bytes(len(input_bytes))}")
        #determine if we're encrypting or decrypting and behave accordingly.
        if inspect(input_bytes) == True:
            #If True, we are de-crypting
            message(f"Encrypted input file detected - Initiating decryption{RS}")
            key_bytes, key_time, cipher_bytes = decrypt(input_bytes)
            message(f"Decryption completed.{RS}")
        else:
            #if False, we are encrypting
            message(f"Raw input file detected - Initiating encryption{RS}")
            key_bytes, key_time, cipher_bytes = encrypt(input_bytes)
            message(f"Encryption completed.{RS}")
        message("Writing output to file")
        write_output_file(output_file, cipher_bytes)
        #calculate total run time, see i told you we'd need it later
        total_run_time = datetime.now() - total_start_time        
        #lets print some status messages right here then exit
        message(f"Encryption/Decryption completed in: {M}{m_and_s(total_run_time)}{C}.{RS}")
        message(f" Input bytes: {C}{convert_bytes(len(input_bytes))} {M}-{C} Input file is: {M}{input_file}{RS}")
        message(f"   Key bytes: {C}{convert_bytes(len(key_bytes))} {M}-{C} generated in: {M}{m_and_s(key_time)}{C}.{RS}")
        message(f"Output bytes: {C}{convert_bytes(len(cipher_bytes))} {M}-{C} Output file is: {M}{output_file}{RS} ")
        exit()
    except KeyboardInterrupt:
        error("Operation terminated")

    
