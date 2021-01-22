from tornado import web, gen
import json
import numpy as np
import cv2

class ImgOCRHandler(web.RequestHandler):
    def initialize(self, img_ocr_service):
        self.img_ocr_service = img_ocr_service

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*') 
        self.set_header('Access-Control-Allow-Headers', 'x-requested-with')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, PUT, DELETE')

    async def post(self):
        data = json.loads(self.request.body)
        file_type = None
        block_flag = None
        try:
            file_type = data["file_type"]
            block_flag = data["block_flag"]
        except Exception as e:
            self.send_error(400)

        if file_type == "filename":
            filename = None
            try:
                filename = data["filename"]
            except Exception as e:
                self.send_error(400)

            result = None
            while True:
                try:
                    result = await self.img_ocr_service.get_ocr_result_by_filename(filename)
                except Exception as e:
                    self.send_error(500, message=str(e))
                    return

                if(result == None and block_flag):
                    await gen.sleep(0.5)
                    continue
                else:
                    break

            self.write(json.dumps(result, ensure_ascii=False))
            return
        elif file_type == "file":
            if("file" not in self.request.files or len(self.request.files["file"]) < 1):
                print(len(self.request.files["file"]))
                self.send_error(500)
                return
            file_meta = self.request.files["file"][0]
            file_content = file_meta["body"]

            result = None
            while True:
                try:
                    result = await self.img_ocr_service.get_ocr_result_by_file(file_content)
                except Exception as e:
                    self.send_error(500, message=str(e))
                    return

                if(result == None and block_flag):
                    await gen.sleep(0.5)
                    continue
                else:
                    break         

            self.write(json.dumps(result, ensure_ascii=False))
        elif file_type == "base64":
            src = None
            try:
                src = data["img_src"]
            except Exception as e:
                self.send_error(400)

            result = None
            while True:
                try:
                    result = await self.img_ocr_service.get_ocr_result_by_base64(src)
                except Exception as e:
                    self.send_error(500, message=str(e))
                    return
                if(result == None and block_flag):
                    await gen.sleep(0.5)
                    continue
                else:
                    break         

            self.write(json.dumps(result, ensure_ascii=False))
        else:
            self.send_error(400)
            return

    def write_error(self, status_code, **kwargs):
        if("message" in kwargs):
            self.write("status: {0}; reason: {1}".format(status_code, kwargs["message"]))
        else:
            self.write("status: {0}".format(status_code))