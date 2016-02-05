import sys
import re
import copy

MIN_WIDTH = 1
DATA_DEPTH = 32
COUNT_WIDTH = 6

class simScaffold:
	def __init__(self):
		self.iden = ""
		self.curStr = ""
	def idenAdd(self):
		self.iden = self.iden + 2 * " "
	def idenSub(self):
		self.iden = self.iden[0:-2]	
	def addToCode(self,curStr):
		self.curStr = self.curStr + curStr
	def setParam(self,name,value):
		curStr = self.iden + "parameter " + name + " = " + str(value) + ";\n"
		self.addToCode(curStr)
	def decl(self,fName,name,bitlength,bitarray):
		curStr = self.iden + fName
		if (bitlength != "0"):
			curStr = curStr + " [" + bitlength + ":0] " + name 	
		else: 
			curStr = curStr + " " + name 
		if(len(bitarray)>0):
			curStr = curStr + " "
		for item in bitarray:
			curStr = curStr + "[0:" + item + "]"
		curStr = curStr + ";\n"	
		self.addToCode(curStr)
	def beginAlways(self,sensitivity_list,processname):
	 	curStr = self.iden + "always @("
		for item in sensitivity_list:
			curStr = curStr + item + ","		
		curStr = curStr[:-1] + ") \nbegin : "+ processname+"\n"
		self.idenAdd()
		self.addToCode(curStr)
	def endComm(self):
		self.idenSub()
		curStr = self.iden + "end\n"
		self.addToCode(curStr)	
	def endCase(self):
		self.idenSub()
		curStr = self.iden + "endcase\n"
		self.addToCode(curStr)		
	def addNNewLine(self,n):
		curStr = "\n" * n
		self.addToCode(curStr)
	def endModule (self): 
		curStr = "\n" + self.iden + "endmodule\n"
		self.addToCode(curStr)
	def getVerilog(self):
		return self.curStr	
	def commentHeader(self,strIn):
		curStr = self.iden + "//" + ("-"*80) + "\n"
		curStr = curStr + self.iden + "//" + strIn + "\n"
		curStr = curStr + self.iden + "//" + ("-"*80) + "\n"
		self.addToCode(curStr)
	def beginModule(self,name,portList):
		curStr = self.iden + "module " + name + "(\n"
		for item in portList:
			curStr = curStr + self.iden + item + ",\n"
		curStr = curStr[:-2] + "\n);\n"
		self.addToCode(curStr)
	def commentLine(self,inStr):
		curStr = "//" + ("-"*10) + inStr
		curStr = curStr.ljust(60,"-") + "\n"
		self.addToCode(curStr)
	def nextSection(self,inStr):
		self.addNNewLine(1)
		self.commentLine(inStr)
	def makeModule(self,modtype,modname,params,port):
		immStr = "#("
		for item in params:
			immStr = immStr + item + ","
		immStr = immStr[:-1] + ")"
		curStr = self.iden + modtype + " " + immStr + " " + modname + "(\n"
		for key in port:
    			curStr = curStr + self.iden + "." + (key.ljust(10," ")) + " (" + port[key] + ")" + ",\n"
		curStr = curStr[:-2] + "\n"
		curStr = curStr + self.iden + ");\n"
		self.addToCode(curStr)
	def makeComb(self,stringIn):
		curStr = self.iden + stringIn + ";\n"
		self.addToCode(curStr)
	def synSameLogicComb(self,source,operant,sign,target):
		curStr = target + " " + sign + " " 
		for i in source:
			curStr = curStr + i + operant
		curStr = curStr[:-1]
		return curStr
	def makeIfCondition(self,strIn,name):
		if(strIn != ""):
			curStr = self.iden + name + " " + "(" + strIn + ")" + " begin\n"
		else:
			curStr = self.iden + name + " begin\n"			
		self.idenAdd()
		self.addToCode(curStr)
	def makeCirBuffCode(self,num,name):
		curStr = ''
		for i in range(0,num):
			if(i==num-1):
				curStr = curStr + self.iden + name + "[0]" + " <= " + name + "[" + str(i) + "]" + ";\n"	
			else:
				curStr = curStr + self.iden + name + "[" + str(i+1) + "]" + " <= " + name + "[" + str(i)  + "]" + ";\n"	
		self.addToCode(curStr)
	def makeResetCode(self,varList,valueList,operator):
		curStr = ''
		for i in range(0,len(varList)):
			curStr = curStr + self.iden + varList[i] + " " + operator + " " + valueList[i] + ";\n"
		self.addToCode(curStr)	

	def makeMux(self,sel,muxIn,muxOut,operator,selname):
		curStr = self.iden + "case" + " " + "(" + selname + ")" + "\n"
		self.idenAdd()
		tempLen = len(self.iden + sel[0] + ": ")
		for i in range(0,len(sel)):
			curStr = curStr + self.iden + sel[i] + ": begin\n"
			curStr = curStr + " " * tempLen + muxOut + " " + operator + " " + muxIn[i] + ";\n"
			curStr = curStr + " " * tempLen + "end\n"
		self.idenSub()			
		curStr = curStr + self.iden + "endcase\n"
		self.addToCode(curStr)	
	def makeTempLogic(self,strIn):
		curStr = ''
		for i in strIn:
			curStr = curStr + self.iden + "assign " + i + ";\n"
		self.addToCode(curStr)			
	
