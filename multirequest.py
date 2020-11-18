import numpy as np
import requests
import multiprocessing
import os
import random
import json

ip = "localhost"
configuration = {}
with open("config.json") as f:
    configuration = json.load(f)
port = configuration["web_server"]["port"]
url = "http://{}:{}/ocr_service".format(ip, port)

def random_img_filename(q):
    files= os.listdir("./imgs")
    body = {
        "file_type": "filename",
        "filename": "./imgs/" + files[random.randint(0, len(files) - 1)],
        "block_flag": True
    }
    res = requests.post(url, data=body)
    print("random img filename", res.elapsed)
    q.put(res.elapsed)

def same_img_filename(q):
    files= os.listdir("./imgs")
    body = {
        "file_type": "filename",
        "filename": "./imgs/" + files[0],
        "block_flag": True
    }
    res = requests.post(url, data=body)
    print("same img filename", res.elapsed)
    q.put(res.elapsed)

def random_img_file(q):
    files= os.listdir("./imgs")
    body = {
        "file_type": "file",
        "block_flag": True
    }
    upload_files = {'file': open("./imgs/" + files[random.randint(0, len(files) - 1)], 'rb')}
    res = requests.post(url, data=body, files=upload_files)
    print("random img file:", res.elapsed)
    q.put(res.elapsed)

if __name__ == "__main__":
    q = multiprocessing.Queue()
    num = 1
    for i in range(num):
        # multiprocessing.Process(target=random_img_filename, args=(q,)).start()
        # multiprocessing.Process(target=random_img_file, args=(q,)).start()
        multiprocessing.Process(target=same_img_filename, args=(q,)).start()

    i = 0
    time = []
    while True:
        time.append(q.get())
        i += 1
        if(i == num):
            break
    print(np.array(time).mean(), np.array(time).max())