import requests
import multiprocessing
import os
import random

def random_img_filename():
    files= os.listdir("./imgs")
    body = {
        "file_type": "filename",
        "filename": "./imgs/" + files[random.randint(0, len(files) - 1)],
        "block_flag": True
    }
    res = requests.post("http://localhost:8888/ocr_service", data=body)
    print("random img filename", res.elapsed)

def same_img_filename():
    files= os.listdir("./imgs")
    body = {
        "file_type": "filename",
        "filename": "./imgs/" + files[0],
        "block_flag": True
    }
    res = requests.post("http://localhost:8888/ocr_service", data=body)
    print("same img filename", res.elapsed)

def random_img_file():
    files= os.listdir("./imgs")
    body = {
        "file_type": "file",
        "block_flag": True
    }
    upload_files = {'file': open("./imgs/" + files[random.randint(0, len(files) - 1)], 'rb')}
    res = requests.post("http://localhost:8888/ocr_service", data=body, files=upload_files)
    print("random img file:", res.elapsed)

if __name__ == "__main__":
    for i in range(30):
        multiprocessing.Process(target=random_img_filename, args=()).start()
        multiprocessing.Process(target=random_img_file, args=()).start()
        multiprocessing.Process(target=same_img_filename, args=()).start()