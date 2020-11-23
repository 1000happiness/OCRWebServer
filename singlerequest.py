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

if __name__ == "__main__":
    files= os.listdir("./imgs")
    body = {
        "file_type": "filename",
        "filename": "./imgs/invoice.png",
        "block_flag": True
    }
    res = requests.post(url, data=body)
    print("result: ", res.content)
    print("time: ", res.elapsed)