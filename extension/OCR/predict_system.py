import time

class PredictSystem:
    def __init__(self, task_q, result_q, status_q, max_task_number):
        self.task_q = task_q
        self.result_q = result_q
        self.status_q = status_q
        self.max_task_number = max_task_number

    def predict_a_img(self, filename):
        print("predict {}".format(filename))
        time.sleep(1)
        ocr_result = []
        return ocr_result

    def start_predict_loop(self):
        predicted_img_number = 0
        while predicted_img_number < self.max_task_number:
            filename = self.task_q.get()
            ocr_result = self.predict_a_img(filename)
            if(ocr_result != None):
                result = {
                    "filename": filename,
                    "ocr_result": ocr_result
                }
                self.result_q.put(result)
            predicted_img_number += 1
        self.status_q.put("end")
        self.status_q.join()

        