import math
import scipy.signal
import matplotlib.pyplot as plt
import matplotlib.axes as ax
import matplotlib.figure as fig
import numpy as np
import cv2 as cv2
import csv as csv
#I define a function that rounds the data (number, type of data, base of rounding, if it is the minimum or maximum of the range), it will be used to determine the maximum and minimum values of the data and approximate them to make them divisible
def myround(x,tipo, base,l):
	y=tipo(base * round(float(x)/base))
	if l==max:
		if(y-x)<0:
			return(y+base)
		else :
			return(y)
	else:
		if(y-x)>0:
			return(y-base)
		else:
			return (y)
soglia= 0
print('Height Threshold : ',soglia)
name="06Feb2019Tonale"#Enter the name of the .csv file here, it will also become the title of the plots
print('Date and place of study',name)
file = open(name+".csv", 'r')
allLines = file.read().split("\n")
allLines.remove(allLines[0]) #the first line contains the names of the axes
allLines.remove(allLines[len(allLines) - 1]) #the last line is empty
data = []
altezza = []
for line in allLines:
	elements = line.split(',')
	#print ('elements',elements)
	data.append([math.degrees(float(elements[0])), float(elements[1])]) #I turn radians into degrees
	altezza.append(int(elements[2]))

print("data: ",len(data))
dataX = [data[i][0] for i in range(len(data))]
dataY = [data[i][1] for i in range(len(data))]
count_line = 0
count_col = 0
count = 0
tot_val = 0
count_dens = 0
container = {}

# range column (degrees)
col_start = myround(min(dataX),int,5,min)
col_end = myround(max(dataX),int,5,max)
col_step = 5

# range rows
line_start = myround(min(dataY),float,0.005,min)
line_end = myround(max(dataY),float,0.005,max)
line_step = 0.01

densityData = np.zeros((len(range(col_start,col_end,col_step)), len(np.arange(line_start, line_end, line_step)))) # creo array vuoto di dimensioni (colonne,righe)
print("Created array whith shape:",densityData.shape)
data.sort(key=lambda x: x[0]) # i reorder the array according to the first value of the tuple (degrees)
#print("Data: ",data[0])
for i in range(col_start, col_end, col_step):#divido per gruppi rispetto a 5 gradi
	tmpArr = []
	while True:
		if i<=90:
			if round(data[count][0]) in range(i,i+col_step) and count != len(data) - 1:
				if altezza[count] > soglia:
					tmpArr.append(data[count])
				count += 1
			else:
				break
		else:
			break
	if tmpArr != []:
		container.update({i : tmpArr})
keys = [key for key in container.keys()] # array of keys
for key in keys:
	count_line = 0
	for i in np.arange(line_start, line_end, line_step):
		count_dens = 0
		for j in range(len(container[key])): #I also divide the y-axis (which will then become x-axis)
			if container[key][j][1] > i and container[key][j][1] < i + line_step:
				count_dens += 1
				tot_val += 1
		densityData[count_col][count_line] = count_dens
		count_line += 1
	count_col +=1
densityData0=densityData
print("Total sample=",tot_val)
#print("Prima",*densityData0)

densityData_mom = np.zeros((len(range(col_start,col_end,col_step)), len(np.arange(line_start, line_end, line_step)))) # creo array vuoto di dimensioni (colonne,righe)
densityData_line = np.zeros((len(range(col_start,col_end,col_step)), len(np.arange(line_start, line_end, line_step)))) # creo array vuoto di dimensioni (colonne,righe)

#If there are less than 2 elements, they are reset to zero.
elementiNellaColonna = 0
for col in range(len(densityData)):
	#print("the elements in the column[",col,"] are:  ")
	for element in range(len(densityData[col])):
		densityData_mom[col][element]=densityData[col][element]
		if densityData[col][element] > 0:
			elementiNellaColonna +=1
	#print(elementiNellaColonna)

	if elementiNellaColonna < 5:
		densityData[col] = np.zeros(densityData[col].shape)
	elementiNellaColonna = 0

