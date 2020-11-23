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
    result = str(res.content, encoding="utf-8")
    result_json = json.loads(result)
    # with open("test.json", "w") as f:
    #     result_json.dump(f, indent=4)
    for i in range(len(result_json)):
        print(result_json[i][0], result_json[i][1][0])
    print("time: ", res.elapsed)
    