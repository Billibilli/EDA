import eulerclass

if __name__ == "__main__":
	g = {	"n1" : ["a","b"],
		"n2" : ["a","b","c","d"],
		"n3" : ["c","d"],
		"a"  : ["n1","n2"],
		"b"  : ["n1","n2"],
		"c"  : ["n3","n2"],
		"d"  : ["n3","n2"]
	    }
	graph=eulerclass.eulerGraph(g)
	graph.findEulerPath()
	print graph.printTour()
