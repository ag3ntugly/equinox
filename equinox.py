#!/usr/bin/env python3

import hashlib
import sys
import argparse
from datetime import datetime
from datetime import timedelta
import time
from math import trunc

total_start_time = datetime.now() #record the time, for later...
#a randomly generated 32 byte number to be used as known plaintext for identification and verification
magic_number = bytes.fromhex("84c399b360db6ef2757f40655ae66ad5fd8569f5e88d226d2307a7f38594217e")
#some color codes so i dont have to type them every time
R = "\033[0;31m"        #red
G = "\033[0;32m"        #green
LG = "\033[0;32m"       #light green
BLG = "\033[1;32m"      #bold light green
Y = "\033[0;33m"        #yellow
B = "\033[0;34m"        #blue
M =  "\033[0;35m"       #magenta
C = "\033[0;36m"        #cyan
W = "\033[0;37m"        #white
RS = "\033[0;0m"        #reset/default
P = G #this is the PRIMARY color, set it to whatever you feel like from the colors above
A = BLG #this is the ACCENT color, set it to whatever you feel like from the colors above
#terminal wizardy
UP = "\033[F"           #go up a line in the terminal
CHIDE = "\033[?25l"     #hide the cursor
CSHOW = "\033[?25h"     #show the cursor
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
def m_and_s (time):  #this is just a thing to turn a time object into minutes and seconds   
    minutes_and_seconds = f"{str(trunc(time.seconds / 60))}:{str((trunc(time.seconds % 60))).zfill(2)}"
    return minutes_and_seconds

def open_input_file(input_file): #open the original input_file for reading as bytes and return said bytes
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
    sample = input_bytes[:64] #read the first 64 bytes 
    if sample[:32] == magic_number: #check for the magic number in the first 32 bytes
        #if we find it, check the password by decrypting the last 32 bytes
        message("Encrypted input detected - Checking Password")
        hash = hashlib.blake2b(password.encode()) #generate a hash from the password
        sample_decrypted = bytearray(a ^ b for a, b in zip(sample[-32:], hash.digest())) #XOR that thang
        #check for magic number to verify the password
        if sample_decrypted == magic_number: #if we find the magic number again, return true            
            message("Password Verified{RS}")
            return True
        else: #if we dont find the magic number again, exit            
            error("Password Verification Failed")
            exit()
    else: #if we didnt find the magic number the first time, return false        
        return False

def write_output_file(file_name, file_data): #open output file for writing as bytes and write said bytes   
    try: 
        with open(file_name, 'wb') as ofile:
            ofile.write(file_data)
    except Exception as e:
        error(f"An unexpected error has occured: {R}{e}")

def generate_key(password, input_filesize):    
    key_start_time = datetime.now() #record the time for later
    lastupdate = datetime.now() #record the time for later
    count = 0 #set the counter to zero    
    print(CHIDE) #hide the cursor so we dont see it whipping around every time the progress bar updates
    hash = hashlib.blake2b(password.encode()) #create a blake2b hash of the input string
    key = hash.digest() #convert the hash to a type we can concatenate    
    while len(key) <= (input_filesize):  #chain hashes untill the key is big enough for the input
        next_hash = hashlib.blake2b(key[-32:]) #use the last 32 of the key as the seed for the next hash
        key = key + next_hash.digest() #type fuckery/concatenation
        count += 1 #increment the count
        timesince = datetime.now() - lastupdate #calculate the time since the last status update
        #if it has been longer than .01 seconds since the last time, update the progress bar and status messages
        if (((timesince.total_seconds()) >= .01) or (len(key) >= input_filesize)): 
            progress_percent = round(((len(key) / input_filesize) * 100)) #how far along are we?
            progress_pad = (" " * (3 - len(str(progress_percent)))) #pad the percentage
            progress_blocks = int(progress_percent / 3) #how many blocks in the progress bar?
            progress_bar = ("░" * progress_blocks) + (" " * (33 - progress_blocks)) #said number of blocks and some padding
            keytime_elapsed = (datetime.now() - key_start_time) #time so far for the key generation operation
            hashes_per_second = round(count / (keytime_elapsed.total_seconds())) #hashes per second, +1 in case the time is less than 1
            hashes_pad = (" " * (6 - len(str(hashes_per_second)))) #pad that baby
            bytes_per_second = (round((count * 64) / (keytime_elapsed.seconds + 1))) #bytes of key per second, +1 in case time is less than 1
            bytes_pad = (" " * (16 - len(str(convert_bytes(bytes_per_second))))) #PAD IT!
            keytime_total = timedelta(seconds=(round(input_filesize / bytes_per_second))) #estimate total time for operation
            keytime_remaining = keytime_total - keytime_elapsed #calculate remaining time based on total estimate
            lastupdate = datetime.now() #set this to now so that .01 seconds from now it'll know its time to do it again
            size = convert_bytes(len(key)) #get the size of the key
            size_pad = (" " * (16 - (len(str(size))))) #PPPPPAAAAAAAADDDDDDDDDD!!!!!!
            #print the progress bar and stats we just calculated
            print( 
            f"{UP}{UP}{P}[{A}={P}] Generating Key: {P}<{A}{progress_bar}{P}> "
            f"{A}{progress_pad}{progress_percent}{P}% "
            f"{A}{size_pad}{size} "
            )
            print(
            f"{P}[{A}={P}] {A}{m_and_s(keytime_elapsed)}{P} elapsed | "
            f"{A}{m_and_s(keytime_total)}{P} total | "
            f"{A}{m_and_s(keytime_remaining)}{P} remaining |"
            f"{A}{bytes_pad}{convert_bytes(bytes_per_second)}{P}/s |"
            f"{hashes_pad}{A}{hashes_per_second}{P}H/s         {RS}"
            )        
    total_keytime = datetime.now() - key_start_time #calculate the key generation time  
    print(CSHOW + UP) #unhide the cursor and go up a line
    message(f"Key Generated") #then print this message
    return key[:input_filesize], total_keytime

