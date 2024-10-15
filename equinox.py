#!/usr/bin/env python3

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

check_value = bytes.fromhex("84c399b360db6ef2757f40655ae66ad5fd8569f5e88d226d2307a7f38594217e")

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
{M}\\ {C}\\   __/|{M}\\{C} \\  \\{M}|{C}\\  \\ \\  \\{M}\\{C}\\  \\ \\  \\ \\  \\{M}\\{C} \\  \\ \\  \\{M}|{C}\\  \\  {M}\\{C} \\  \\/  / {M}/
{M} \\ {C}\\  \\_|/_{M}\\{C} \\  \\{M}\\{C}\\  \\ \\  \\{M}\\{C}\\  \\ \\  \\ \\  \\{M}\\{C} \\  \\ \\  \\{M}\\{C}\\  \\  {M}\\{C} \\    / {M}/ 
{M}  \\ {C}\\  \\_|\\ {M}\\{C} \\  \\{M}\\{C}\\  \\ \\  \\{M}\\{C}\\  \\ \\  \\ \\  \\{M}\\{C} \\  \\ \\  \\{M}\\{C}\\  \\  /     \\{M}/  
{M}   \\ {C}\\_______{M}\\{C} \\_____  \\ \\_______\\ \\__\\ \\__\\\\ \\__\\ \\_______\\/  /\\   \\  
{M}    \\{M}|_______|\\|___| {C}\\__\\{M}|_______|\\|__|\\|__| \\|__|\\|_______{C}/__/ {M}/{C}\\ __\\ 
                    {M}\\|__|                                  |__|/ \\|__| 
                                                                       
      Equinox{C} a terrible file encryption utility by {G}ag3ntugly
     {M}Password{C} can be any length, whatever you want, the {M}longer{C} the {M}better{C}.
   {M}Input file{C} can be any old {M}file{C} you have need to {M}obscure{C} from {M}eavesdroppers{C}.
  {M}Output file{C} is a new file with {M}.eqx{C} appended to the name, created in the current
              directory unless an output file name/path is specified.

The process for {M}decrypting{C} the file is identical to {M}encrypting{C},
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
        print(f"{C}[{M}{R}!{C}] An unexpected error has occured: {R}{e}{RS}")
        sys.exit()
    return file_bytes

def write_output_file(output_file, output_bytes):
    #open output file for writing as bytes and write said bytes
    try:
        with open(output_file, 'wb') as ofile:
            ofile.write(output_bytes)
    except Exception as e:
        print(f"{C}[{M}{R}!{C}] An unexpected error has occured: {R}{e}{RS}")

def generate_key(password, input_filesize):
    #record the time, set counter to 0
    key_start_time = datetime.now()
    count = 0
    #create a blake2b hash of the input string
    hash = hashlib.blake2b(password.encode())
    key = hash.digest()
    #use the last 32 bytes of the initial hash as the seed for the next hash, add that hash to the first hash, and repeat untill it's as big as in the input file
    while len(key) <= input_filesize + 32:
        next_hash = hashlib.blake2b(key[-32:])
        key = key + next_hash.digest()
        count += 1
        #every hundred iterations, update the progress bar and status messages
        if ((count % 100) == 1):
            progress_percent = ((len(key) / input_filesize) * 100)
            progress_blocks = round(progress_percent / 2)
            progress_bar = ("■" * progress_blocks) + (" " * (50 - progress_blocks))
            keytime_elapsed = (datetime.now() - key_start_time)
            keytime_total = keytime_elapsed / (len(key) / input_filesize)
            keytime_remaining = keytime_total - keytime_elapsed
            bytes_per_second = round((count * 64) / (keytime_elapsed.seconds + .1))
            hashes_per_second = round(count / (keytime_elapsed.seconds + .1))
            print(f"\033[F{C}[{M}-{C}] Generating Key: {C}<{M}{progress_bar}{C}> {M}{round(progress_percent,1)}{C}% {convert_bytes(len(key))}     \n{C}[{M}-{C}] ({M}{m_and_s(keytime_elapsed)} {C}elapsed / {M}{m_and_s(keytime_total)}{C} total / {M}{m_and_s(keytime_remaining)} {C}remaining) : {M}{convert_bytes(bytes_per_second)}{C}/s : {M}{hashes_per_second} H{C}/S   {RS}" ,end="")
    #calculate the key generation time    
    total_keytime = datetime.now() - key_start_time
    #return the key trimmed to the exact length
    return key, total_keytime

def encrypt(input, key):
    print(f"{C}[{M}-{C}] Encrypting input file{RS}")
    input = input + check_value
    key_trimmed = key[:len(input)]
    cipher_bytes = bytearray(a ^ b for a, b in zip(input, key[:len(input)]))
    return cipher_bytes

def decrypt(input, key):    
    print(f"{C}[{M}-{C}] Detected encrypted input file. {RS}")
    print(f"{C}[{M}-{C}] Checking Password{RS}")
    key_trimmed = key[:len(input)]
    check_bytes = bytearray(a ^ b for a, b in zip(input[-32:], key_trimmed[-32:]))
    if check_bytes != check_value:
        print(f"{C}[{R}!{C}] Password invalid: please try again.{RS}")
        exit()
    else:
        print(f"{C}[{M}-{C}] Password appears valid: decrypting input file{RS}")
        cipher_bytes = bytearray(a ^ b for a, b in zip(input[:-32],key[:-32] ))
    return cipher_bytes

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

    #if the user has specified an output file name, set it to that
    if args.output:
        output_file = args.output

    #if not, we check it for our magic extension indicating an already ecrypted file, and strip it off
    elif ".eqx" in input_file:
        output_file = input_file[:-4]

    #otherwise set it to the input file name with .eqx appended to it
    else:
        output_file = input_file + ".eqx"
    
    #this is where actually do the thing
    print(f"{C}[{M}-{C}] Beginning file encryption/decryption{RS}")
    print(f"{C}[{M}-{C}] Reading input file{RS}")
    input_bytes = open_input_file(input_file)
    print(f"{C}[{M}-{C}] Input file is {M}{convert_bytes(len(input_bytes))}{RS}\n")
    key_bytes, key_time = generate_key(password, len(input_bytes))
    print(f"\n{C}[{M}-{C}] Key Generated{RS}")
    #determine if we're encrypting or decrypting and behave accordingly.    
    if ".eqx" in input_file:
        cipher_bytes = decrypt(input_bytes, key_bytes)
    else:    
        cipher_bytes = encrypt(input_bytes, key_bytes)

    #write result to output file
    print(f"{C}[{M}-{C}] Writing output to file{RS}")
    write_output_file(output_file, cipher_bytes)    
    #calculate total run time, see i told you we'd need it later
    total_time = datetime.now() - total_start_time
    
    #lets print some status messages right here then exit
    print(f"{C}[{M}-{C}] Encryption/Decryption completed in: {M}{m_and_s(total_time)}{C}.{RS}")
    print(f"{C}[{M}-{C}]    Key bytes: {C}{convert_bytes(len(key_bytes))} {M}-{C} generated in: {M}{m_and_s(key_time)}{C}.{RS}")
    print(f"{C}[{M}-{C}]  Input bytes: {C}{convert_bytes(len(input_bytes))} {M}-{C} Input file is: {M}{input_file}{RS}")
    print(f"{C}[{M}-{C}] Cipher bytes: {C}{convert_bytes(len(cipher_bytes))} {M}-{C} Output file is: {M}{output_file}{RS} ")
    exit()

    