for col in range(len(densityData)):
	contcolonna=0
	maximum_col=densityData_mom[col].max()
	#print("maximum_col[",col,"]: ",maximum_col)
	for element in reversed(range(len(densityData[col]))):
		if (densityData_mom[col][element]==maximum_col) and maximum_col!=0:
			#print("Element: ",element)
			densityData_line[col][element]=densityData_mom[col][element]
			contcolonna+=1
			break
	#print("contccolumn ",contcolonna)
first_counter = 0
for col in range(len(densityData)):
	for element in range(len(densityData[col])):
		if (densityData_line[col][element])!=0.0:
			# print("["+ str(col) + "," + str(element) + "]")
			first_counter += 1
			densityData_line[col][element]=1400 #sis used to make the line all the same colour otherwise it would change colour depending on the amount of data.
		#print("densityData_line[",col,"][",element,"]: ",densityData_line[col][element])
#print("type: ",type(densityData_line))
for col in range(len(densityData)):
	if (densityData[col].sum())!=0:
		densityData[col] /= densityData[col].sum()

densityData_line1=densityData_line.T
# print(first_counter)
# print(densityData_line1)
# plt.plot(densityData_line1)
# print(densityData_line1.shape)
xLabel = np.arange(line_start, line_end, line_step)
xLabelRounded = [round(label,3) for label in xLabel] #rounding the data on the y-axis when 32-bit
yLabelRounded = np.array(range(col_start, col_end, col_step))
first_array = np.zeros([2,first_counter])
first_counter_2 = 0
for col in range(len(densityData)):
	for element in range(len(densityData[col])):
		if (densityData_line[col][element])!=0.0:
			first_array[0][first_counter_2] = yLabelRounded[col]
			first_array[1][first_counter_2] = xLabelRounded[element]
			first_counter_2 += 1
print ('Length x:',len(first_array[0]))
numero=int(input('Enter a number less than or equal to length as long as it is odd= '))
yhat = scipy.signal.savgol_filter(first_array[1],numero,7)
plt.plot(first_array[0], first_array[1])
plt.plot(first_array[0], yhat, color='red')
plt.ylabel('Norm Diff B2-B8')
plt.xlabel('Angle of incidence of the sun')
plt.title(name + 'Moda')
plt.show()


with open(name+'Moda.csv', 'a') as csvfile:
	fieldnames = ['Nome', 'Angolo di incidenza','DN interpolata','DN']
	writer = csv.DictWriter(csvfile,delimiter=',', fieldnames=fieldnames)
	str_first_array_1 = ""
	for element in first_array[0]:
		str_first_array_1 += str(int(element)) + " "
	#print(str_first_array_1)
	str_first_array_2 = ""
	for element in first_array[1]:
		str_first_array_2 += str(float(element)) + " "
	#print(str_first_array_2)
	str_first_array_3 = ""
	for element in yhat:
		str_first_array_3 += str(float(element)) + " "
	#print(str_first_array_3)
	writer.writeheader()
	writer.writerow({'Nome': name, 'Angolo di incidenza': str_first_array_1,'DN interpolata': str_first_array_3,'DN':str_first_array_2})

#Moda maintaining the value of the samples
#plt.imshow(densityData_line.T,origin='lower')
#plt.ylabel('Norm Diff B2-B8')
#plt.xlabel('Angle of incidence of the sun')
#plt.title(name+'ModaeValore')

#I add the values to the axes (by default the previously created ranges (55,21) would be put in, not the assumed values)
#xLabel = np.arange(line_start, line_end, line_step)
#xLabelRounded = [round(label,3) for label in xLabel] #rounding the data on the y-axis when at 32 bits
#plt.yticks(np.array(range(densityData.shape[1])), xLabelRounded)#assex
#plt.tick_params(axis='x', rotation=90)
#plt.xticks(np.array(range(densityData.shape[0])), np.array(range(col_start, col_end, col_step)))#assey
#plt.clim(0,0.5)
#plt.colorbar()
#plt.savefig(name+".png", bbox_inches='tight',dpi=600)
#plt.show()

