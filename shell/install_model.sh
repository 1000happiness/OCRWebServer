cd extension
cd OCR
mkdir model
cd model
wget https://paddleocr.bj.bcebos.com/20-09-22/mobile/det/ch_ppocr_mobile_v1.1_det_infer.tar
tar -xf ch_ppocr_mobile_v1.1_det_infer.tar
wget https://paddleocr.bj.bcebos.com/20-09-22/cls/ch_ppocr_mobile_v1.1_det_infer.tar
tar -xf ch_ppocr_mobile_v1.1_cls_infer.tar
wget https://paddleocr.bj.bcebos.com/20-09-22/mobile/rec/ch_ppocr_mobile_v1.1_det_infer.tar
tar -xf ch_ppocr_mobile_v1.1_rec_infer.tar