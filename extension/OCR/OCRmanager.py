import multiprocessing
import threading
from .predict_system import PredictSystem

class OCRManager:
    processes = []
    manage_loop_flag = False
    status_q = multiprocessing.Queue()

    def __init__(self, configuration, ocr_service):
        process_num = configuration["process"]["number"]
        self.max_task_number = configuration["process"]["max_task_number"]
        self.predict_system_configuration = configuration["predict_system"]

        task_q, result_q = ocr_service.get_task_and_result_queue()
        self.task_q = task_q
        self.result_q = result_q

        for i in range(process_num):
            predict_system = PredictSystem(self.predict_system_configuration, task_q, result_q, self.status_q, self.max_task_number)
            self.processes.append(multiprocessing.Process(target=predict_system.start_predict_loop))

    def start_all_process(self):
        for process in self.processes:
            process.start()

    def start_process_management(self):
        self.manage_loop_flag = True
        self.start_all_process()
        th = threading.Thread(target=self.process_management_loop)
        th.start()

    def stop_process_management(self):
        self.manage_loop_flag = False

    def process_management_loop(self):
        while self.manage_loop_flag:
            status = self.status_q.get()
            if status == "end":
                predict_system = PredictSystem(self.predict_system_configuration, self.task_q, self.result_q, self.status_q, self.max_task_number)
                process = multiprocessing.Process(target=predict_system.start_predict_loop)
                process.start()


