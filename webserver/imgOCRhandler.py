from tornado import web, gen
import json
import numpy as np
import cv2

class ImgOCRHandler(web.RequestHandler):
    def initialize(self, img_ocr_service):
        self.img_ocr_service = img_ocr_service

    async def post(self):
        file_type = self.get_body_argument("file_type")
        block_flag = self.get_body_argument("block_flag")
        if block_flag != "True" and block_flag != "False":
            self.send_error(400)
            return
        if file_type == "filename":
            filename = self.get_body_argument("filename")

            result = None
            while True:
                try:
                    result = await self.img_ocr_service.get_ocr_result_by_filename(filename)
                except Exception as e:
                    self.send_error(500, message=str(e))
                    return

                if(result == None and block_flag == "True"):
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

                if(result == None and block_flag == "True"):
                    await gen.sleep(0.5)
                    continue
                else:
                    break         

            self.write(json.dumps(result, ensure_ascii=False))
        else:
            self.send_error(400)
            return

    def write_error(self, status_code, **kwargs):
        self.write("status: {0}; reason: {1}".format(status_code, kwargs["message"]))