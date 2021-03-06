from tornado import web

from .imgOCRhandler import ImgOCRHandler

def make_app(img_ocr_service):
    application = web.Application([
        (r'/ocr_service', ImgOCRHandler, {"img_ocr_service": img_ocr_service})
    ])
    return application