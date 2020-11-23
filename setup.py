
from webserver.application import make_app
from webserver.webserver import WebServer
from service.imgOCRservice import ImgOCRService
from extension.OCR.OCRmanager import OCRManager

import json

if __name__ == '__main__':
    configuration = {}
    with open("config.json") as f:
        configuration = json.load(f)

    img_ocr_service = ImgOCRService(configuration["service"])
    ocr_manager = OCRManager(configuration["ocr"], img_ocr_service)
    application = make_app(img_ocr_service)
    web_server = WebServer(configuration["web_server"], application)

    img_ocr_service.start_result_receive_loop()
    ocr_manager.start_process_management()
    print("Web server in port {0} start".format(configuration["web_server"]["port"]))
    web_server.start_block()