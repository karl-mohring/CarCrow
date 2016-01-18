from subprocess import check_output
import os
import re

PATH = "E:\Dropbox\Projects\CarCrow\\"


def build_file_list(file_path):
    file_list = []
    for root, folders, files in os.walk(file_path):
        folders.sort()
        files.sort()
        for filename in files:
            if re.search(".(avi|AVI)$", filename) is not None:
                file_list.append(os.path.join(root, filename))
    return file_list

file_list = build_file_list(PATH)
print file_list

check_output("ffmpeg -i '{0}' -r 5 {1}\Output\\{2}%04d.jpg".format(file_list[0], os.path.split(file_list[0])[0], os.path.split(file_list[0])[-1].split('.')[0]), shell=True)

