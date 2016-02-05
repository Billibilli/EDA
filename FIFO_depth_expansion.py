import sys
import re
import copy

MIN_DEPTH = 8
DATA_WIDTH = 2
COUNT_WIDTH = 4

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
		curStr = self.iden + "parameter " + name + "=" + str(value) + ";\n"
		self.addToCode(curStr)
	def decl(self,fName,name,bitlength,bitarray):
		curStr = self.iden + fName
		if (bitlength != "1"):
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

def main(argv):
	outputfile = 'FIFO_depth_expansion.v'
	try:
		fifoDepth = long(argv[0])
	except IndexError:
		print "Usage: python FIFO_depth_expansion.py <FIFO_depth>"
		sys.exit(2)
	try:
		fifoDepth = long(argv[0])
	except ValueError: 
		print "FIFO_depth should be an integer !"
		sys.exit(2)
	if(fifoDepth<MIN_DEPTH):
		print "FIFO_depth should be more than " +  str(MIN_DEPTH) + " !" 
		sys.exit(2)
	if(((fifoDepth/MIN_DEPTH) != 0 and (((fifoDepth/MIN_DEPTH) & ((fifoDepth/MIN_DEPTH) - 1)) == 0))==False):
		print "FIFO_depth/8 should be a power of 2 !"
		sys.exit(2)
	myVerilog = simScaffold()
	header = "FIFO depth expansion of depth 8 FIFO. Depth = " + str(fifoDepth)
	myVerilog.commentHeader(header)
	myVerilog.beginModule("FIFO_depth_expansion",["clk","reset","put","get","data_in","empty_bar","full_bar","data_out"])
	myVerilog.nextSection("Parameter")
	myVerilog.setParam("DATA_WIDTH","2")
	myVerilog.nextSection("Input Declaration")
	myVerilog.decl("input","clk","1",[])
	myVerilog.decl("input","reset","1",[])
	myVerilog.decl("input","put","1",[])
	myVerilog.decl("input","get","1",[])
	myVerilog.decl("input","data_in","DATA_WIDTH - 1",[])
	myVerilog.nextSection("Output Declaration")
	myVerilog.decl("output","data_out","DATA_WIDTH - 1",[])
	myVerilog.decl("output","empty_bar","1",[])
	myVerilog.decl("output","full_bar","1",[])
	myPortTemplate = {"clk":"clk", 
		          "reset":"reset",
                          "put":"PUTSUB",
                          "get":"GETSUB",
		          "data_in":"data_in",
		          "data_out":"DATA_OUT_SUB",
			  "full_bar":"FULL_BAR_SUB",
			  "empty_bar":"EMPTY_BAR_SUB",
			  }
	numOfFIFO=fifoDepth/MIN_DEPTH
	myVerilog.nextSection("Interface Elements")
	myVerilog.decl("reg","data_out","DATA_WIDTH - 1",[])
	myVerilog.decl("reg","empty_bar","1",[])
	myVerilog.decl("reg","full_bar","1",[])
	myVerilog.nextSection("Internal Elements")
	myVerilog.decl("reg",myPortTemplate["put"],str(numOfFIFO - 1 ),[])
	myVerilog.decl("reg",myPortTemplate["get"],str(numOfFIFO - 1 ),[])
	myVerilog.decl("wire",myPortTemplate["put"]+"SUB",str(numOfFIFO - 1 ),[])
	myVerilog.decl("wire",myPortTemplate["get"]+"SUB",str(numOfFIFO - 1 ),[])
	myVerilog.decl("wire",myPortTemplate["full_bar"],str(numOfFIFO - 1 ),[])
	myVerilog.decl("wire",myPortTemplate["empty_bar"],str(numOfFIFO - 1 ),[])
	myVerilog.decl("wire",myPortTemplate["data_out"],"DATA_WIDTH - 1",[str(numOfFIFO - 1)])
	myVerilog.nextSection("Sub Modules")
	for i in range(0,numOfFIFO):
		instancename = "FIFO" + str(i)
		myPortTemplate2 = myPortTemplate.copy()
		myPortTemplate2["put"] = myPortTemplate["put"] + "SUB"+ "[" + str(i) + "]" 
		myPortTemplate2["get"] = myPortTemplate["get"] + "SUB"+ "[" + str(i) + "]" 
		myPortTemplate2["data_out"] = myPortTemplate["data_out"] + "[" + str(i) + "]" 
		myPortTemplate2["full_bar"] = myPortTemplate["full_bar"] + "[" + str(i) + "]" 
		myPortTemplate2["empty_bar"] = myPortTemplate["empty_bar"] + "[" + str(i) + "]" 
		myVerilog.makeModule("FIFO",instancename,["DATA_WIDTH",str(MIN_DEPTH),str(COUNT_WIDTH)],myPortTemplate2)
		myVerilog.addNNewLine(1)

	myVerilog.nextSection("Top Level Processes")

	myVerilog.beginAlways(["*"],"FULL_BAR_GEN_PROCESS")
	operantList = []
	for i in range(0,numOfFIFO):
		 operantList.append(myPortTemplate["full_bar"] + "[" + str(i) + "]")
	createdCode = myVerilog.synSameLogicComb(operantList,"|","=","full_bar")
	myVerilog.makeComb(createdCode)
	myVerilog.endComm()
	myVerilog.addNNewLine(1)

	myVerilog.beginAlways(["*"],"EMPTY_BAR_GEN_PROCESS")
	operantList = []
	for i in range(0,numOfFIFO):
		 operantList.append(myPortTemplate["empty_bar"] + "[" + str(i) + "]")
	createdCode = myVerilog.synSameLogicComb(operantList,"|","=","empty_bar")
	myVerilog.makeComb(createdCode)
	myVerilog.endComm()
	myVerilog.addNNewLine(1)
 
	myVerilog.beginAlways(["posedge clk","posedge reset"],"PUT_PTR_PROCESS")
	myVerilog.makeIfCondition("reset == 1'b1","if")
	opList = []
	valueList = []
	for i in range(0,numOfFIFO):
		opList.append(myPortTemplate["put"] + "[" + str(i) + "]")
		if(i== 0):
			valueList.append("1'b1")
		else:
			valueList.append("1'b0")
	myVerilog.makeResetCode(opList,valueList,"<=")
	myVerilog.endComm()
	myVerilog.makeIfCondition("","else")
	myVerilog.makeIfCondition("put == 1'b1","if")
	myVerilog.makeCirBuffCode(numOfFIFO,myPortTemplate["put"])
	myVerilog.endComm()
	myVerilog.endComm()
	myVerilog.endComm()
	myVerilog.addNNewLine(1)

	myVerilog.beginAlways(["posedge clk","posedge reset"],"GET_PTR_PROCESS")
	myVerilog.makeIfCondition("reset == 1'b1","if")
	opList = []
	valueList = []
	for i in range(0,numOfFIFO):
		opList.append(myPortTemplate["get"] + "[" + str(i) + "]")
		if(i == 0):
			valueList.append("1'b1")
		else:
			valueList.append("1'b0")
	myVerilog.makeResetCode(opList,valueList,"<=")
	myVerilog.endComm()
	myVerilog.makeIfCondition("","else")
	myVerilog.makeIfCondition("get == 1'b1","if")
	myVerilog.makeCirBuffCode(numOfFIFO,myPortTemplate["get"])
	myVerilog.endComm()
	myVerilog.endComm()
	myVerilog.endComm()
	myVerilog.addNNewLine(1)


	temp = long(1)
	muxcase = []
	muxinput = []
	for i in range(0,numOfFIFO):
		muxcase.append(str(numOfFIFO) + "'b" + str(bin(temp))[2:].rjust(numOfFIFO,"0"))
		muxinput.append(myPortTemplate["data_out"]+"["+str(i)+"]")
		temp = temp<<1

	myVerilog.beginAlways(["*"],"DATA_OUT_MUX_PROCESS")
	myVerilog.makeMux(muxcase,muxinput,"data_out","=",myPortTemplate["get"])
	myVerilog.endComm()
	myVerilog.addNNewLine(1)



	codeList = []
	for i in range(0,numOfFIFO):
		codeList.append(myPortTemplate["put"]+"SUB"+'['+str(i)+']'+ " = "+myPortTemplate["put"]+'['+str(i)+']'+ ' & put' )
	myVerilog.makeTempLogic(codeList)
	myVerilog.addNNewLine(1)



	codeList = []
	for i in range(0,numOfFIFO):
		codeList.append(myPortTemplate["get"]+"SUB"+'['+str(i)+']'+ " = "+myPortTemplate["get"]+'['+str(i)+']'+ ' & get' )
	myVerilog.makeTempLogic(codeList)
	myVerilog.addNNewLine(1)
	myVerilog.endModule()

	codeBuffer = myVerilog.getVerilog()
	fo = open(outputfile, "w")
	fo.write(codeBuffer)
	fo.close()

if __name__ == "__main__":
	main(sys.argv[1:])
