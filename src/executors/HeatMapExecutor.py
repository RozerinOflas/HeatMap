"""
    It is a component in which object detection results are accumulated into a heatmap.
"""

import os
import cv2
import sys
import numpy as np
import matplotlib.pyplot as plt
from ultralytics import YOLO

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

from sdks.novavision.src.media.image import Image
from sdks.novavision.src.base.component import Component
from sdks.novavision.src.helper.executor import Executor
from components.HeatMapExample.src.utils.response import build_response
from components.HeatMapExample.src.models.PackageModel import PackageModel


class HeatmapExecutor(Component):
    def __init__(self, request, bootstrap):
        super().__init__(request, bootstrap)
        self.request.model = PackageModel(**(self.request.data))
        self.input_video = self.request.get_param("inputVideo")
        self.draw_boxes = self.request.get_param("DrawBoxes", default=True)

        # YOLO modelini yükle
        self.model = YOLO("yolo11m.pt")

    @staticmethod
    def bootstrap(config: dict) -> dict:
        return {}

    def generate_heatmap(self, video_path):
        cap = cv2.VideoCapture(video_path)

        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out_boxes = cv2.VideoWriter("output_with_boxes.mp4", fourcc, fps, (width, height))
        out_overlay = cv2.VideoWriter("output_overlay.mp4", fourcc, fps, (width, height))

        heatmap_accum = np.zeros((height, width), dtype=np.float32)
        frames_list = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frames_list.append(frame.copy())
            results = self.model(frame, verbose=False)

            for r in results:
                boxes = r.boxes.xyxy.cpu().numpy()
                confs = r.boxes.conf.cpu().numpy()
                clss = r.boxes.cls.cpu().numpy()

                for box, conf, cls_id in zip(boxes, confs, clss):
                    x1, y1, x2, y2 = map(int, box)
                    label = f"{self.model.names[int(cls_id)]} {conf:.2f}"

                    if self.draw_boxes:
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame, label, (x1, y1 - 5),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

                    heatmap_accum[y1:y2, x1:x2] += 1

            out_boxes.write(frame)

        cap.release()
        out_boxes.release()

        # Heatmap kaydet
        plt.figure(figsize=(10, 8))
        plt.imshow(heatmap_accum, cmap='hot', alpha=0.8)
        plt.colorbar()
        plt.title("Object Detection Heatmap")
        heatmap_path = "heatmap.png"
        plt.savefig(heatmap_path)
        plt.close()

        # Overlay video
        heatmap_norm = cv2.normalize(heatmap_accum, None, 0, 255, cv2.NORM_MINMAX)
        heatmap_color = cv2.applyColorMap(heatmap_norm.astype(np.uint8), cv2.COLORMAP_JET)

        for frame in frames_list:
            overlay = cv2.addWeighted(frame, 0.6, heatmap_color, 0.4, 0)
            out_overlay.write(overlay)

        out_overlay.release()

        return heatmap_path, "output_with_boxes.mp4", "output_overlay.mp4"

    def run(self):
        # Videoyu Redis'ten al
        video = Image.get_frame(img=self.input_video, redis_db=self.redis_db)

        heatmap_path, boxed_video, overlay_video = self.generate_heatmap(video.value)

        # Çıktıyı Redis'e yaz
        self.heatmap_image = Image.set_frame(img=heatmap_path, package_uID=self.uID, redis_db=self.redis_db)
        self.overlay_video = Image.set_frame(img=overlay_video, package_uID=self.uID, redis_db=self.redis_db)

        packageModel = build_response(context=self)
        return packageModel


if "__main__" == __name__:
    Executor(sys.argv[1]).run()
