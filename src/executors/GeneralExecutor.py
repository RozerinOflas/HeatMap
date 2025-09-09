import os
import sys
import cv2
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

from sdks.novavision.src.media.image import Image
from sdks.novavision.src.base.capsule import Capsule
from sdks.novavision.src.helper.executor import Executor
from capsules.HeatMap.src.utils.response import build_response
from capsules.HeatMap.src.models.PackageModel import PackageModel


class HeatMap(Capsule):
    def __init__(self, request, bootstrap):
        super().__init__(request, bootstrap)
        self.request.model = PackageModel(**(self.request.data))
        self.images = self.request.get_param("inputImage")
        self.input_detections = self.request.get_param("inputDetections")

        # boş heatmap canvas
        self.heatmap_accumulator = None

    @staticmethod
    def bootstrap(config: dict) -> dict:
        return {}

    def generate_heatmap(self, frame, detections):
        h, w, _ = frame.shape

        if self.heatmap_accumulator is None:
            self.heatmap_accumulator = np.zeros((h, w), dtype=np.float32)

        # detection'ların merkez noktasını ekle
        for det in detections:
            bbox = det["boundingBox"]
            cx = int(bbox["left"] + bbox["width"] / 2)
            cy = int(bbox["top"] + bbox["height"] / 2)

            if 0 <= cx < w and 0 <= cy < h:
                self.heatmap_accumulator[cy, cx] += 1

        # normalize et ve colormap uygula
        heatmap_norm = cv2.normalize(self.heatmap_accumulator, None, 0, 255, cv2.NORM_MINMAX)
        heatmap_color = cv2.applyColorMap(heatmap_norm.astype(np.uint8), cv2.COLORMAP_JET)

        # frame üzerine bindir
        blended = cv2.addWeighted(frame, 0.6, heatmap_color, 0.4, 0)
        return blended

    def run(self):
        output_image = None
        if len(self.input_detections) != 0:
            frame = Image.get_frame(img=self.images, redis_db=self.redis_db)
            output_image = self.generate_heatmap(frame, self.input_detections)

        packageModel = build_response(context=self, output_image=output_image)
        return packageModel


if "__main__" == __name__:
    Executor(sys.argv[1]).run()
