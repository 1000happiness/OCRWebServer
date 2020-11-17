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
        if file_type == "filename":
            filename = self.get_body_argument("filename")
            result = await self.img_ocr_service.get_ocr_result_by_filename(filename)
            if(result == None and block_flag):
                while result == None:
                    result = await self.img_ocr_service.get_ocr_result_by_filename(filename)
                    await gen.sleep(0.5)
            self.write(json.dumps(result, ensure_ascii=False))
        elif file_type == "file":
            file_meta = self.request.files["file"][0]
            file_content = file_meta["body"]
            result = await self.img_ocr_service.get_ocr_result_by_file(file_content)
            if(result == None and block_flag):
                while result == None:
                    result = await self.img_ocr_service.get_ocr_result_by_file(file_content)
                    await gen.sleep(0.5)
            self.write(json.dumps(result, ensure_ascii=False))