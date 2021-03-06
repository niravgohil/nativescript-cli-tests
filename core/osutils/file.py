"""
File utils.
"""

import fnmatch
import os
import shutil
import time
import tarfile
import zipfile

from core.osutils.os_type import OSType
from core.osutils.process import Process
from core.settings.settings import CURRENT_OS


class File(object):
    @staticmethod
    def read(file_path, print_content=False):
        file_path = file_path.replace("\\", os.path.sep)
        file_path = file_path.replace("/", os.path.sep)
        try:
            with open(file_path, 'r') as file_to_read:
                output = file_to_read.read()
            if print_content:
                print output
            return output
        except IOError:
            return ""

    @staticmethod
    def write(file_path, text):
        try:
            with open(file_path, 'w') as file_to_write:
                file_to_write.write(text + '\n')
            time.sleep(2)
        except:
            print "Failed to write in {0}".format(file_path)

    @staticmethod
    def append(file_path, text):
        try:
            with open(file_path, 'a') as file_to_append:
                file_to_append.write(text + os.linesep)
        except IOError:
            pass

    @staticmethod
    def exists(path):
        path = path.replace("\\", os.path.sep)
        path = path.replace("/", os.path.sep)
        if os.path.exists(path):
            return True
        else:
            return False

    @staticmethod
    def find(base_path, file_name, exact_match=False, match_index=0):
        """
        Find file in path.
        :param base_path: Base path.
        :param file_name: File/folder name.
        :param exact_match: If True it will match exact file/folder name
        :param match_index: Index of match (all matches are sorted by path len, 0 will return closest to root)
        :return: Path to file.
        """
        matches = []
        for root, dirs, files in os.walk(base_path, followlinks=True):
            for current_file in files:
                if exact_match:
                    if file_name == current_file:
                        matches.append(os.path.join(root, current_file))
                else:
                    if file_name in current_file:
                        matches.append(os.path.join(root, current_file))
        matches.sort(key=lambda s: len(s))
        return matches[match_index]

    @staticmethod
    def find_by_extension(ext):
        """
        Find by file extension recursively.
        :param ext: File extension.
        :return: List of found files.
        """
        matches = []
        if "." not in ext:
            ext = "." + ext
        for root, dirs, files in os.walk(os.curdir):
            for f in files:
                if f.endswith(ext):
                    matches.append(os.path.join(root, f))
        print "Files found by \"" + ext + "\" extension recursively:"
        for match in matches:
            print match
        return matches

    @staticmethod
    def pattern_exists(directory, pattern):
        """
        Check if file pattern exist at location.
        :param directory: Base directory.
        :param pattern: File pattern, for example: '*.aar' or '*.android.js'.
        :return: True if exists, False if does not exist.
        """
        found = False
        for root, dirs, files in os.walk(directory):
            for basename in files:
                if fnmatch.fnmatch(basename, pattern):
                    filename = os.path.join(root, basename)
                    print pattern + " exists: " + filename
                    found = True
        return found

    @staticmethod
    def extension_exists(path, extension):
        result = False
        for file_name in os.listdir(path):
            if file_name.endswith(extension):
                print "File: {0}".format(os.path.join(path, file_name))
                result = True
                break
        if result:
            print "There is at least one {0} file in {1} directory.".format(extension, path)
        else:
            print "There are no {0} files in {1} directory.".format(extension, path)
        return result

    @staticmethod
    def remove(file_path, force=True):
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                # File is locked by some process
                print "Failed to delete {0}.".format(file_path)
                if force:
                    print "Kill processes associated with this file."
                    Process.kill_by_handle(file_path)
                    if CURRENT_OS == OSType.WINDOWS:
                        Process.kill('node')
                        Process.kill('adb')
                    os.remove(file_path)

    @staticmethod
    def replace(file_path, str1, str2):
        """
        Replace strings in file
        :param file_path: File path
        :param str1: Old string.
        :param str2: New string.
        """

        if File.exists(file_path):
            content = File.read(file_path=file_path)
            new_content = content.replace(str1, str2)
            File.write(file_path=file_path, text=new_content)

            print "##### REPLACE FILE CONTENT #####"
            print "File: {0}".format(file_path)
            print "Old String: {0}".format(str1)
            print "New String: {0}".format(str2)
        else:
            raise IOError("{0} not found!".format(file_path))

    @staticmethod
    def find_text(text, f):
        data = open(f, 'r')
        found = False
        for line in data:
            if text in line:
                found = True
        return found

    @staticmethod
    def copy(src, dest):
        shutil.copy(src, dest)

    @staticmethod
    def move(src, dest):
        shutil.move(src, dest)

    @staticmethod
    def get_size(file_path):
        if File.exists(file_path):
            return os.path.getsize(file_path)
        else:
            raise IOError("{0} not found!".format(file_path))
    
    @staticmethod
    def unpack_tar(file_path, dest_dir):
        try:
            tarFile = tarfile.open(file_path, 'r:gz')
            tarFile.extractall(dest_dir)
        except:
            print "Failed to unpack .tar file {0}".format(file_path)

    @staticmethod
    def unzip(file_path, dest_dir):
        try:
            zipFile = zipfile.ZipFile(file_path, 'r')
            zipFile.extractall(dest_dir)
            zipFile.close()
        except:
            print "Failed to unzip file {0}".format(file_path)
