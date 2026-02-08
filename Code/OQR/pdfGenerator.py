from xlrd import open_workbook 
from reportlab. lib . pagesizes import A4  
from reportlab. pdfgen import canvas 
from reportlab.pdfbase.pdfmetrics import stringWidth

import numpy as np
import cv2 as cv
import os

def mmtopix(x):
    return (x*595)//210


temp = input("Enter Dir Name (like Samples/): ")
qrDir = temp+"BW_SecQR/SecQR_PNG/"
list_samples = os.listdir(qrDir)
list_samples.sort()
try:
    list_samples.remove(".DS_Store")
except:
    print("")
   
w, h = A4
count = 3

name = "FinalSamples_"+str(count)
c = canvas.Canvas(os.path.join(os.path.expanduser("~"), os.getcwd()+"/"+temp+name+".pdf"))

tempw = w//5
temph = h//5

c.setFont ( "Helvetica" , 8)

last_full = False
for i, name in enumerate(list_samples):
    version = int(name.split("_")[2])-1
    size_code = 17+(version*4)
    for j, scale_size in enumerate([.3,.4,.5,.6,.7]):
        size = mmtopix(scale_size*size_code)
        
        imgName = qrDir+name
        width = stringWidth("Size - "+str(scale_size*size_code),"Helvetica",8)

        c.drawImage (imgName, ((2*j+1)*(tempw//2))-(size//2), h-((((i)+1)*(temph))-(size//2)), width = size, height = size)
        c.drawString ( ((2*j+1)*(tempw//2))-(width//2), h-((((i)+1)*(temph))-(size//2))-15, "Size - "+str(scale_size*size_code))

    if i==5:
        break
try:
    c.showPage()
    c.save()
    count+=1
except:
    print("Save Error")