def bin(x):
	# Courtesey from Benjamin Wiley Sittley. Back-port from 2.6. 
	out = []
	if x == 0:
		out.append('0')
	while x>0:
		out.append('01'[x & 1])
		x >>= 1
		pass
	try:
		return '0b' + ''.join(reversed(out))
	except NameError, ne2:
		out.reverse()
	return '0b' + ''.join(out)

def findOptimalComb(width):
	rMatrix1 = [{'5':0,'12':0,'16':0}, #0
	            {'5':1,'12':0,'16':0}, #1
	            {'5':1,'12':0,'16':0}, #2
	            {'5':1,'12':0,'16':0}, #3
	            {'5':1,'12':0,'16':0}, #4
	            {'5':1,'12':0,'16':0}, #5
	            {'5':2,'12':0,'16':0}, #6 
	            {'5':2,'12':0,'16':0}, #7 
	            {'5':2,'12':0,'16':0}, #8 
	            {'5':2,'12':0,'16':0}, #9
	            {'5':2,'12':0,'16':0}, #10
	            {'5':0,'12':1,'16':0}, #11
	            {'5':0,'12':1,'16':0}, #12
	            {'5':0,'12':0,'16':1}, #13
	            {'5':3,'12':0,'16':0}, #14
	            {'5':3,'12':0,'16':0}, #15
	            {'5':0,'12':0,'16':1}];#16
	rMatrix2 = [5,#0
                    4,#1
                    3,#2
                    2,#3
                    1,#4
                    0,#5
                    4,#6
                    3,#7
                    2,#8
                    1,#9
                    0,#10
                    1,#11
                    0,#12
                    3,#13
                    1,#14
                    0,#15
                    0]#16
	keyList = ["5","12","16"]
	if width > 16 :
		for i in range(17,width+1):
				tempList = []
				tempindexList = []
				tempindexList.append(i-5)
				tempindexList.append(i-12)
				tempindexList.append(i-16)
				tempList.append(rMatrix2[i-5])
				tempList.append(rMatrix2[i-12])		
				tempList.append(rMatrix2[i-16])
				temp= min(tempList)
				tempminiindex = tempList.index(temp)
				minindex = tempindexList[tempminiindex]
				newItem1 = (rMatrix1[minindex]).copy()
				newItem1[keyList[tempminiindex]]=newItem1[keyList[tempminiindex]] + 1
				newItem2 = tempList[tempminiindex]
				rMatrix1.append(newItem1)
				rMatrix2.append(newItem2)
		return [rMatrix2[len(rMatrix2)-1],rMatrix1[len(rMatrix1)-1]]

	else : 
		return [rMatrix2[width],rMatrix1[width]]

