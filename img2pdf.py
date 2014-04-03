from os.path import exists, isfile, join, expanduser, basename
from shutil import copyfile, rmtree
from sys import argv
from reportlab import platypus
from PIL import Image
from tempfile import mkdtemp
from re import search
from os import listdir
from os.path import isfile, join

class PdfCreator:
    def __init__(self, imagePaths, pdfPath = None):
        self.__imagePaths = imagePaths
        self.__tmpDir = mkdtemp()
        if not pdfPath:
            self.__pdfPath = join(expanduser('~'), "workout.pdf")
        else:
            self.__pdfPath = pdfPath

    def __prepare(self):
        paths = list(filter(self.__condition, argv))
        if not len(paths):
            print("Error: there are not files for processing!")
            return None
        tmpPaths = []
        for src in paths:
            dst = join(self.__tmpDir, basename(src))
            copyfile(src, dst)
            tmpPaths.append(dst)
        return tmpPaths

    def __convert(self,imagePaths):
        doc = platypus.SimpleDocTemplate(self.__pdfPath)
        doc.leftMargin = 0
        doc.bottomMargin = 0
        doc.rightMargin = 0
        doc.topMargin = 0
        size = (int(8.27 * 72)*4, int(11.69 * 72)*4)
        pageWidth = 583
        pageHeight = 829
        story = []
        isSuccess = False
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
            pilImg.thumbnail(size, Image.ANTIALIAS)
            pilImg.save(p)
            repImg = platypus.Image(p, imageWidth, imageHeight)
            story.append(repImg)
            story.append(platypus.PageBreak())
            print('OK')
            isSuccess = True
        doc.build(story)
        if isSuccess:
            print("Pdf file was created successfully")
        else:
            print("Pdf file was not created")

    def create(self):
        imagePaths = self.__prepare()
        if not imagePaths:
            exit(1)
        self.__convert(imagePaths)


    def __exit__(self, exc_type, exc_val, exc_tb):
        rmtree(self.__tmpDir)

    def __condition(self, p):
        return exists(p) and isfile(p) and search(r'\.jpg$|\.bmp$|\.tiff$|\.png$|\.gif$|\.jpeg$', p) != None


########################################################################
if __name__ == "__main__":
    if len(argv) == 1 or argv[-1] == '--help':
        print("Usage:\npython3 img2pdf.py image_file1[image_file2...]")
        exit(0)
    PdfCreator(argv[1:]).create()