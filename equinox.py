#!/usr/bin/python3

import hashlib
import os
import platform
import sys
import argparse
from datetime import datetime
import math
from math import trunc
import time


#record the time, for later...
total_start_time = datetime.now()

#define some color codes so i dont have to remember this nonsense
R = "\033[91m"
G = "\033[92m"
Y = "\033[93m"
B = "\033[94m"
M =  "\033[95m"
C = "\033[96m"
W = "\033[97m"
RS = "\033[0m"

#help messages and shit
usage_text = f"{C}python equinox.py [-h/--help] -p/--password {M}PASSWORD{C} -i/--input {M}INPUT_FILE_PATH{C} [-o/--output {M}OUTPUT_FILE_PATH{C}]{RS}"

help_text = f'''

{C} _______   ________  ___  ___  ___  ________   ________     ___    ___ 
{M}|{C}\\  ___ \\ {M}|{C}\\   __  \\{M}|{C}\\  \\{M}|{C}\\  \\{M}|{C}\\  \\{M}|{C}\\   ___  \\{M}|{C}\\   __  \\   {M}|{C}\\  \\  /  /{M}|{C}
{M}\\ {C}\\   __/|{M}\\{C} \\  \\{M}|{C}\\  \\ \\  \\{M}\\{C}\\  \\ \\  \\ \\  \\{M}\\{C} \\  \\ \\  \\{M}|{C}\\  \\  \\ \\  \\/  / /
{M} \\ {C}\\  \\_|/_{M}\\{C} \\  \\{M}\\{C}\\  \\ \\  \\{M}\\{C}\\  \\ \\  \\ \\  \\{M}\\{C} \\  \\ \\  \\{M}\\{C}\\  \\  \\ \\    / / 
{M}  \\ {C}\\  \\_|\\ {M}\\{C} \\  \\{M}\\{C}\\  \\ \\  \\{M}\\{C}\\  \\ \\  \\ \\  \\{M}\\{C} \\  \\ \\  \\{M}\\{C}\\  \\  /     \\/  
{M}   \\ {C}\\_______{M}\\{C} \\_____  \\ \\_______\\ \\__\\ \\__\\\\ \\__\\ \\_______\\/  /\\   \\  
{M}    \\{M}|_______|\\|___| {C}\\__\\{M}|_______|\\|__|\\|__| \\|__|\\|_______{C}/__/ {M}/{C}\\ __\\ 
                    {M}\\|__|                                  |__|/ \\|__| 
                                                                       
                                                                       
      Equinox{C} a terrible file encryption utility by {G}ag3ntugly
     {M}Password{C} can be any length, whatever you want, the {M}longer{C} the {M}better{C}.
   {M}Input file{C} can be any old {M}file{C} you have need to {M}obscure{C} from {M}eavesdroppers{C}.
  {M}Output file{C} is a new file with {M}.eqx{C} appended to the name, created in the current
              directory unless an output file name/path is specified.

The process for {M}decrypting{C} the file is identical to {M}encrypting{C}
just specify the {M}.eqx{C} file as the input, and a new file without the {M}.eqx{C} extension
will be created in the current directory, unless an output file name/path is specified

If the {M}wrong password{C} is supplied, the result will be {M}garbage{C}.

This is {M}slow{C} and {M}iefficient{C} so it takes a long time for large files!

It is probably not very secure so you should not trust it with state secrets.

'''
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
        print(f"{C}[{M}{R}!{C}] File Not Found{RS}")
        sys.exit()
    except IOError:
        print(f"{C}[{M}{R}!{C}] Input/Output Error{RS}")
        sys.exit()
    except Exception as e:
        print(f"{C}[{M}{R}!{C}] An unexpected error has occuR: {R}{e}{RS}")
        sys.exit()
    return file_bytes

def write_output_file(output_file, output_bytes):
    #open a file for writing as bytes and write said bytes
    with open(output_file, 'wb') as ofile:
        ofile.write(output_bytes)

