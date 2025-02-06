import os
import shutil
import pathlib

class _ReadOnlyMeta(type):

    def __setattr__(cls, name, value):
        raise AttributeError('Cannot set attribute of this class')

class FileManager(metaclass=_ReadOnlyMeta):

    ROOT_DIR = os.path.join(pathlib.Path(__file__).absolute().parent, 'files')

    @classmethod
    def move_file(
            cls, 
            original_file_path: str,
            new_file_path: str,
        ):
        """new_file_path는 ROOT_DIR가 생략된 경로"""
        save_dir = os.path.join(cls.ROOT_DIR, os.path.split(new_file_path)[0])
        os.makedirs(save_dir, exist_ok=True)
        new_file_path = os.path.join(cls.ROOT_DIR, new_file_path)
        shutil.copy(original_file_path, new_file_path)
    
    @classmethod
    def remove_file(cls, file_path:str):
        """ROOT_DIR 이하의 경로를 입력받아 파일 삭제
        오류 발생하여도 raise 하지 않음
        """
        try:
            os.remove(os.path.join(cls.ROOT_DIR, file_path))
        except:
            pass