class weFIFOMake:
	def __init__(self,myPortTemplate,dataWidth):
		self.tempPivotDatIn = -1;
		self.myPortTemplate = myPortTemplate
		self.dataWidthAccum = dataWidth;
		self.dataWidth= dataWidth;

		self.tempPivotDatInBK = -1;
		self.myPortTemplateBK = myPortTemplate
		self.dataWidthAccumBK = dataWidth;
		self.dataWidthBK = dataWidth;	
	
	def reset(self):
		self.tempPivotDatIn = self.tempPivotDatInBK
	   	self.myPortTemplate = self.myPortTemplateBK
		self.dataWidthAccum = self.dataWidthAccumBK
		self.dataWidth = self.dataWidthBK

	def makeAssignDataIn(self,inNum,numOfFIFO):
		endPivot = inNum
		tempPivot = -1
		listReturn = []
		for i in range(0,numOfFIFO):
			headDatin = "data_in"
			headWire = self.myPortTemplate["data_in"] + "_" + str(inNum)+"_SUB" 
			if(inNum<=self.dataWidthAccum):
				if(numOfFIFO != 1):
					dataInAssignFrom = headDatin + "[" + str(self.tempPivotDatIn + endPivot) + ":" + str(self.tempPivotDatIn + 1) + "]"
					dataInAssignTo = headWire + "[" + str(i) + "]" 
				else:
					dataInAssignFrom = headDatin 	
					dataInAssignTo = headWire				
			else:
				if((self.tempPivotDatIn + self.dataWidthAccum) == (self.tempPivotDatIn + 1)):
					if(self.dataWidth != 1):
						subAssFrom = headDatin + "[" + str(self.tempPivotDatIn + self.dataWidthAccum) + "]"
						dataInAssignTo = headWire + "[" + str(i) + "]" 
					else:
						subAssFrom = headDatin	
						dataInAssignTo = headWire 
				else:	
					if(self.dataWidth < inNum):
						dataInAssignTo = headWire
						subAssFrom = headDatin + "[" + str(self.tempPivotDatIn + self.dataWidthAccum)  + ":" + str(self.tempPivotDatIn + 1) + "]"
					else:
						dataInAssignTo = headWire + "[" + str(i) + "]"
						subAssFrom = headDatin + "[" + str(self.tempPivotDatIn + self.dataWidthAccum)  + ":" + str(self.tempPivotDatIn + 1) + "]"
				zeroPad = str(inNum - self.dataWidthAccum)  + "'b" + "0" * (inNum - self.dataWidthAccum)
				dataInAssignFrom = ( "{" + zeroPad + ", " + subAssFrom +"}") 
			dataInStr = dataInAssignTo + " = " + dataInAssignFrom	
			self.dataWidthAccum = self.dataWidthAccum - inNum
			tempPivot = tempPivot + inNum	
			self.tempPivotDatIn = self.tempPivotDatIn + inNum;
			listReturn.append(dataInStr)	
		return listReturn	
	def makeAssignDataOut(self,inNum,numOfFIFO):
		endPivot = inNum
		tempPivot = -1
		listReturn = []
		for i in range(0,numOfFIFO):
			head1 = "data_out"
			head2 = self.myPortTemplate["data_out"] + "_" + str(inNum)+"_SUB" 
			if(inNum<=self.dataWidthAccum):
				if(numOfFIFO == 1):
					dataInAssignFrom = head2 
					dataInAssignTo = head1 
				else:
					subAss = "[" + str(self.tempPivotDatIn + endPivot) + ":" + str(self.tempPivotDatIn + 1) + "]"
					dataInAssignFrom = head2 + "[" + str(i) + "]" 
					dataInAssignTo = head1 + subAss					
			else:
				if((self.tempPivotDatIn + self.dataWidthAccum) == (self.tempPivotDatIn + 1)):
					if(self.dataWidth == 1):
						dataInAssignFrom = head2 + "[0]"
						dataInAssignTo = head1	
					else:
						dataInAssignFrom = head2 + "[" + str(i) + "]" + "[0]"
						dataInAssignTo = head1	+ "[" + str(self.dataWidth-1) + "]"				
				else:
					if(self.dataWidth < inNum):
						dataInAssignFrom = head2 + "[" +  str(self.dataWidth-1) +  ":0]"
						dataInAssignTo = head1
					else:	
						if(self.dataWidthAccum == 1 ):
							dataInAssignFrom = head2 + "[" + str(i) + "]"  + "[" + str(self.dataWidth -1)+ "]" 
							dataInAssignTo = head1	+  "[" + str(self.dataWidth -1)+ ":" + str(self.tempPivotDatIn + 1) + "]" 
						else:
							dataInAssignFrom = head2 + "[" + str(i) + "]"  + "[" + str(self.dataWidthAccum-1) + ":0" + "]" 
							dataInAssignTo = head1	+  "[" + str(self.dataWidth -1)+ ":" + str(self.tempPivotDatIn + 1) + "]" 	
			dataStr = dataInAssignTo + " = " + dataInAssignFrom
			self.dataWidthAccum = self.dataWidthAccum - inNum
			tempPivot = tempPivot + inNum	
			self.tempPivotDatIn = self.tempPivotDatIn + inNum;
			listReturn.append(dataStr)	
		return listReturn	


