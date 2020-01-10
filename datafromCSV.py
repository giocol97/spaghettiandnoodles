import csv,ast,extcolors,sys
import scipy.io as sio
#for the extcolors package visit https://github.com/giocol97/extract-colors-py
#to extract the colors from an image use   colors, pixel_count = extcolors.extract_crop(data[1234][2],150)

#DATA FORMAT
#data is an array with the following row format:
#[0]=>country code (IT,JP,TW), [1]=>recipe name, [2]=>image link, [3]=>array of ingredients [4]=>color data RGB [5]=>color data 1-4096
#color data is an array of colors where each color contains 3 numbers indicating the RGB color and another number indicating how many pixels of that color were in the image
#the number of colors is variable

def getNationData(code,data):
    dataRet=[]
    for row in data:
        if row[0]==code:
            dataRet.append(row)
    return dataRet


#this function converts the colors in an image from 24 to 12 bits so that when put in the network there is a limited amount of possible colors (2^12 vs 2^24)
#the input is the array colors returned by extcolors.extract_crop()
def transformColors24to12bits(colors24):
    colors12=[]
    for j in range(len(colors24)):
        color=[]
        for i in range(3):
            c=int(15*colors24[j][0][i]/255)
            color.append(int(c*255/15))
        color12=[color,colors24[j][1]]
        colors12.append(color12)
    return colors12

def elaboraColori(inst,data):
    n=len(data)
    instance=int(inst)
    numInstances=4
    inizio=int(((n/numInstances))*(instance-1))
    fine=int(((n/numInstances))*instance-1)
    f = open("data/colorData"+str(instance)+".txt", "w+")
    for i in range(inizio,fine):
        if data[i][2]=="":
            continue
        colors, pixel_count = extcolors.extract_crop(data[i][2],150)
        f.write(str(colors)+"\t"+data[i][2]+"\n")
    f.close()

def RGBtoInt(r,g,b):
    r=bin(r)
    g=bin(g)
    b=bin(b)
    r=r[2:]
    g=g[2:]
    b=b[2:]
    while len(r)<4:
        r="0"+r
    while len(g)<4:
        g="0"+g
    while len(b)<4:
        b="0"+b
    return int(r+g+b,2)

def getGoodIngredients(badIngredients,goodIngredients):
    ingredients=[]
    #for each bad ingredient we try to find a corresponding good ingredient, otherwise we delete the ingredient
    for badIng in badIngredients:
        for goodIng in goodIngredients:
            if goodIng in badIng:
                ingredients.append(goodIng)
                break
    return ingredients


#IT dataset
with open('data/IT.csv', mode='r') as csv_file:
    data=list(csv.reader(csv_file))

data.pop(0)
for i in range(len(data)):
    data[i][0]="IT"
    data[i][3]=ast.literal_eval(data[i][3])

#JP dataset
with open('data/JP.csv', mode='r', encoding="utf8") as csv_file:
    dataJP=list(csv.reader(csv_file))

for i in range(len(dataJP)):
    row=[]
    if dataJP[i][1]=="":
        continue
    row.append("JP")
    row.append(dataJP[i][1])#name
    row.append(dataJP[i][0])#img
    ingr=[]
    for j in range(2,len(dataJP[i])):
        ingr.append(dataJP[i][j])#single ingredient
    ingr = list(filter(None, ingr))#remove empty elements
    row.append(ingr)
    data.append(row)

#TW dataset
with open('data/TW.csv', mode='r', encoding="utf8") as csv_file:
    dataTW=list(csv.reader(csv_file))

for i in range(len(dataTW)):
    row=[]
    if dataTW[i][1]=="":
        continue
    row.append("TW")
    row.append(dataTW[i][1])#name TODO remove number in front of the name
    row.append(dataTW[i][0])#img
    ingr=[]
    for j in range(2,len(dataTW[i])):
        ingr.append(dataTW[i][j])#single ingredient
    ingr = list(filter(None, ingr))#remove empty elements
    row.append(ingr)
    data.append(row)

#get the ingredients in a list
with open('data/ingredients.csv', mode='r', encoding="utf8") as csv_file:
    ingredientsCSV=list(csv.reader(csv_file))

ingredients=[]
for ing in ingredientsCSV:
    ingredients.append(ing[0])


with open('data/TWN.csv', mode='r', encoding="utf8") as csv_file:
    dataTWN=list(csv.reader(csv_file))

for i in range(len(dataTWN)):
    row=[]
    if dataTWN[i][1]=="":
        continue
    row.append("TWN")
    row.append(dataTWN[i][1])#name TODO remove number in front of the name
    row.append(dataTWN[i][0])#img
    ingr=[]
    for j in range(2,len(dataTWN[i])):
        ingr.append(dataTWN[i][j])#single ingredient
    ingr = list(filter(None, ingr))#remove empty elements
    ingr=list(dict.fromkeys(getGoodIngredients(ingr,ingredients)))
    if len(ingr)<3:
        continue
    row.append(ingr)
    data.append(row)

with open('data/JPN.csv', mode='r', encoding="utf8") as csv_file:
    dataJPN=list(csv.reader(csv_file))

for i in range(len(dataJPN)):
    row=[]
    if dataJPN[i][1]=="":
        continue
    row.append("JPN")
    row.append(dataJPN[i][1])#name TODO remove number in front of the name
    row.append(dataJPN[i][0])#img
    ingr=[]
    for j in range(2,len(dataJPN[i])):
        ingr.append(dataJPN[i][j])#single ingredient
    ingr = list(filter(None, ingr))#remove empty elements
    ingr=list(dict.fromkeys(getGoodIngredients(ingr,ingredients)))
    if len(ingr)<3:
        continue
    row.append(ingr)
    data.append(row)

#separate the data of the noodles dataset since there is no color data
dataJPN=getNationData("JPN",data)
dataTWN=getNationData("TWN",data)

#retrieve the data from the files created from elaboraColori
colorData=[]
colorData16=[]
for i in range(1,5):
    f = open("data/colorData"+str(i)+".txt", "r")
    for row in f:
        colorRow=[]
        row=row.split("\t")
        row[0]=ast.literal_eval(row[0])
        row[1]=row[1].strip()
        colorData.append(row)
        for color in row[0]:
            c=RGBtoInt(int(color[0][0]*15/255),int(color[0][1]*15/255),int(color[0][2]*15/255))+1
            colorRow.append([c,color[1]])
        colorData16.append(colorRow)
    f.close()
#colorData[65][0][0][0]=colorData[65][0][0][0]*15/255

j=0
for i in range(len(colorData)):
    if colorData[i][1] == data[j][2]:
        data[j].append(colorData[i][0])
        data[j].append(colorData16[i])
    else:
        j+=1
        if colorData[i][1] == data[j][2]:
            data[j].append(colorData[i][0])
            data[j].append(colorData16[i])
        else:
            print("MISMATCH")
    j+=1

#remove rows without color data
indexes=[]
for i in range(len(data)):
    if len(data[i])!=6:
        indexes.append(i)
for i in  reversed(indexes):
    del data[i]



#divide the data in the 3 nations and then save it in .mat files for the nations and the mixed dataset
dataIT=getNationData("IT",data)
dataJP=getNationData("JP",data)
dataTW=getNationData("TW",data)
#dataJPN <--above
#dataTWN <--above
#sio.savemat("data/data.mat",{"data":data})
#sio.savemat("data/dataIT.mat",{"data":dataIT})
#sio.savemat("data/dataJP.mat",{"data":dataJP})
#sio.savemat("data/dataTW.mat",{"data":dataTW})
