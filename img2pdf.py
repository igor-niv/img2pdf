#!/usr/bin/python3

from os.path import exists, isfile, join, expanduser, basename, isdir
from shutil import copyfile, rmtree
from sys import argv
from reportlab import platypus
from PIL import Image
from tempfile import mkdtemp
from re import search
from os import remove, listdir
import argparse
import subprocess
import unittest

class PdfCreator:
    def __init__(self, imagePaths, pdfPath = None):
        self.__imagePaths = imagePaths
        self.__tempDir = mkdtemp()
        self.__pdfPath = join(expanduser('~'), "workout.pdf") if not pdfPath else pdfPath

    @property
    def tempDir(self):
        return self.__tempDir

    @tempDir.setter
    def tempDir(self, tempDir):
        if not isinstance(tempDir, str):
            raise TypeError
        assert exists(tempDir), "The temp directory path must be valid"
        self.__tempDir = tempDir

    @property
    def pdfPath(self):
        return self.__pdfPath

    def __prepare(self):
        paths = list(filter(self.__condition, self.__imagePaths))
        if not len(paths):
            print("Error: there are not files for processing!")
            return None
        tmpPaths = []
        for src in paths:
            dst = join(self.__tempDir, basename(src))
            copyfile(src, dst)
            tmpPaths.append(dst)
        return tmpPaths

    def __convert(self,imagePaths):
        doc = platypus.SimpleDocTemplate(self.__pdfPath)
        doc.leftMargin = 0
        doc.bottomMargin = 0
        doc.rightMargin = 0
        doc.topMargin = 0
        pageWidth = 583
        pageHeight = 829
        story = []
        hasStory = False
        for p in imagePaths:
            try:
                pilImg = Image.open(p)
                print('Adding ' + basename(p) + ' to pdf document...')
            except Exception:
                print('Cannot access a file: ' + p)
                continue
            if pilImg.size[0] > pilImg.size[1]:
                pilImg = pilImg.rotate(90)
            ratio = pilImg.size[1] / pilImg.size[0]
            imageWidth = pageWidth
            imageHeight = imageWidth * ratio
            if imageHeight > pageHeight:
                imageHeight = pageHeight
                imageWidth = imageHeight / ratio
            pilImg.save(p)
            repImg = platypus.Image(p, imageWidth, imageHeight)
            story.append(repImg)
            story.append(platypus.PageBreak())
            print('OK')
            hasStory = True
        doc.build(story)
        if hasStory:
            print("Pdf file was created successfully")
        else:
            print("Pdf file was not created")
            if exists(self.__pdfPath):
                remove(self.__pdfPath)
        return hasStory

    def create(self):
        imagePaths = self.__prepare()
        if not imagePaths:
            return False
        result = self.__convert(imagePaths)
        rmtree(self.__tempDir)
        return result

    def __condition(self, p):
        return exists(p) and isfile(p) and search(r'\.jpg$|\.bmp$|\.tiff$|\.png$|\.gif$|\.jpeg$', p) != None

########################################################################

def recursiveSearch(p, fps):
    def enumFilesInDir():
        _files = listdir(p)
        for i in range(0, len(_files)):
            _files[i] = join(p, _files[i])
        return _files
    files = enumFilesInDir()
    for f in files:
        assert exists(f), "File or directory not found: " + f
        if isdir(f):
            recursiveSearch(f, fps)
        elif isfile(f):
            fps.append(f)


def parseArgs():
    parser = argparse.ArgumentParser(description="img2pdf.py is very simple python script to convert "
                                                 "image files to a single pdf file (A4 paper size)")
    parser.add_argument("-d", "--directories",
                        help="search image files in specified directories (recursive search only)", type=str, nargs="+")
    parser.add_argument("-f", "--files",
                        help="image file names", type=str, nargs="+")
    parser.add_argument("--printer",
                        help="if this option is enabled, "
                             "script create the pdf file and print it on a default printer", action="store_true")
    parser.add_argument("--out",
                        help="Full path of the PDF file (~/workout.pdf is default) ", type=str)
    args = parser.parse_args()

    filePaths = []
    if args.directories:
        for dir in args.directories:
            recursiveSearch(dir, filePaths)
    if args.files:
        for file in args.files:
            assert exists(file) and isfile(file), "File or directory not found: " + file
            filePaths.append(file)
    return args.printer, filePaths, args.out

########################################################################

if __name__ == "__main__":
    isPrint, filePaths, pdfPath = parseArgs()
    pdfCreator = PdfCreator(filePaths, pdfPath)
    pdfCreator.create()
    if isPrint:
        subprocess.call(["lpr", pdfCreator.pdfPath])
