import sys
import re

MAX_DATAWIDTH = 32
MIN_DATAWIDTH = 8

class CRCsyn:

	def __init__ (self,dataWidth,polynomial,iden):
		self.dataWidth = dataWidth + len(polynomial) - 1
		self.polynomial = polynomial
		self.iden = iden
		self.dataWidthRaw = dataWidth

	def genMat(self):
		self.matrixH = []
		curInput = long(1)
		term  = len(self.polynomial)-1
		if self.dataWidth>term:
			for i in range(0,term):
				self.matrixH.append(self.crcSerial(curInput,0))
				curInput = curInput <<1
			#print curInput
			for i in range(term,self.dataWidthRaw):
				#left for optimization
				self.matrixH.append(self.crcSerial(curInput,0))
				curInput = curInput <<1					
		else:
			for i in range(0,self.dataWidthRaw):
				# data bit 0,1,2,3
				self.matrixH.append(self.crcSerial(curInput,0))
				curInput = curInput <<1
		#self.matrixH= self.matrixH.reverse()
		#print self.matrixH
		#print self.matrixH[0]
		return self.matrixH

	def crcSerial(self,inCRC,status):
		padLength = len(self.polynomial)-1
		termCond= long('1',2)<<padLength
		outCRC = self.bin(inCRC) + ('0' * padLength)
		outCRC = long(outCRC[2:],2)
		if (status == 0):
			while 1:
				if outCRC<termCond:
					break
				else:
					outCRC = self.crcNextState(outCRC)
					#print outCRC
					outCRCstr = outCRC
					outCRC = long(outCRC,2)
			#print outCRCstr
			return outCRCstr[(len(outCRCstr)-padLength):]
		else:
			outCRCstr = self.crcNextState(outCRC)
			return outCRCstr[(len(outCRCstr)-padLength):]

	def bin(self,x):
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


	def crcNextState(self,curInput):
		#print curInput
		dataWidth = self.dataWidth
		polynomial = self.polynomial
		temp = str(self.bin(curInput))[2:].rjust(dataWidth,'0')
		firstOneIndex = temp.index('1')
		polyMask = str(self.bin(long(polynomial,2)))[2:].ljust(len(temp[firstOneIndex:]),'0')
		partInput = str(self.bin(long(temp[firstOneIndex:],2)))[2:]
		result = long(partInput,2) ^ long(polyMask,2)
		return str(self.bin(result))[2:].rjust(dataWidth,'0')

	def genVerilog(self):
		dataStr = "";
		for i in range(0,len(self.polynomial)-1):
			dcounter = 0
			dataStr = dataStr + self.iden + "crc_out["+ str(i) + "]="
			for item in self.matrixH:
				if item[len(self.polynomial)-2-i] == '1':
					dataStr = dataStr + "data_in[" + str(dcounter)  + ']^' 
				dcounter = dcounter + 1 
			dataStr = dataStr[:-1] + ";\n"

		return dataStr

	def run(self):
		self.genMat()
		return self.genVerilog()

def main(argv):
	outputfile = 'CRC.v'
	try:
		dataWidth = long(argv[0])
		polynomial = argv[1]
	except IndexError:
		print "Usage: python CRC.py <data_width> <polynomial_function>"
		sys.exit(2)
	try :
		dataWidth = long(argv[0])
	except ValueError: 
		print "Data width should be the first argument (an integer between 8 and 32)!"
		sys.exit(2)
	if(dataWidth<MIN_DATAWIDTH):
		print "Data width minimum data width is ", MIN_DATAWIDTH 
		sys.exit(2)
	elif(dataWidth>MAX_DATAWIDTH):
		print "Data width maximum data width is ", MAX_DATAWIDTH
		sys.exit(2)
	if(re.match(r"^[01]+$",polynomial)):
		if(polynomial[0] != "1"):
			print "Polynomial MSB should be 1"
			sys.exit(2)
		elif(polynomial[-1] != "1"):
			print "Polynomial LSB should be 1"
			sys.exit(2)
		if(len(polynomial)<=1):
			print "Polynomial should be larger than 1"
			sys.exit(2)
		elif(len(polynomial)>=dataWidth):
			print "Polynomial should be less than data width, which is input as, ", dataWidth
			sys.exit(2)
	else :
		print "Polynomial unrecognized data format. (i.e. 1101 -> x^3 + x^2 + 1 ) "
		sys.exit(2)
	reversePolynomial = polynomial[::-1]
	counter = 0
	wstr = ''
	for c in reversePolynomial:
		if(c=='1'):
			if(counter == 0): 
				wstr = '1+'
			elif (counter == 1):
				wstr = wstr + "x+"
			else:
				wstr = wstr + "x^" + str(counter) + "+"
		counter = counter + 1
	wstr = wstr[0:-1]
	outputBitField = "[" + str(len(polynomial)-2) + ":0]"
	inputBitField = "[" + str(dataWidth-1) + ":0]"
	idenAdd = ''
	fo = open(outputfile, "w")
	fo.write(idenAdd + "//" + ("-"*80) + "\n")
	fo.write(idenAdd + "// CRC module for data" + inputBitField + " , " + "crc" + outputBitField + "=" + wstr + ";" + "\n")
	fo.write(idenAdd + "//" + ("-"*80) + "\n")
	fo.write(idenAdd+"module crc(\n")
	idenAdd = idenAdd + 2 * " "
	fo.write(idenAdd+"input " + inputBitField + " data_in,\n")
	fo.write(idenAdd+"output " + outputBitField + " crc_out);\n\n")
	fo.write(idenAdd+"reg " + outputBitField + " crc_out;\n\n")	
	fo.write(idenAdd+"always @(*) begin\n")
	idenAdd = idenAdd + 2 * " "
	#print dataWidth
	#print polynomial
	myCRC = CRCsyn(dataWidth,polynomial,idenAdd)
	synCRCcore = myCRC.run()
	fo.write(synCRCcore + '\n')
	idenAdd = idenAdd[0:-2]
	fo.write(idenAdd+"end // always\n\n")
	idenAdd = idenAdd[0:-2]
	fo.write(idenAdd+"endmodule // crc")
	fo.close()

if __name__ == "__main__":
	main(sys.argv[1:])
