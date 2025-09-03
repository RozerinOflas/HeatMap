import os
import sys
import cv2
import numpy as np
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

from sdks.novavision.src.media.image import Image
from sdks.novavision.src.base.component import Component
from sdks.novavision.src.helper.executor import Executor
from components.HeatMap.src.utils.response import build_response
from components.HeatMap.src.models.PackageModel import PackageModel


class HeatMap(Component):
    def __init__(self, request, bootstrap):
        super().__init__(request, bootstrap)
        self.request.model = PackageModel(**(self.request.data))
        self.image = self.request.get_param("inputImage")          # Frame
        self.detections = self.request.get_param("inputDetections")  # ObjectTracking output
        self.frameTime = float(self.request.get_param("FrameTime")) # Kullanıcıdan gelen saniye aralığı
        self.decay = float(self.request.get_param("Decay", 0.95))   # Isının yavaşça silinmesi için

        # Isı haritası buffer
        if "heatmap" not in self.bootstrap:
            self.bootstrap["heatmap"] = None
        if "last_update" not in self.bootstrap:
            self.bootstrap["last_update"] = datetime.now()

    @staticmethod
    def bootstrap(config: dict) -> dict:
        return {}

    def update_heatmap(self, frame_shape, points):
        """ Noktalardan heatmap matrisini günceller """
        if self.bootstrap["heatmap"] is None:
            self.bootstrap["heatmap"] = np.zeros((frame_shape[0], frame_shape[1]), dtype=np.float32)

        heatmap = self.bootstrap["heatmap"]

        # Decay uygula (eski veriler yavaşça silinsin)
        heatmap *= self.decay

        # Yeni noktaları işaretle
        for (x, y) in points:
            if 0 <= y < heatmap.shape[0] and 0 <= x < heatmap.shape[1]:
                heatmap[int(y), int(x)] += 1.0

        self.bootstrap["heatmap"] = heatmap
        return heatmap

    def apply_heatmap(self, frame, heatmap):
        """ OpenCV applyColorMap ile ısı haritasını çizer """
        hm = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
        hm = hm.astype(np.uint8)
        hm_color = cv2.applyColorMap(hm, cv2.COLORMAP_JET)
        blended = cv2.addWeighted(frame, 0.6, hm_color, 0.4, 0)
        return blended

    def run(self):
        img = Image.get_frame(img=self.image, redis_db=self.redis_db)
        frame = img.value

        # Detections içinden (x, y) noktalarını çıkar
        points = []
        for det in (self.detections or []):
            bbox = det["boundingBox"]
            x = int(bbox["left"] + bbox["width"] / 2)
            y = int(bbox["top"] + bbox["height"] / 2)
            points.append((x, y))

        # Frame time kontrolü
        now = datetime.now()
        if (now - self.bootstrap["last_update"]).total_seconds() >= self.frameTime:
            heatmap = self.update_heatmap(frame.shape, points)
            frame = self.apply_heatmap(frame, heatmap)
            self.bootstrap["last_update"] = now

        # Çıktı olarak görüntüyü güncelle
        img.value = frame
        self.image = Image.set_frame(img=img, package_uID=self.uID, redis_db=self.redis_db)

        packageModel = build_response(context=self)
        return packageModel


if "__main__" == __name__:
    Executor(sys.argv[1]).run()
