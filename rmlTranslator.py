import pandas as pd
regX, regY, regZ = 0, 0, 0
valXYZ = [0, 0, 0]

excludeChar = ['%', '(', '#', ' ', 'O']
commandsAllNC = []

with open('nctest.nc') as f:
    lines = f.readlines()
    for line in lines:
        if(line != '\n'):
            lineIgnore = False
            for char in excludeChar:
                if(line[0] == char):
                    lineIgnore = True
            if(lineIgnore == False):
                cutLine = len(line)-1
                #print(repr(line[:cutLine]))
                lineToPhase = line[:cutLine]
                multiLine = lineToPhase.split(' ')
                
                
                #######
                
                if(multiLine[0][0] == 'X' or multiLine[0][0] == 'Y' or multiLine[0][0] == 'Z'):
                    multiLine.insert(0, 'G1')
                    
                #print(multiLine)
                #######
                for i in multiLine:
                    commandsAllNC.append(i)
                
                #if(len(multiLine) > 1):
                #    if(multiLine[1][0] == 'G' or multiLine[1][0] == 'M'):
                #        print(multiLine)
    #print(commandsAllNC)
#for p in commandsAllNC:
#    print(p)    
    
    
newDocToggle = True
linesDivided = []
newLine = []
for i in commandsAllNC:
       
    if(len(newLine) == 0):
        newLine.append(i)
    else:
        if(i[0] == 'G' or i[0] == 'M'):
            linesDivided.append(newLine)
            newLine = []
            newLine.append(i)
        else:
            newLine.append(i)
            
linesDivided2 = []           
for line in linesDivided:
    idReg = 100
    logFOcc = 0
    for itemID in range(len(line)):
        if(line[itemID][0] == 'F'):
            logFOcc += 1
            if(logFOcc > 1):
                idReg = itemID
    if(logFOcc > 1):
        newLine = []
        newLine2 = []
        for itemID in range(len(line)):
            if(itemID < idReg-1):
                newLine.append(line[itemID])
            else:
                newLine2.append('G1')
                for i in range(itemID, len(line)):
                    newLine2.append(line[i])
        linesDivided2.append(newLine)
        linesDivided2.append(newLine2)
    else:
        linesDivided2.append(line)
        

#for i in linesDivided2:
#    print(i)       

def reformatXYZ(itemsAvail, newDocToggle):
    #if(newDocToggle == True):
        
    #    newDocToggle = False 
    #else:
    #    valXYZ = [regX, regY, regZ]
        
    global valXYZ
    global regX
    global regY
    global regZ
    
    valXYZ = [regX, regY, regZ]
        
    for item in itemsAvail:
        if(item[0] == 'X'):
            valXYZ[0] = str(float(item[1:])*100)
            regX = valXYZ[0]
            
        elif(item[0] == 'Y'):
            valXYZ[1] = str(float(item[1:])*100)
            regY = valXYZ[1]
            
        elif(item[0] == 'Z'):
            valXYZ[2] = str(float(item[1:])*10)
            regZ = valXYZ[2]
        
           
           
    XYZText = 'Z{},{},{}'.format(valXYZ[0], valXYZ[1], valXYZ[2])
    return XYZText
    
def addHeaderFooter(commandBody):
    headerRML = [';;^DF;','!MC0;','V50.0;', 'F3.0;', '^PR;','Z0,0,15500;','J1;','^PA;','!RC15;']
    footerRML = ['^PR;','Z0,0,15500;','!MC0;','^DF;']
    newCommandRML = []
    for i in headerRML:
        newCommandRML.append(i)
    for j in commandBody:
        newCommandRML.append(j)
    for k in footerRML:
        newCommandRML.append(k)
        
    return newCommandRML
    
def saveFile(lines, name):
    filename = 'RML_{}.rml'.format(name)
    with open('RML_testFile.rml', 'w') as f:
        for line in lines:
            f.write(line)
            f.write('\n')
    print('done writing RML file')
    
    
df = pd.read_excel('gcodeRMLComp.xls')
CommandsRML = []
#print(df[df['NC']=='M3 '].index.item())
#column_NC = df.iloc[:,0]
newCommandRML = []
for line in linesDivided2:
    itemTemp = line[0]
    if(df.loc[df['NC']== str(itemTemp)].RML.size > 0):
        corresponingItem = (df.loc[df['NC']== str(itemTemp)].RML.item())
        if(corresponingItem != 0):
            corresponingID = corresponingItem[0]
            #print('\n')
            #print(line)
            
            if(corresponingID == 'Z'):
                prevItem = '0' #F should never appear before X,Y or Z and therefore will be reassigned
                for item in line[1:]:
                    if(item[0] == 'F'):
                        #logFOcc = 0
                        velVal = item[1:]
                        if(prevItem[0] == 'X' or prevItem[0] == 'Y'):
                            resSpeedComm = 'F{}'.format(velVal)
                            #print('line: {} has been turned into: {}'.format(item,resSpeedComm))
                            #logFOcc += 1
                        elif(prevItem[0] == 'Z'):
                            resSpeedComm = 'V{}'.format(velVal)
                            #print('line: {} has been turned into: {}'.format(item,resSpeedComm))
                            #logFOcc += 1
                        #else:
                        #    print('prevItem not recognized: {}'.format(prevItem))
                    prevItem = item
                    
                    
                    
                    
                CommandsRML.append(reformatXYZ(line[1:], newDocToggle))
            
            else:
                CommandsRML.append(corresponingItem)
            
   # except:
    #    print('EXCEPTION')

CommandsRML = addHeaderFooter(CommandsRML)
for some in CommandsRML:
    print(some)
    #pass

lines = CommandsRML

with open('RML_testFile.rml', 'w') as f:
    for line in lines:
        f.write(line)
        f.write('\n')
print('done writing RML file')
############what do we do with: 
    ### nc-F as rml-F or rml-V; 
    ### missing F; alphaNC seems to rely on predefined values
    ### Offset Variables declared with ao #560...
    ### Absolute;
    ### tool change 
    ### etc 