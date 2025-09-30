
import numpy as np
import pandas as pd
from PIL import Image
import cv2
import json

import os
import inspect
import platform
import subprocess


__all__ = [
    'code',
    'finder',
    'read',
]


def code(input_):
    if inspect.isfunction(input_) or inspect.ismodule(input_) or inspect.isclass(input_):
        file_path = inspect.getfile(input_)
    else:
        file_path = os.path.expanduser(input_)

    if platform.system() == 'Darwin':
        subprocess.run(['code', file_path], check=True)
    elif platform.system() == 'Windows':
        subprocess.run(['powershell.exe', '-Command', f'code {file_path}'], check=True)
    else:
        raise NotImplementedError('This function is supported on Windows and macOS only. ')



def finder(path):
    path = os.path.expanduser(path)
    if platform.system() == 'Darwin':
        subprocess.run(['open', path], check=True)
    elif platform.system() == 'Windows':
        subprocess.run(['start', '', path], shell=True, check=True)
    else:
        raise NotImplementedError('This function is supported on Windows and macOS only. ')
    
    return os.path.abspath(path)



class _FileReader:
    def __init__(self, path, dtype):
        self.path = os.path.expanduser(path)
        self.dtype = dtype
    
        if not os.path.exists(self.path):
            raise FileNotFoundError(f'{path} does not exists')
        
        self.path = path
        self.ext = os.path.splitext(path)[-1].lower()[1:]
        self.name = os.path.basename(path)
        self.stem = os.path.splitext(self.name)[0]


    def _img(self):
        img = Image.open(self.path)
        try:
            n_frames = img.n_frames
        except AttributeError:
            n_frames = 1
        arr = []
        for i in range(n_frames):
            if n_frames > 1:
                img.seek(i)
            arr.append(np.array(img))

        arr = np.array(arr).astype(self.dtype)
        if arr.shape[0] == 1:
            return arr[0]
        return arr



    def _avi(self):
        avi = cv2.VideoCapture(self.path)
        arr = []
        while True:
            ret, frame = avi.read()
            if not ret:
                break
            arr.append(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
        avi.release()
        return np.array(arr).astype(self.dtype)


    def _json(self):
        with open(self.path, 'r') as f:
            dic = json.load(f)
        return dic


    def _csv(self):
        return np.array(pd.read_csv(self.path, header=None))


    def _npy(self):
        return np.load(self.path).astype(self.dtype)


    def _npz(self):
        dic = dict(np.load(self.path))
        for key in dic.keys():
            dic[key] = dic[key].astype(self.dtype)
        return dic


    def _other(self):
        msg = f"No implemented method for '{self.ext}', nothing to return."
        if os.path.exists(self.path):
            msg += f" The file '{self.name}' exists, you may use finder() to open it."
        print(msg)
        return None


    def read(self):
        if self.ext == 'npz':
            data = self._npz()

        elif self.ext == 'npy':
            data = self._npy()

        elif self.ext == 'avi':
            data = self._avi()

        elif self.ext in ['bmp', 'tif', 'tiff']:
            data = self._img()

        elif self.ext == 'csv':
            data = self._csv()

        elif self.ext == 'json':
            data = self._json()

        else:
            data = self._other()

        return data



def read(path, dtype=float):
    target = _FileReader(path, dtype)
    return target.read()
    


# class _FileWriter:
#     pass



# def _to_csv(array=None, save=None):
#     if array is not None:
#         pd.DataFrame(array).to_csv(save, header=None, index=None)
#     else:
#         raise TypeError('array is None')

# def imwrite(array=None, save=None, convert=False):
#     if array is not None:
#         if array.dtype == np.uint8:
#             Image.fromarray(array).save(save)
#         elif not (array.dtype == np.uint8) and convert:
#             Image.fromarray(array.astype(np.uint8)).save(save)
#         else:
#             raise TypeError('array.dtype must be np.uint8')
#     else:
#         raise TypeError('array is None')


# def gifshow(array, auto_contrast=True, loops=0, fps=30, save=None, override=False):
#     import io
#     from IPython.display import display, Image as IPImage
    
#     array = read(array)
#     if array.ndim != 3:
#         raise ValueError('array must be 3-d')
        
#     duration = int(1000 / fps)
#     if auto_contrast:
#         images = [Image.fromarray(min_max_normalize(frame, min_=0, max_=255)) 
#                   for frame in array]
#     else:
#         images = [Image.fromarray(frame)for frame in array]
#     gif_buffer = io.BytesIO()

#     if loops == 1:
#         loop = None
#     elif loops in (0, np.inf):
#         loop = 0
#     else:
#         loop = loops - 1

#     images[0].save(gif_buffer, 
#                    format='GIF', 
#                    save_all=True, 
#                    append_images=images[1:], 
#                    duration=duration, 
#                    loop=loop)
    
#     gif_buffer.seek(0)

#     if save is not None:
#         if os.path.exists(save):
#             if override:
#                 os.remove(save)
#             elif not override:
#                 raise FileExistsError('file already exists')
#         else:
#             with open(save, 'wb') as f:
#                 f.write(gif_buffer.getvalue())

#     display(IPImage(data=gif_buffer.getvalue(), format='gif'))
