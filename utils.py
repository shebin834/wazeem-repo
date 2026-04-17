import os

def rename(file_path, prefix, count):
    ext = os.path.splitext(file_path)[1]
    return f"{prefix}_{str(count).zfill(3)}{ext}"