def generate_key(password, input_filesize):
    key_start_time = datetime.now()
    count = 0
    #create a blake2b hash of the input string
    hash = hashlib.blake2b(password.encode())
    key = hash.digest()
    #use the last 32 bytes of the initial hash as the seed for the next hash, add that hash to the first hash, and repeat untill it's as big as in the input file
    while len(key) <= input_filesize:
        next_hash = hashlib.blake2b(key[-32:])
        key = key + next_hash.digest()
        count += 1
        if ((count % 1000) == 1):
            progress_percent = ((len(key) / input_filesize) * 100)
            progress_blocks = round(progress_percent / 2)
            progress_bar = ("■" * progress_blocks) + (" " * (50 - progress_blocks))
            keytime_elapsed = (datetime.now() - key_start_time)
            keytime_total = keytime_elapsed / (len(key) / input_filesize)
            keytime_remaining = keytime_total - keytime_elapsed
            bytes_per_second = round((count * 64) / (keytime_elapsed.seconds + .1))
            hashes_per_second = round(count / (keytime_elapsed.seconds + .1))
            print(f"\033[F{C}[{M}-{C}] Generating Key: {C}<{M}{progress_bar}{C}> {M}{round(progress_percent,1)}{C}% {convert_bytes(len(key))}     \n{C}[{M}-{C}] ({M}{m_and_s(keytime_elapsed)} {C}elapsed / {M}{m_and_s(keytime_total)}{C} total / {M}{m_and_s(keytime_remaining)} {C}remaining) : {M}{convert_bytes(bytes_per_second)}{C}/s : {M}{hashes_per_second} H{C}/S   {RS}" ,end="")
        
    total_keytime = datetime.now() - key_start_time
    return key[:input_filesize], total_keytime

def convert_bytes(size):
    #i stole this from stack overflow ngl
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return "%3.1f %s" % (size, x)
        size /= 1024.0

    return size

if __name__ == "__main__":
    
    #parse the arguments
    parser = argparse.ArgumentParser(usage=usage_text,description=help_text,epilog=f"{RS}",formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-p", "--password", type=str, required=True)
    parser.add_argument("-i", "--input", type=str, required=True)
    parser.add_argument("-o", "--output", type=str, required=False)
    args = parser.parse_args()
    
    
    #set variables from args
    password = args.password
    input_file = args.input

    #check if it has our extension, and if so strip it and set output file name to that.
    if ".eqx" in input_file:
        output_file = input_file[:-4]
    #then check if a custom output filename was specified, in which case fuck that previous nonsense and set it to what they asked for, come what may
    elif args.output:
        output_file = args.output
    #otherwise set it to the input file name with .eqx appended to it
    else:
        output_file = input_file + ".eqx"
    
    #this is where actually do the thing
    print(f"{C}[{M}-{C}] Beginning file encryption/decryption{RS}")
    print(f"{C}[{M}-{C}] Reading input file{RS}")
    input_bytes = open_input_file(input_file)
    print(f"{C}[{M}-{C}] Input file is {M}{convert_bytes(len(input_bytes))}{RS}\n")
    key_bytes, key_time = generate_key(password, len(input_bytes))
    print(f"{C}[{M}-{C}] Key Generated{RS}")    
    print(f"{C}[{M}-{C}] Encrypting input file{RS}")
    cipher_bytes = bytearray(a ^ b for a, b in zip(input_bytes, key_bytes))
    print(f"{C}[{M}-{C}] Writing output file{RS}")
    write_output_file(output_file, cipher_bytes)

    #calculate total run time see i told you we'd need it later
    total_time = datetime.now() - total_start_time
    

    #lets print some status usage_texts right here 
    print(f"{C}[{M}-{C}] Encryption/Decryption completed in: {M}{m_and_s(total_time)}{C}.{RS}")
    print(f"{C}[{M}-{C}]    Key bytes: {C}{convert_bytes(len(key_bytes))} {M}-{C} generated in: {M}{m_and_s(key_time)}{C}.{RS}")
    print(f"{C}[{M}-{C}]  Input bytes: {C}{convert_bytes(len(input_bytes))} {M}-{C} Input file is: {M}{input_file}{RS}")
    print(f"{C}[{M}-{C}] Cipher bytes: {C}{convert_bytes(len(cipher_bytes))} {M}-{C} Output file is: {M}{output_file}{RS} ")

    