#prints the matrix calculated with the implemented function
#print("After",*densityData)
#print("Density max",densityData.max())#print the max value obtained

#plt.imshow(densityData0,origin='lower')#not normalised
#plt.imshow(densityData0/tot_val,origin='lower')#normalised by tot_val
plt.imshow(densityData.T,origin='lower')#normalised for column values
plt.ylabel('Norm Diff B2-B8')
plt.xlabel('Angle of incidence of the sun')
plt.title(name)
#print("Density of the point [0][3]:",(densityData)[0][3])
#print("Max densityData ",densityData.max())
#I add the values to the axes (by default the previously created ranges (55,21) would be put in, not the assumed values)
xLabel = np.arange(line_start, line_end, line_step)
print('Range: ',range(densityData.shape[1]))
#print('Range2: ',xLabelRounded)
xLabelRounded = [round(label,3) for label in xLabel] #rounding the data on the y-axis when at 32 bits
plt.yticks(np.array(range(densityData.shape[1])), xLabelRounded)#assex
plt.tick_params(axis='x', rotation=90)
plt.xticks(np.array(range(densityData.shape[0])), np.array(range(col_start, col_end, col_step)))#assey
plt.clim(0,0.5)
plt.colorbar()
#plt.savefig(name+".png", bbox_inches='tight',dpi=600)
plt.show()
#densityData=np.array(densityData)
print("Density data: ",densityData.shape)

dataXY=densityData.reshape([2,int((densityData.shape[0]*densityData.shape[1])/2)])

dataX1 = [densityData[0][i] for i in range(len(densityData))]
dataY1 = [densityData[i][1] for i in range(len(densityData))]

np.set_printoptions(threshold=np.inf)
#print("densitydata: ",densityData,)

#Using the function hist2d
plt.hist2d(dataY, dataX,bins=38,range=[[line_start, line_end],[col_start, col_end]] ,density=False)
#Three arrays are created, the first is a two-dimensional array in which the density can be seen by specifying the exact position,
#the other two are one-dimensional and correspond to the angle ranges[1] and B2-B8 difference[2].

#print the matrix calculated with hist2d
#print("print hist2d:",*plt.hist2d(dataX, dataY,bins=30,range=[[col_start, col_end], [line_start, line_end]])[0])

#Plot hist2d
plt.ylabel('Angolo di incidenza del sole')
plt.xlabel('Valore Diff B2-B8')
plt.title(name+"2d")
plt.colorbar()
#figure.set_size_inches(32, 18)
#plt.savefig(name+"2d.png", bbox_inches='tight',dpi=600)
plt.show()

#Plot of the scatterplot
plt.grid(True,linestyle='-', linewidth=0.3)
plt.scatter(dataXY[0],dataXY[1]) # scatterplot
plt.title("Scatter plot " + name)
plt.show()

with open(name+'Scatter.csv', 'a') as csvfile:
	fieldnames = ['Nome', 'Angolo di incidenza','DN']
	writer = csv.DictWriter(csvfile,delimiter=',', fieldnames=fieldnames)
	str_scat_array_1 = ""
	for element in dataX:
		str_scat_array_1 += str(int(element)) + " "
	#print(str_scat_array_1)
	str_scat_array_2 = ""
	for element in dataY:
		str_scat_array_2 += str(float(element)) + " "
	#print(str_scat_array_2)
	writer.writeheader()
	writer.writerow({'Nome': name, 'Angolo di incidenza': str_scat_array_1,'DN': str_scat_array_2})

cv2.waitKey(0)
cv2.destroyAllWindows
