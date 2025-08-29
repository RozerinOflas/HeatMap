import os
import cv2
import sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

from sdks.novavision.src.media.image import Image
from sdks.novavision.src.base.component import Component
from sdks.novavision.src.helper.executor import Executor
from components.HeatMap.src.utils.response import build_responseGeneral
from components.HeatMap.src.models.PackageModel import PackageModel


class HeatMapExecutor(Component):
    def __init__(self, request, bootstrap):
        super().__init__(request, bootstrap)
        self.request.model = PackageModel(**(self.request.data))
        self.image = self.request.get_param("inputImage")
        self.detections = self.request.get_param("outputDetections")  # object tracking JSON
        self.bins = self.request.get_param("Bins") or 100  # ısı haritası çözünürlüğü

    @staticmethod
    def bootstrap(config: dict) -> dict:
        return {}

    def extract_points(self):
        """Bounding box merkezlerini alır"""
        points = []
        for det in self.detections:
            bbox = det["boundingBox"]
            x_center = bbox["left"] + bbox["width"] / 2
            y_center = bbox["top"] + bbox["height"] / 2
            points.append([x_center, y_center])
        return np.array(points)

    def generate_heatmap(self, points, img_shape):
        """2D histogram tabanlı heatmap oluşturur"""
        if len(points) == 0:
            return np.zeros((img_shape[0], img_shape[1]))

        heatmap, xedges, yedges = np.histogram2d(
            points[:,1],  # y koordinatı (row)
            points[:,0],  # x koordinatı (col)
            bins=self.bins,
            range=[[0, img_shape[0]], [0, img_shape[1]]]
        )

        # Gaussian Blur ile pürüzsüzleştirme
        heatmap = cv2.GaussianBlur(heatmap, (15, 15), 0)

        # Normalize et
        heatmap = (heatmap / np.max(heatmap) * 255).astype(np.uint8)
        return heatmap

    def overlay_heatmap(self, img, heatmap):
        """Heatmap’i orijinal görüntü üzerine bindirir"""
        heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
        overlay = cv2.addWeighted(img, 0.6, heatmap_color, 0.4, 0)
        return overlay

    def run(self):
        img = Image.get_frame(img=self.image, redis_db=self.redis_db)
        points = self.extract_points()
        heatmap = self.generate_heatmap(points, img.value.shape[:2])
        overlay_img = self.overlay_heatmap(img.value, heatmap)
        img.value = overlay_img
        self.image = Image.set_frame(img=img, package_uID=self.uID, redis_db=self.redis_db)
        packageModel = build_responseGeneral(context=self)
        return packageModel


if "__main__" == __name__:
    Executor(sys.argv[1]).run()
