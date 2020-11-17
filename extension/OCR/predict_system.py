import time
import os
import sys

__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.append(os.path.abspath(os.path.join(__dir__, '../..')))

import extension.OCR.tools.infer.utility as utility
import cv2
import extension.OCR.tools.infer.predict_det as predict_det
import extension.OCR.tools.infer.predict_rec as predict_rec
import extension.OCR.tools.infer.predict_cls as predict_cls
import copy
import numpy as np
import time
from extension.OCR.ppocr.utils.utility import check_and_read_gif

class TextSystem(object):
    def __init__(self, args):
        self.text_detector = predict_det.TextDetector(args)
        self.text_recognizer = predict_rec.TextRecognizer(args)
        self.use_angle_cls = args.use_angle_cls
        if self.use_angle_cls:
            self.text_classifier = predict_cls.TextClassifier(args)

    def get_rotate_crop_image(self, img, points):
        '''
        img_height, img_width = img.shape[0:2]
        left = int(np.min(points[:, 0]))
        right = int(np.max(points[:, 0]))
        top = int(np.min(points[:, 1]))
        bottom = int(np.max(points[:, 1]))
        img_crop = img[top:bottom, left:right, :].copy()
        points[:, 0] = points[:, 0] - left
        points[:, 1] = points[:, 1] - top
        '''
        img_crop_width = int(
            max(
                np.linalg.norm(points[0] - points[1]),
                np.linalg.norm(points[2] - points[3])))
        img_crop_height = int(
            max(
                np.linalg.norm(points[0] - points[3]),
                np.linalg.norm(points[1] - points[2])))
        pts_std = np.float32([[0, 0], [img_crop_width, 0],
                              [img_crop_width, img_crop_height],
                              [0, img_crop_height]])
        M = cv2.getPerspectiveTransform(points, pts_std)
        dst_img = cv2.warpPerspective(
            img,
            M, (img_crop_width, img_crop_height),
            borderMode=cv2.BORDER_REPLICATE,
            flags=cv2.INTER_CUBIC)
        dst_img_height, dst_img_width = dst_img.shape[0:2]
        if dst_img_height * 1.0 / dst_img_width >= 1.5:
            dst_img = np.rot90(dst_img)
        return dst_img

    def print_draw_crop_rec_res(self, img_crop_list, rec_res):
        bbox_num = len(img_crop_list)
        for bno in range(bbox_num):
            cv2.imwrite("./output/img_crop_%d.jpg" % bno, img_crop_list[bno])
            print(bno, rec_res[bno])

    def __call__(self, img):
        ori_im = img.copy()
        dt_boxes, elapse = self.text_detector(img)
        # print("dt_boxes num : {}, elapse : {}".format(len(dt_boxes), elapse))
        if dt_boxes is None:
            return None, None
        img_crop_list = []

        dt_boxes = sorted_boxes(dt_boxes)

        for bno in range(len(dt_boxes)):
            tmp_box = copy.deepcopy(dt_boxes[bno])
            img_crop = self.get_rotate_crop_image(ori_im, tmp_box)
            img_crop_list.append(img_crop)
        if self.use_angle_cls:
            img_crop_list, angle_list, elapse = self.text_classifier(
                img_crop_list)
            # print("cls num  : {}, elapse : {}".format(
            #     len(img_crop_list), elapse))
            
        
        rec_res, elapse = self.text_recognizer(img_crop_list)
        # print("rec_res num  : {}, elapse : {}".format(len(rec_res), elapse))
        # self.print_draw_crop_rec_res(img_crop_list, rec_res)
        return dt_boxes, rec_res

class PredictSystem:
    def __init__(self, configuration, task_q, result_q, status_q, max_task_number):
        self.task_q = task_q
        self.result_q = result_q
        self.status_q = status_q
        self.max_task_number = max_task_number
        self.configuration = configuration

    def start_predict_loop(self):
        text_sys = TextSystem(utility.parse_args(self.configuration))
        predicted_img_number = 0
        while predicted_img_number < self.max_task_number:
            task = self.task_q.get()

            img = None
            filename = ""
            if task["file_type"] == "filename":
                filename = task["filename"]
                img, flag = check_and_read_gif(filename)
                if not flag:
                    img = cv2.imread(filename)
                if img is None:
                    print("error in loading image:{}".format(filename))
                    continue
            elif task["file_type"] == "file":
                file = task["file"]
                img = np.frombuffer(file, dtype=np.uint8)
                img = cv2.imdecode(img, 1)
                filename = task["filename"]

            ocr_result = self.predict_a_img(img, text_sys)

            if(ocr_result != None):
                result = {
                    "filename": filename,
                    "ocr_result": ocr_result
                }
                self.result_q.put(result)
            predicted_img_number += 1
        self.status_q.put("end")

    def predict_a_img(self, img, text_sys):
        dt_boxes, rec_res = text_sys(img)
        ocr_result = []
        for i in range(len(dt_boxes)):
            ocr_result.append([
                dt_boxes[i].tolist(),
                [rec_res[i][0], float(rec_res[i][1])]
            ])
        return ocr_result

def sorted_boxes(dt_boxes):
    """
    Sort text boxes in order from top to bottom, left to right
    args:
        dt_boxes(array):detected text boxes with shape [4, 2]
    return:
        sorted boxes(array) with shape [4, 2]
    """
    num_boxes = dt_boxes.shape[0]
    sorted_boxes = sorted(dt_boxes, key=lambda x: (x[0][1], x[0][0]))
    _boxes = list(sorted_boxes)

    for i in range(num_boxes - 1):
        if abs(_boxes[i + 1][0][1] - _boxes[i][0][1]) < 10 and \
                (_boxes[i + 1][0][0] < _boxes[i][0][0]):
            tmp = _boxes[i]
            _boxes[i] = _boxes[i + 1]
            _boxes[i + 1] = tmp
    return _boxes

if __name__ == '__main__':
    args = utility.parse_args()
    text_sys = TextSystem(utility.parse_args())

    

        