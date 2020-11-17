# 支持并发访问的OCR服务器

## 项目说明

* 这个项目基于[飞桨OCR](https://github.com/PaddlePaddle/PaddleOCR)搭建，使用torando框架实现并发访问服务

* 项目特点
1. 实现了简单的进程池，使用可配置的多进程运行识别模型，避免了原飞桨OCR中出现的无法利用多核CPU和内存占用过大的问题
2. 在识别的基础上加入了可配置的数据缓存，缓存已经识别的结果，减少了服务器对大量相同图片请求的冗余计算

## 快速启动
* 安装环境
```
#conda
conda env create -f requirement.yaml

#pip
pip install -r requirement.txt

#在windows下，直接安装的sharply库缺少链接库，需要手动安装，可访问链接 https://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml 自行下载安装
```
* 下载模型

下载[检测模型](https://paddleocr.bj.bcebos.com/20-09-22/mobile/det/ch_ppocr_mobile_v1.1_det_infer.tar)，[分类模型](https://paddleocr.bj.bcebos.com/20-09-22/cls/ch_ppocr_mobile_v1.1_cls_infer.tar)和[识别模型](https://paddleocr.bj.bcebos.com/20-09-22/mobile/rec/ch_ppocr_mobile_v1.1_rec_infer.tar)，将其解压放置在可以访问到的文件夹中，并在config.json中配置文件的位置，前往[飞桨OCR](https://github.com/PaddlePaddle/PaddleOCR)可以获取关于模型的更加详细的信息

* 修改配置

配置示例为如下json文件
```
{
    "web_server": {
        "port": 8888 //服务运行的端口
    },
    "ocr": {
        "process": {
            "number": 4, //识别进程数量
            "max_task_number": 20 //每个进程能够识别的图片数量
        },
        "predict_system": { //更多相关配置详见./extension/OCR/tools/infer/utility.py
            "enable_mkldnn": true, //开启mkldnn
            "det_model_dir": "./extension/OCR/model/ch_ppocr_mobile_v1.1_det_infer/", //检测模型路径
            "rec_model_dir": "./extension/OCR/model/ch_ppocr_mobile_v1.1_rec_infer/", //分类模型路径
            "cls_model_dir": "./extension/OCR/model/ch_ppocr_mobile_v1.1_cls_infer/" //识别模型路径
        }
    },
    "service": {
        "time": 6000, //图片缓存有效时间
        "img_number": 100 //图片缓存数量
    }
}
```

* 运行服务

```
#/bin/bash
python setup.py
```

* 运行测试

```
#运行前需要准备好图片，并修改测试文件中的端口
#/bin/bash
python multirequest.py
```
## 访问接口

* 访问示例
```
#通过文件名访问
files= os.listdir("./imgs")
body = {
    "file_type": "filename",
    "filename": "./imgs/" + files[random.randint(0, len(files) - 1)],
    "block_flag": True
}
res = requests.post("http://ip:port/ocr_service", data=body)

#上传文件访问
files= os.listdir("./imgs")
body = {
    "file_type": "file",
    "block_flag": True
}
upload_files = {'file': open("./imgs/" + files[random.randint(0, len(files) - 1)], 'rb')}
res = requests.post("http://ip:port/ocr_service", data=body, files=upload_files)
```
* 请求体说明
```
body = {
    "file_type": "filename", //@str 只能取两个值：filename或file，如果为file需要在在请求中加入formdata格式的文件（详见请求示例）
    "filename": "./imgs/" + files[random.randint(0, len(files) - 1)], //@str 当file_type为filename时，需要给出服务端能够访问到的文件路径
    "block_flag": True //@bool 为True时请求会阻塞到完成识别，为False时服务端会开始识别，但请求直接返回
}
```

## 并发性能
* 运行环境：R5 3600 + 32GB 3200 双通道内存
* 运行配置与文档中的示例配置相同
* 测试图片的平均识别时间为0.5秒，最少用时0.3秒，最大用时3秒
* 测试结果
1. 50个进程请求不同的未缓存的图片，请求平均用时4.8秒，请求用时最长为9秒
2. 50个进程请求相同的未缓存的图片，请求平均用时1.14秒，请求用时最长为1.5秒
3. 50个进程请求相同的已缓存的图片，请求平均用时0.01秒，请求用时最长为0.03秒