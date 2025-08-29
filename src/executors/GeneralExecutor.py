import os
import cv2
import sys
import numpy as np
from collections import defaultdict

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

from sdks.novavision.src.media.image import Image
from sdks.novavision.src.base.component import Component
from sdks.novavision.src.helper.executor import Executor
from components.HeatMap.src.utils.response import build_responseGeneral
from components.HeatMap.src.models.PackageModel import PackageModel


class GeneralExecutor(Component):
    def __init__(self, request, bootstrap):
        super().__init__(request, bootstrap)
        self.request.model = PackageModel(**(self.request.data))
        self.image = self.request.get_param("inputImage")
        self.detections = self.request.get_param("outputDetections")  # frame bazlı liste
        self.bins = self.request.get_param("Bins") or 100
        self.frame_time = self.request.get_param("FrameTime") or 1
        self.heatmap_time = self.request.get_param("HeatMapTime") or 0

    @staticmethod
    def bootstrap(config: dict) -> dict:
        return {}

    def extract_points_by_id(self, detections):
        """Her trackerID için ayrı noktalar listesi oluşturur"""
        id_points = defaultdict(list)
        for det in detections:
            bbox = det["boundingBox"]
            tracker_id = det["trackerID"]
            x_center = bbox["left"] + bbox["width"] / 2
            y_center = bbox["top"] + bbox["height"] / 2
            id_points[tracker_id].append([x_center, y_center])
        return id_points

    def generate_heatmap(self, points, img_shape):
        """2D histogram tabanlı heatmap"""
        if len(points) == 0:
            return np.zeros((img_shape[0], img_shape[1]), dtype=np.uint8)

        points = np.array(points)
        heatmap, _, _ = np.histogram2d(
            points[:,1],  # y koordinatı
            points[:,0],  # x koordinatı
            bins=self.bins,
            range=[[0, img_shape[0]], [0, img_shape[1]]]
        )
        heatmap = cv2.GaussianBlur(heatmap, (15, 15), 0)
        heatmap = (heatmap / np.max(heatmap) * 255).astype(np.uint8)
        return heatmap

    def overlay_heatmap(self, img, heatmap):
        """Heatmap’i görüntü üzerine bindirir"""
        heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
        overlay = cv2.addWeighted(img, 0.6, heatmap_color, 0.4, 0)
        return overlay

    def run(self):
        img = Image.get_frame(img=self.image, redis_db=self.redis_db)
        img_shape = img.value.shape[:2]

        accumulated_points = []  # tüm frame’lerden toplanan noktalar
        for frame_idx, frame_detections in enumerate(self.detections):
            # frame içindeki tüm trackerID noktalarını al
            id_points = self.extract_points_by_id(frame_detections)
            for pts in id_points.values():
                accumulated_points.extend(pts)

            # frame_time geldiğinde heat map oluştur
            if (frame_idx + 1) % self.frame_time == 0:
                heatmap = self.generate_heatmap(accumulated_points, img_shape)
                overlay_img = self.overlay_heatmap(img.value.copy(), heatmap)
                img.value = overlay_img

            # HeatMapTime ile sınırlamak istersek
            if self.heatmap_time > 0 and len(accumulated_points) > self.heatmap_time:
                accumulated_points = accumulated_points[-self.heatmap_time:]  # en son HeatMapTime kadar noktayı tut

        # Son frame’deki heat map’i overlay et
        heatmap = self.generate_heatmap(accumulated_points, img_shape)
        img.value = self.overlay_heatmap(img.value.copy(), heatmap)

        # Redis veya package’a kaydet
        self.image = Image.set_frame(img=img, package_uID=self.uID, redis_db=self.redis_db)
        packageModel = build_responseGeneral(context=self)
        return packageModel


if "__main__" == __name__:
    Executor(sys.argv[1]).run()
