from tornado import web, gen
import json

class ImgOCRHandler(web.RequestHandler):
    def initialize(self, img_ocr_service):
        self.img_ocr_service = img_ocr_service

    async def post(self):
        filename = self.get_body_argument("filename")
        result = await self.img_ocr_service.get_ocr_result_by_filename_noblock(filename)
        # result = await self.img_ocr_service.test()
        self.write(json.dumps(result))