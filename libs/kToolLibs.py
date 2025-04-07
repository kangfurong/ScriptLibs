import hashlib
import os
from datetime import datetime

class kMD5FileManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self._md5_cache = set()
        self._file_date = None
        try:
            self._load_file_data()
        except Exception as e:
            print(f"Error initializing kMD5FileManager: {e}")
            raise

    def _get_current_date(self):
        return datetime.now().strftime('%Y-%m-%d')

    def _compute_md5(self, data):
        try:
            return hashlib.md5(data.encode('utf-8')).hexdigest()
        except Exception as e:
            print(f"Error computing MD5: {e}")
            raise ValueError("Error computing MD5 hash.")

    def _load_file_data(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        self._file_date = lines[-1].strip()
                        self._md5_cache = set(line.strip() for line in lines[:-1])
            except Exception as e:
                print(f"Error reading file: {e}")
                raise IOError("Error reading the file.")
        else:
            self._file_date = self._get_current_date()

    def _write_to_file(self):
        try:
            with open(self.file_path, 'w') as f:
                for md5_hash in self._md5_cache:
                    f.write(f"{md5_hash}\n")
                f.write(f"{self._file_date}\n")
            return True
        except Exception as e:
            print(f"Error writing to file: {e}")
            return False

    def _is_md5_exists(self, md5_hash):
        return md5_hash in self._md5_cache

    def _write_md5(self, md5_hash):
        today = self._get_current_date()

        if today != self._file_date:
            self._md5_cache.clear()
            self._file_date = today
            self._md5_cache.add(md5_hash)
            return self._write_to_file()

        if self._is_md5_exists(md5_hash):
            # 不需要写入文件
            return True

        self._md5_cache.add(md5_hash)
        return self._write_to_file()

    def write_precomputed_md5(self, md5_hash):
        try:
            if not isinstance(md5_hash, str) or len(md5_hash) != 32:
                raise ValueError("Invalid MD5 hash")
            return self._write_md5(md5_hash)
        except Exception as e:
            print(f"Error in write_precomputed_md5: {e}")
            return False

    def write_md5_from_text(self, text):
        try:
            if not isinstance(text, str):
                raise ValueError("Input text must be a string")
            md5_hash = self._compute_md5(text)
            return self._write_md5(md5_hash)
        except Exception as e:
            print(f"Error in write_md5_from_text: {e}")
            return False

# 示例使用
if __name__ == "__main__":
    try:
        #file_manager = kMD5FileManager('md5_data.txt')

        # 接口1：传入已计算的MD5值
        #result = file_manager.write_precomputed_md5('d41d8cd98f00b204e9800998ecf8427e')
        #print("Write precomputed MD5 result:", "Success" if result else "Failure")

        # 接口2：传入文本并计算MD5值
        #result = file_manager.write_md5_from_text('example_string')
        #print("Write MD5 from text result:", "Success" if result else "Failure")
        print("test...")
    except Exception as e:
        #print(f"Fatal error: {e}")
        print("exception...")