def main(argv):
	outputfile = 'FIFO_width_expansion.v'
	try:
		fifoWidth = long(argv[0])
	except IndexError:
		print "Usage: python FIFO_width_expansion.py <FIFO_width>"
		sys.exit(2)
	try:
		fifoWidth = long(argv[0])
	except ValueError: 
		print "FIFO_width should be an integer !"
		sys.exit(2)
	if(fifoWidth<MIN_WIDTH):
		print "FIFO_width should be more than " +  str(MIN_WIDTH) + " !" 
		sys.exit(2)

	myVerilog = simScaffold()
	header = "FIFO depth expansion of depth 5,12,16 FIFO. Width = " + str(fifoWidth)
	myVerilog.commentHeader(header)
	myVerilog.beginModule("FIFO_width_expansion",["clk","reset","put","get","data_in","empty_bar","full_bar","data_out"])
	myVerilog.nextSection("Parameter")
	myVerilog.setParam("DATA_DEPTH",str(DATA_DEPTH))
	myVerilog.setParam("COUNT_WIDTH",str(COUNT_WIDTH))
	myPortTemplate = {"clk":"clk", 
		          "reset":"reset",
                          "put":"put",
                          "get":"get",
		          "data_in":"DATA_IN_SUB",
		          "data_out":"DATA_OUT_SUB",
			  "full_bar":"FULL_BAR_SUB",
			  "empty_bar":"EMPTY_BAR_SUB",
			  }
	optimalResult = findOptimalComb(fifoWidth)
	numRedundantBit = optimalResult[0]
	numOfFIFO =  optimalResult[1]

	myVerilog.nextSection("Input Declaration")
	myVerilog.decl("input","clk","0",[])
	myVerilog.decl("input","reset","0",[])
	myVerilog.decl("input","put","0",[])
	myVerilog.decl("input","get","0",[])
	myVerilog.decl("input","data_in",str(fifoWidth - 1),[])

	myVerilog.nextSection("Output Declaration")
	myVerilog.decl("output","data_out",str(fifoWidth - 1),[])
	myVerilog.decl("output","empty_bar","0",[])
	myVerilog.decl("output","full_bar","0",[])

	myVerilog.nextSection("Interface Elements")
	myVerilog.decl("wire","data_out",str(fifoWidth - 1),[])
	myVerilog.decl("wire","empty_bar","0",[])
	myVerilog.decl("wire","full_bar","0",[])

	myVerilog.nextSection("Internal Elements")

	if(numOfFIFO["5"] >1):
		myVerilog.decl("wire",myPortTemplate["full_bar"]+"_5_SUB", "0" ,[str(numOfFIFO["5"] - 1)])
		myVerilog.decl("wire",myPortTemplate["empty_bar"]+"_5_SUB", "0" ,[str(numOfFIFO["5"] - 1)])
		myVerilog.decl("wire",myPortTemplate["data_in"]+"_5_SUB",str(5 - 1),[str(numOfFIFO["5"] - 1)])
		myVerilog.decl("wire",myPortTemplate["data_out"]+"_5_SUB",str(5 - 1),[str(numOfFIFO["5"] - 1)])
	elif (numOfFIFO["5"]  == 1):
		myVerilog.decl("wire",myPortTemplate["full_bar"]+"_5_SUB", "0",[])
		myVerilog.decl("wire",myPortTemplate["empty_bar"]+"_5_SUB", "0",[])
		myVerilog.decl("wire",myPortTemplate["data_in"]+"_5_SUB",str(5 - 1),[])	
		myVerilog.decl("wire",myPortTemplate["data_out"]+"_5_SUB",str(5 - 1),[])
	
	if(numOfFIFO["12"] >1):
		myVerilog.decl("wire",myPortTemplate["full_bar"]+"_12_SUB", "0" ,[str(numOfFIFO["12"] - 1)])
		myVerilog.decl("wire",myPortTemplate["empty_bar"]+"_12_SUB", "0" ,[str(numOfFIFO["12"] - 1)])
		myVerilog.decl("wire",myPortTemplate["data_in"]+"_12_SUB",str(12 - 1),[str(numOfFIFO["12"] - 1)])
		myVerilog.decl("wire",myPortTemplate["data_out"]+"_12_SUB",str(12 - 1),[str(numOfFIFO["12"] - 1)])
	elif (numOfFIFO["12"]  == 1):
		myVerilog.decl("wire",myPortTemplate["full_bar"]+"_12_SUB", "0",[])
		myVerilog.decl("wire",myPortTemplate["empty_bar"]+"_12_SUB", "0",[])	
		myVerilog.decl("wire",myPortTemplate["data_in"]+"_12_SUB",str(12 - 1),[])
		myVerilog.decl("wire",myPortTemplate["data_out"]+"_12_SUB",str(12 - 1),[])
		
	if(numOfFIFO["16"] >1):
		myVerilog.decl("wire",myPortTemplate["full_bar"]+"_16_SUB", "0",[str(numOfFIFO["16"] - 1)])
		myVerilog.decl("wire",myPortTemplate["empty_bar"]+"_16_SUB", "0",[str(numOfFIFO["16"] - 1)])
		myVerilog.decl("wire",myPortTemplate["data_in"]+"_16_SUB",str(16 - 1),[str(numOfFIFO["16"] - 1)])
		myVerilog.decl("wire",myPortTemplate["data_out"]+"_16_SUB",str(16 - 1),[str(numOfFIFO["16"] - 1)])
	elif (numOfFIFO["16"]  == 1):
		myVerilog.decl("wire",myPortTemplate["full_bar"]+"_16_SUB", "0",[])
		myVerilog.decl("wire",myPortTemplate["empty_bar"]+"_16_SUB", "0",[])	
		myVerilog.decl("wire",myPortTemplate["data_in"]+"_16_SUB",str(16 - 1),[])
		myVerilog.decl("wire",myPortTemplate["data_out"]+"_16_SUB",str(16 - 1),[])


	myVerilog.nextSection("Sub Modules")

	for i in range(0,numOfFIFO["5"]):
		instancename = "FIFO5_" + str(i)
		myPortTemplate2 = myPortTemplate.copy()
		if(numOfFIFO["5"]>1):
			subAss = "[" + str(i) + "]"
		else:
			subAss = ""
		myPortTemplate2["data_in"] = myPortTemplate["data_in"] + "_5_SUB" + subAss
		myPortTemplate2["data_out"] = myPortTemplate["data_out"] + "_5_SUB" + subAss
		myPortTemplate2["full_bar"] = myPortTemplate["full_bar"]  + "_5_SUB" + subAss
		myPortTemplate2["empty_bar"] = myPortTemplate["empty_bar"] + "_5_SUB" + subAss
		myVerilog.makeModule("FIFO5",instancename,["DATA_DEPTH","COUNT_WIDTH"],myPortTemplate2)
		myVerilog.addNNewLine(1)

	for i in range(0,numOfFIFO["12"]):
		instancename = "FIFO12_" + str(i)
		myPortTemplate2 = myPortTemplate.copy()
		if(numOfFIFO["5"]>1):
			subAss = "[" + str(i) + "]"
		else:
			subAss = ""
		myPortTemplate2["data_in"] = myPortTemplate["data_in"] + "_12_SUB" + subAss
		myPortTemplate2["data_out"] = myPortTemplate["data_out"] + "_12_SUB" + subAss
		myPortTemplate2["full_bar"] = myPortTemplate["full_bar"]  + "_12_SUB" + subAss
		myPortTemplate2["empty_bar"] = myPortTemplate["empty_bar"] + "_12_SUB" + subAss
		myVerilog.makeModule("FIFO12",instancename,["DATA_DEPTH","COUNT_WIDTH"],myPortTemplate2)
		myVerilog.addNNewLine(1)

	for i in range(0,numOfFIFO["16"]):
		instancename = "FIFO16_" + str(i)
		myPortTemplate2 = myPortTemplate.copy()		
		if(numOfFIFO["5"]>1):
			subAss = "[" + str(i) + "]"
		else:
			subAss = ""
		myPortTemplate2["data_in"] = myPortTemplate["data_in"]  + "_16_SUB" + subAss
		myPortTemplate2["data_out"] = myPortTemplate["data_out"] + "_16_SUB" + subAss
		myPortTemplate2["full_bar"] = myPortTemplate["full_bar"] + "_16_SUB" + subAss
		myPortTemplate2["empty_bar"] = myPortTemplate["empty_bar"] + "_16_SUB" + subAss
		myVerilog.makeModule("FIFO16",instancename,["DATA_DEPTH","COUNT_WIDTH"],myPortTemplate2)
		myVerilog.addNNewLine(1)


	myweFIFOMake = weFIFOMake(myPortTemplate,fifoWidth)
	makeDataIn = myweFIFOMake.makeAssignDataIn(5,numOfFIFO["5"])
	myVerilog.makeTempLogic(makeDataIn)
	makeDataIn = myweFIFOMake.makeAssignDataIn(12,numOfFIFO["12"])
	myVerilog.makeTempLogic(makeDataIn)
	makeDataIn = myweFIFOMake.makeAssignDataIn(16,numOfFIFO["16"])
	myVerilog.makeTempLogic(makeDataIn)
	myVerilog.addNNewLine(1)
	myweFIFOMake.reset()
	makeDataIn = myweFIFOMake.makeAssignDataOut(5,numOfFIFO["5"])
	myVerilog.makeTempLogic(makeDataIn)
	makeDataIn = myweFIFOMake.makeAssignDataOut(12,numOfFIFO["12"])
	myVerilog.makeTempLogic(makeDataIn)
	makeDataIn = myweFIFOMake.makeAssignDataOut(16,numOfFIFO["16"])
	myVerilog.makeTempLogic(makeDataIn)

	if (numOfFIFO["5"] == 0 ):
		if (numOfFIFO["12"] == 0 ):
			if (numOfFIFO["16"] == 0 ):
				print "Unknown runtime error"
				sys.exit(2)
			else:
				if(numOfFIFO["16"] == 1):
					strInFullBar = "full_bar" + " = "+ myPortTemplate["full_bar"] + "_16_" + "SUB"
					strInEmptyBar = "empty_bar" + " = "+ myPortTemplate["full_bar"] + "_16_" + "SUB"
				else:
					strInFullBar = "full_bar" + " = "+ myPortTemplate["full_bar"] + "_16_" + "SUB[0]"
					strInEmptyBar = "empty_bar" + " = "+ myPortTemplate["full_bar"] + "_16_" + "SUB[0]"
		else:
			if(numOfFIFO["12"] == 1):
				strInFullBar = "full_bar" + " = "+ myPortTemplate["full_bar"] + "_12_" + "SUB"
				strInEmptyBar = "empty_bar" + " = "+ myPortTemplate["full_bar"] + "_12_" + "SUB"
			else:	
				strInFullBar = "full_bar" + " = "+ myPortTemplate["full_bar"] + "_12_" + "SUB[0]"
				strInEmptyBar = "empty_bar" + " = "+ myPortTemplate["full_bar"] + "_12_" + "SUB[0]"
	else:
		if(numOfFIFO["5"] == 1):
			strInFullBar = "full_bar" + " = "+ myPortTemplate["full_bar"] + "_5_" + "SUB"
			strInEmptyBar = "empty_bar" + " = "+ myPortTemplate["full_bar"] + "_5_" + "SUB"
		else:	
			strInFullBar = "full_bar" + " = "+ myPortTemplate["full_bar"] + "_5_" + "SUB[0]"
			strInEmptyBar = "empty_bar" + " = "+ myPortTemplate["full_bar"] + "_5_" + "SUB[0]"
	myVerilog.addNNewLine(1)
	myVerilog.makeTempLogic([strInFullBar])
	myVerilog.makeTempLogic([strInEmptyBar])

	myVerilog.endModule()
	codeBuffer = myVerilog.getVerilog()
	fo = open(outputfile, "w")
	fo.write(codeBuffer)
	fo.close()

if __name__ == "__main__":
	main(sys.argv[1:])
