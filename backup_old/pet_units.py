"""
工具函数模块
"""
import os
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


def load_pet_image(pet_instance, image_paths=None):
    """通用的图片加载函数"""
    if image_paths is None:
        image_paths = ["pet.png", "pet.jpg", "pet.gif"]

    for path in image_paths:
        if os.path.exists(path):
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(
                    pet_instance.pet_width, pet_instance.pet_height,
                    Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                if hasattr(pet_instance, 'pet_label'):
                    pet_instance.pet_label.setPixmap(pixmap)
                return True

    return False


def create_placeholder(pet_instance):
    """创建占位符"""
    from PyQt5.QtGui import QPainter, QBrush, QColor, QPen

    pixmap = QPixmap(pet_instance.pet_width, pet_instance.pet_height)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QBrush(QColor(100, 150, 255, 200)))
    painter.setPen(QPen(QColor(50, 100, 200), 2))
    painter.drawEllipse(10, 10, 80, 80)
    painter.end()

    if hasattr(pet_instance, 'pet_label'):
        pet_instance.pet_label.setPixmap(pixmap)