def decrypt(input_bytes):
    #Generate the full key
    key_bytes, key_time = generate_key(password, len(input_bytes))
    message(f"Decrypting file")
    start = datetime.now() #record the time for later
    input_bytes = input_bytes[32:]  #Trim off the first magic number and trim the key to match
    key_bytes = key_bytes[:len(input_bytes)]
    cipher_bytes = bytearray(a ^ b for a, b in zip(input_bytes, key_bytes)) #XOR that thang
    finish = datetime.now() - start #calulate the time it took to finish
    message(f"Decryption completed in {finish.total_seconds()} seconds")
    cipher_bytes = cipher_bytes[32:] #Trim off the 2nd magic number
    return key_bytes, key_time, cipher_bytes

def encrypt(input_bytes):
    #Generate the full key, 32 bytes bigger than the input file to account for the magic number
    key_bytes, key_time = generate_key(password, (len(input_bytes) + 32))
    message(f"Encrypting file")
    start = datetime.now() #record the time for later
    input_bytes = magic_number + input_bytes #add the magic number on the front
    key_bytes = key_bytes[:len(input_bytes)] #Trim the key to match in the input   
    cipher_bytes = bytearray(a ^ b for a, b in zip(input_bytes, key_bytes)) #XOR that thang
    finish = datetime.now() - start #calculate time it took to finish
    message(f"Encryption completed in {finish.total_seconds()} seconds")
    cipher_bytes = magic_number + cipher_bytes #prepend the magic number
    return key_bytes, key_time, cipher_bytes

def printslow(text,delay=0.002):
        for letter in text:
            print(letter, end='', flush=True)
            time.sleep(delay)
        print()

def message(message):
    printslow(f"{P}[{A}={P}] {message}{RS}")

def error(error):
    printslow(f"{P}[{R}!{P}] {error}{RS}")
    exit()

def convert_bytes(size): #i stole this from stack overflow ngl
    for x in [f'{P}bytes', f'{P}KB', f'{P}MB', f'{P}GB', f'{P}TB']:
        if size < 1024.0:
            return "%3.1f %s" % (size, x)
        size /= 1024.0
    return size

if __name__ == "__main__":
    try:
        #parse the arguments andset variables from args and stuff
        parser = argparse.ArgumentParser(usage=usage_text,description=help_text,epilog=f"{RS}",formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument("-p", "--password", type=str, required=True)
        parser.add_argument("-i", "--input", type=str, required=True)
        parser.add_argument("-o", "--output", type=str, required=False)
        args = parser.parse_args()
        password = args.password
        input_file = args.input
        if args.output:  #if the user has specified an output file name, set it to that
            output_file = args.output
        elif input_file.endswith(".eqx"): #if not, we check it for our magic extension indicating an already ecrypted file, and strip it off
            output_file = input_file[:-4]
        else: #otherwise assume we are encrypting and set it to the input file name with .eqx appended to it
            output_file = input_file + ".eqx"       
        #this is where actually do the thing
        print(help_text[:1256]) #print only the ascii and first line from the help text    
        input_bytes = open_input_file(input_file) #read in the input file
        message(f"Input file is {A}{convert_bytes(len(input_bytes))}")
        #determine if we're encrypting or decrypting and behave accordingly.
        if inspect(input_bytes) == True: #If True, we are decrypting
            message("Encrypted input file detected")
            message("Initiating decryption")
            key_bytes, key_time, cipher_bytes = decrypt(input_bytes) #call the decrypt function
        else: #if False, we are encrypting
            message("Plaintext input file detected")
            message("Initiating encryption")
            key_bytes, key_time, cipher_bytes = encrypt(input_bytes) #call the encrypt function
        message("Writing output to file") 
        write_output_file(output_file, cipher_bytes) #write the output to a file
        total_run_time = datetime.now() - total_start_time #calculate total run time, see i told you we'd need it later       
        #lets print some status messages right here then exit
        message(f"Encryption/Decryption completed in: {A}{m_and_s(total_run_time)}{P}.{RS}")
        message(f" Input bytes: {P}{convert_bytes(len(input_bytes))} {A}-{P} Input file is: {A}{input_file}{RS}")
        message(f"   Key bytes: {P}{convert_bytes(len(key_bytes))} {A}-{P} generated in: {A}{m_and_s(key_time)}{P}.{RS}")
        message(f"Output bytes: {P}{convert_bytes(len(cipher_bytes))} {A}-{P} Output file is: {A}{output_file}{RS} ")
        exit()
    except KeyboardInterrupt: #shut this baby down nicely upon CTRL-C because lord have mercy does it puke a bunch of nonsense if you dont
        error("Operation terminated")