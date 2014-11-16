class eulerGraph(object):

	def __init__(self, eulerGraphInput={}):
		self.__eulerGraphDic = eulerGraphInput

	def findEulerPath(self):
		self.eulerTempPath=[]
		self.eulerFinalPath=[]
		self.eulerEdges=self.__getEdges()
		self.starter=self.__eulerGraphDic.keys()[0]
		self.eulerFinalPath.append(self.starter)
		for vertex in self.__eulerGraphDic:
			if len(vertex)!= 0:
				return self.__findOneEulerPath(self.starter)

	def __findOneEulerPath(self,root):
		self.eulerTempPath.append(root)
		for neighbour in self.__eulerGraphDic[root]:
			self.__shouldIGoThisEdge(root,neighbour)
		
	def __shouldIGoThisEdge(self,root,neighbour):
        	if {root,neighbour} not in self.eulerEdges:  			      #This neighbour has already been reached, try another one
			return -1
		else: 
                	self.eulerEdges.pop(self.eulerEdges.index({root,neighbour}))  # Mark down that I reached this neighbour 
                        if(neighbour==self.eulerFinalPath[0]):		      	      # If back to the start point 
                                if self.eulerEdges.__len__()!=0:                      # and find out didn't travel all nodes 
                                        for i in reversed(self.eulerTempPath):        # back to the point where it still have neighbours 
                                                for k in self.eulerEdges:             # Which means back to the closest element in the path
                                                        if i in k:                    # that should be appear in the remaining edge
                                              			self.eulerFinalPath=self.eulerTempPath[self.eulerTempPath.index(i):]+self.eulerFinalPath
                                                                self.eulerTempPath=self.eulerTempPath[0:self.eulerTempPath.index(i)]
                                                                return self.__findOneEulerPath(i)
                                else:
                                        self.eulerFinalPath=self.eulerTempPath+self.eulerFinalPath
                                        return self.eulerFinalPath
                        else:
                                self.__findOneEulerPath(neighbour)
	def __getEdges(self):
		edges = []
		for vertex in self.__eulerGraphDic:
			for neighbour in self.__eulerGraphDic[vertex]:
				if {neighbour, vertex} not in edges:
					edges.append({vertex, neighbour})
		return edges 

	def printTour(self):
		res = ""
		for i in self.eulerFinalPath:
			res += str(i) + "->" " "
			
		res = res[0:-3] 
		return res
