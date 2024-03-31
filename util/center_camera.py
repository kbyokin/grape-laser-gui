import time
import datetime
from threading import Thread
import cv2

import torch
from torchvision import transforms

from PIL import Image
import numpy as np
import torchvision.transforms.functional as F

class PadToSquare:
    def __init__(self, fill=(0, 0, 0), padding_mode='constant'):
        self.fill = fill
        self.padding_mode = padding_mode

    def __call__(self, img):
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        w, h = img.size
        max_wh = np.max([w, h])
        hp = int((max_wh - w) / 2)
        vp = int((max_wh - h) / 2)
        padding = (hp, vp, hp, vp)
        return F.pad(img, padding, self.fill, self.padding_mode)
    
