import multiprocessing
import threading
import copy
import os
import time
import cv2
import numpy as np
# from tornado import gen

class ImgStatus():
    PROCESSING = 0
    FINISHED = 1

class ImgOCRService():
    img_task_q = multiprocessing.Queue()
    img_result_q = multiprocessing.Queue()

    ocr_result_lock = threading.Lock()
    '''
    {
        filename: {
            mtime: @int
            timestamp: @int
            ocr_result: @list
            status: @enum
        }
    }
    '''
    ocr_result_dict = {}

    receive_loop_flag = False

    def __init__(self, configuration):
        self.cache_time = configuration["time"]
        self.cache_img_number = configuration["img_number"]

    async def get_ocr_result_by_filename(self, filename):
        redo_flag = False
        mtime = 0.0
        try:
            mtime = os.path.getmtime(filename)
        except FileNotFoundError as e:
            raise Exception("{} not exist".format(filename))

        self.ocr_result_lock.acquire()
        if filename in self.ocr_result_dict.keys():
            result = self.ocr_result_dict[filename]

            #检验图片是否正在被处理
            if result["status"] != ImgStatus.FINISHED:
                self.ocr_result_lock.release()
                return None
            
            #检验result dict对应的图片是否被修改过
            if result["mtime"] != mtime:
                self.ocr_result_dict.pop(filename)#如果图片被修改，那么需要重新进行OCR处理
                redo_flag = True
        else:
            redo_flag = True

        if(not redo_flag):
            ocr_result = copy.deepcopy(self.ocr_result_dict[filename]["ocr_result"])
            self.ocr_result_lock.release()
            return ocr_result
        else:
            #将需要处理的图片加入task queue
            self.ocr_result_dict[filename] = {
                "mtime": mtime,
                "timestamp": time.time(),
                "ocr_result": [],
                "status": ImgStatus.PROCESSING
            }
            self.img_task_q.put({
                "filename": filename,
                "file_type": "filename"
            })
            self.ocr_result_lock.release()
            return None

    async def get_ocr_result_by_file(self, file):
        redo_flag = False
        filename = hash(file)
        img = None
        try:
            img = np.frombuffer(file, dtype=np.uint8)
            img = cv2.imdecode(img, 1)         
        except Exception as e:
            print("formdata can't be decoded as img")
            raise e
        finally:
            if img is None:
                raise Exception("formdata can't be decoded as img")

        self.ocr_result_lock.acquire()
        if filename in self.ocr_result_dict.keys():
            result = self.ocr_result_dict[filename]
            #检验图片是否正在被处理
            if result["status"] != ImgStatus.FINISHED:
                self.ocr_result_lock.release()
                return None
        else:
            redo_flag = True

        if(not redo_flag):
            ocr_result = copy.deepcopy(self.ocr_result_dict[filename]["ocr_result"])
            self.ocr_result_lock.release()
            return ocr_result
        else:
            #将需要处理的图片加入task queue
            self.ocr_result_dict[filename] = {
                "mtime": time.time(),
                "timestamp": time.time(),
                "ocr_result": [],
                "status": ImgStatus.PROCESSING
            }
            self.img_task_q.put({
                "filename": filename,
                "file": file,
                "file_type": "file"
            })
            self.ocr_result_lock.release()
            return None

    def add_result(self, result):
        self.ocr_result_lock.acquire()
        filename = result["filename"]
        ocr_result = result["ocr_result"]
        if (filename in self.ocr_result_dict):
            self.ocr_result_dict[filename]["ocr_result"] = ocr_result
            self.ocr_result_dict[filename]["status"] = ImgStatus.FINISHED
        else:
            mtime = 0.0
            if(type(filename) == int):
                mtime = 0.0
            elif (type(filename) == str):
                try:
                    mtime = os.path.getmtime(filename.toString())
                except FileNotFoundError as e:
                    print("file {} not exist".format(filename))
                    return None
                
            self.ocr_result_dict[filename] = {
                "mtime": mtime,
                "timestamp": time.time(),
                "ocr_result": ocr_result,
                "status": ImgStatus.FINISHED
            }
        self.ocr_result_lock.release()
    
    def get_task_and_result_queue(self):
        return self.img_task_q, self.img_result_q

    def start_result_receive_loop(self):
        self.receive_loop_flag = True
        th = threading.Thread(target=self.result_receive_loop, daemon=True)
        th.start()

    def stop_result_receive_loop(self):
        self.receive_loop_flag = False

    def result_receive_loop(self):
        receive_num = 0
        while self.receive_loop_flag:
            result = self.img_result_q.get()
            self.add_result(result)
            receive_num += 1
            if(receive_num > self.cache_img_number):
                self.clear_result_cache()
                receive_num = 0

    def clear_result_cache(self):
        print("clear")
        self.ocr_result_lock.acquire()
        if len(self.ocr_result_dict) > self.cache_img_number:
            now = time.time()
            keys = list(self.ocr_result_dict.keys())
            for filename in keys:
                if(now - self.ocr_result_dict[filename]["timestamp"] > self.cache_time):
                    self.ocr_result_dict.pop(filename)
        
        if len(self.ocr_result_dict) > self.cache_img_number:
            keys = list(self.ocr_result_dict.keys())
            delete_num = len(keys) - self.cache_img_number // 2
            for i in range(delete_num):
                self.ocr_result_dict.pop(keys[i])

        self.ocr_result_lock.release()
    


