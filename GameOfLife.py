#Copyright 2012 Matthias Pall Gissurarson
#This file is part of GameOfLife.
#Licensed under the MIT X License. See LICENSE for details

#Klasi sem utfaerir GameOfLife ad stadaldri, en med notkun setBS ma utfaera alla LifeLike automata.
#Fall sem audveldar okkur prentun fylkis, notad i Main
import re
import datetime
from Cell import Cell

def printer(PCLoadLetter):
		for j in range(len(PCLoadLetter)):
				print PCLoadLetter[j]
		print ''

class GameOfLife:
	__Generations = 0	#Heldur utan um hve margar kynslodir hafa ordid til.
	width, height = 0,0 #Heldur utan um haed og breidd svaedisins sem spilad er a
	Wrap = False #Heldur utan um hvort Wrap se a eda ekki
	Born = [] #Heldur utan um regluna hver faedist
	Survives = [] #Heldur utan um regluna um hver lifir af
	__Count = dict() #Geymir hve margar frumur eru i kringum hverja frumu
	__Cell = dict() #Geymir frumurnar, thaer eru Processes, thannig ad hver fruma telur utan um sig i einu. 
	__Map = dict() #Geymir spilunar svaedid

	# Smidurinn okkar
	def __init__(self,w, h, wr, Field):		
		self.width, self.height = w, h
		self.Wrap = wr
		self.setupCells()
		self.__Generations = 0
		self.Born = [3]
		self.Survives = [2,3]
		self.__Map = dict()
		self.__Count = dict()
		if  Field:	
			self.setField(Field)
	
	#Setur patternid sem geymt er i skjalinu filename sem fieldid. Fylgir RLE kerfinu.
	def openPattern(self, filename):
		try:
			f = open(filename.rsplit('.rle')[0] + '.rle', 'r')
			skjal = f.read()
			f.close()
		except IOError:
			print filename + ' was not found'
			return

		linur = skjal.split('\n')
		popp = linur.pop(0)
		while popp.find('#') is not -1:
			popp = linur.pop(0)
		reglugrunnur = popp.split(',')
		reglur = ['','','','']
		for s in reglugrunnur:
			if s.find('x') is not -1:
				reglur[0] = s
			if s.find('y') is not -1:
				reglur [1] = s
			if s.find('rule') is not -1:
				reglur[2] = s		
			if s.find('wrap') is not -1:
				reglur[3] = s
		
		xstrengur = reglur[0].split()
		ystrengur = reglur[1].split()
		x = int(xstrengur[2])
		y = int(ystrengur[2])
		wrap = False
	
		if len(reglur[3]) is 0:
			wrap = False
		elif(int(reglur[3].split()[2]) == 1):
			wrap = True
		
		B = []
		S = []
		if len(reglur[2]) is 0:
			B = [3]
			S = [2,3]
		else:
			rulestrengur = reglur[2].split()
			BogSstrengur = rulestrengur[2].split('/')
			bstrengur = 'B3'
			sstrengur = 'S23'
			for s in BogSstrengur:
				if s.find('B') is not -1:
					bstrengur = s
				if s.find('S') is not -1:
					sstrengur = s
			for i in range(9):
				if str(i) in bstrengur:
					B.append(i)
				if str(i) in sstrengur:
					S.append(i)

		#Faum streng sem inniheldur bara skipanirnar			
	
		dead = ['b','B']
		alive = ['o']
		newrow = ['$']
		
		skipanir = ''.join(str(''.join(linur).split('!')[0].split('\n')))
		t =''
		for c in skipanir:
			if c in newrow or c in dead or c in alive or c.isdigit():
				t += c
		self.__init__(x, y,wrap,None)
		self.setBSlists(B,S)
		self.setFieldString(t)

	
	#Vistar nuverandi leiksvaedi
	def savePattern(self, filename):
		l = "#C Made by Matthias Pall Gissurarson's Cellular Automata Simulator at\n"
		l += "#O "
		l += str(datetime.datetime.now())
		l += "\n"
		wrap = 0
		if self.Wrap:
			wrap = 1
		l += "x = " 
		l += str(self.width) 
		l += ", y = "
		l += str(self.height)
		l += ", rule = S"
		for s in self.Survives:
			l += str(s)
		l += "/B"
		for s in self.Born:
			l+= str(s)
		
		l += ", wrap = "
		l += str(wrap)
		l += '\n'
		l += self.getFieldString()
		
		f = open(filename.rsplit('.rle')[0] + '.rle','w')
		f.write(l)
		f.close()

	#Tekur inn streng  sem inniheldur rod hluta a forminu <run_count><tag> thar sem <run_count> er hve oft thetta munstur endurtekur sig
	# og <tag> er annad hvort b, o eda $
	# thar sem b thydir daud fruma, o thydir lifandi fruma og $ thydir enda thessarar linu svaedisins. <run_count> ma sleppa ef thad er 1, og ekki tharf ad setja inn alla linuna, allar frumur eftir $ eru taldar daudar. Allar linur a eftir sidustu encodudu linunni eru fylltar af daudum frumum.
	#skipanir verdur ad vera a rettu formi og lysa svaedi sem passar inn i nuverandi svaedi.
	def setFieldString(self, skipanir):
		l = re.split('([bBo\\$])',skipanir)
		dead = ['b','B']
		alive = ['o']
		newrow = ['$']
		#Getur ekki endad a tolu
		l.pop()
		for i in range(len(l)):
			if l[i].isdigit():
				l[i] = int(l[i])
			if l[i] is '':
				l[i] = 1
		nums = [ 0 for i in range(len(l)/2)]
		orders = [ '' for i in range(len(l)/2)]
		for i in range(len(l)):
			if i%2 == 0:
				nums[i/2] = l[i]
			else :
				orders[i/2] = l[i]		
		Field = [[False for col in range(self.width)] for row in range(self.height)]
		i, j, s = 0,0,0
		while s < len(nums):
			for x in range(nums[s]):
				if orders[s] in dead:
					Field[i][j] = False
					j += 1
				if orders[s] in alive:
					Field[i][j] = True
					j += 1
				if orders[s] in newrow:
					j = 0
					i += 1
			s += 1
		self.setField(Field)
	
	#Skilar Streng sem mundi bua til nuverandi svaedi.
	def getFieldString(self):
		num = [1 for i in range(self.width*self.height + self.height)]
		orders =  ['' for i in range(self.width*self.height + self.height)]
		s = 0
		for i in range(self.height):
			for j in range(self.width):
				if self.hasCell(i,j):
					orders[s] = 'o'
				else:
					orders[s] ='b'
				s += 1
			orders[s] = '$'
			s += 1
		i = 1
		while i < len(orders):
			if orders[i-1] is orders[i]:
				num[i-1] += 1
				num.pop(i)
				orders.pop(i)
				continue
			i += 1
		i = 1

		while i < len(orders):
			#viljum ekki hafa otharfa b.
			if orders[i-1] is 'b' and orders[i] is '$':
				num.pop(i-1)
				orders.pop(i-1)
				i -= 1
				continue
			i += 1
	
		i = 1
		while i < len(orders):
			if orders[i-1] is orders[i]:
				num[i-1] += 1
				num.pop(i)
				orders.pop(i)
				continue
			i += 1

		#Kostum burt sidasta linebreakinu.
		num.pop()
		orders.pop()
		l = ['' for i in range(len(orders))]
		for i in range(len(l)):
			if num[i] > 1:
				l[i] = ''.join([str(num[i]), orders[i]])
			else:
				l[i] = orders[i]
		
		l = ''.join(l)
		s = ''
		#Linulengd verdur vist ad vera minni en 70 stafir.
		for c in l:
			if len(s)%68 == 0 and len(s) != 0:
				s +='\n'
			s += c
		s += '!'
		return s

	#Skilar thessum leik.
	def getGOL(self):
		return self

	#Skilar hvar frumur eru.
	def getGOLKeys(self):
		return self.__Map.viewkeys()

	#Notad til ad stilla hvort kveikt eda slokkt er a wrap
	def setWrap(self, wr):
		'''Sets whether wrap is on or off'''
		self.Wrap = wr

	#Skilar hve margar kynslodir hafa faedst.
	def getGenerations(self):
		'''Retruns generations elapsed'''
		return self.__Generations

	def resetGenerations(self):
		self.__Generations = 0
	
	#Fall sem skilar leiksvaedinu
	def getField(self):
		'''Returns the GameField'''
		Field = [[0]*self.width for i in range(self.height)]
		keys = self.getGOLKeys()
		for k in keys:
			i,j  = k
			Field[i][j] = 1
		return Field
	
	#Breytir astandi frumu i gangstaett nuverandi astand
	def changeCell(self,i,j):
		'''Changes the cell at location i,j'''
		key = (i,j)
		if key in self.__Map:
			del self.__Map[key]
		else:
			self.__Map[key] = True

	#Startar talningu fyrir frumu og frumurnar i kring.
	def countCellAndAround(self,GOL, io, jo, wr,  Ran):
		'''Starts the count for the Cell and the cells around it'''
		counter,itemp,jtemp = 0,0,0
		for i in range(3):
			itemp = io - 1 + i
			if wr:
				if itemp < 0:
					itemp = self.height-1
				elif itemp == self.height:
					itemp = 0
			for j in range(3):
				jtemp = jo -1 + j
				if wr:
					if jtemp < 0:
						jtemp = self.width - 1
					elif jtemp == self.width:
						jtemp = 0
				
					if (itemp,jtemp) in Ran:
						continue
					self.runCell(itemp,jtemp)
				else :
					
					if (itemp,jtemp) in Ran:
						continue
					if itemp >= 0 and jtemp >= 0 and  itemp < self.height and jtemp < self.width:
						self.runCell(itemp,jtemp)
				Ran[(itemp,jtemp)] = True
			
			
	#Breytir astandi frumu, en her er haegt ad akveda i hvada astand hun fer 
	def changeCellDiscrete(self,i,j,val,Field):
		if val:
			self.__Map[(i,j)]
		else:
			del self.__Map[i,j]
		
	#Keyrir talninguna fyrir frumuna i i,j
	def runCell(self,i,j):
		if (i,j) in self.__Cell:
			self.__Cell[(i,j)].run(self,i,j, self.Wrap,self.__Count,self.width, self.height)
		else:
			self.addCell(i,j)
			self.__Cell[(i,j)].run(self,i,j, self.Wrap,self.__Count,self.width, self.height)
	
	#Skilar True ef lifandi fruma er i i,j
	def hasCell(self,i,j):
		'''Returns true if the cell at i,j is alive'''
		return (i,j) in self.__Map
	
	#Fall sem spilar eina umferd leiksins
	def play(self):
		'''Plays one round of the Game of Life'''
		self.upGen()
		tempMap = dict()
		Ran = dict()
		if 0 not in self.Born:
			for key in self.__Map:
				i,j = key
				self.countCellAndAround(self,i,j, self.Wrap, Ran)
		else:	
			for i in range(self.height):
				for j in range(self.width):
					self.runCell(i,j)
		
		#Setjum upp fylkid fyrir alla reitina
		if 0 not in self.Born:
			for key in self.__Count:
				i,j = key
				if self.__Count[(i,j)] in self.Survives:
					if self.hasCell(i,j): 
						tempMap[(i,j)] = True
				else:
					self.removeCell(i,j)
				if self.__Count[(i,j)] in self.Born:
						tempMap[(i,j)] = True
						self.addCell(i,j)
		else:
			for i in range(self.height):
				for j in range(self.width):
					if (i,j) not in self.__Count:
						tempMap[(i,j)] = True
						self.addCell(i,j)
					if self.__Count[(i,j)] in self.Survives:
						if self.hasCell(i,j): 
							tempMap[(i,j)] = True
					else:
						self.removeCell(i,j)
					if self.__Count[(i,j)] in self.Born:
						tempMap[(i,j)] = True
						self.addCell(i,j)
	
		keys = self.__Cell.keys()
		for key in keys:
			if key not in Ran:
				del self.__Cell[key]
		
		self.__Map = tempMap

	#Fjarlaegir frumu i,j ur keyrslumappid
	def removeCell(self, i, j):
		if (i,j) in self.__Cell:
			del self.__Cell[(i,j)]

	#Baetir vid frumu i,j i keyrslumappid
	def addCell(self, i,j):
		if (i,j) not in self.__Cell:
			self.__Cell[(i,j)] = Cell()

	#Upphafsstillir keyrslu mappid
	def setupCells(self):
		self.__Cell = dict()

	#Haekkar fjolda kynsloda um einn
	def upGen(self):	
		self.__Generations += 1
	
	#Hreinsar nuverandi lista frumna.
	def clearCells(self):
		for i in range(self.height):
			for j in range(self.width):
				self.__Cell[(i,j)].clear()
				
	#Setur nyjar reglur
	def setBS(self,B,S):
		if((not B.isdigit() or not S.isdigit()) and not len(B) == 0 and not len(S) == 0):
				print 'Sla verdur inn tolur'
		newB = []
		newS = []
		for i in range(9):
			if str(i) in B:
				newB.append(i)
			if str(i) in S:
				newS.append(i)
		self.setBSlists(newB,newS)

	#Setur nyjar reglur
	def setBSlists(self,B,S):
		self.Born = B
		self.Survives = S
	
	#Setur nytt spilasvaedi
	def setField(self, NyttField):
		'''Sets a new GameField'''
		self.setupCells()
		for i in range(self.height):
			for j in range(self.width):
				if i < len(NyttField):
					if j < len(NyttField[i]):
						if	NyttField[i][j]:
							self.__Map[(i,j)] = True
							self.addCell(i,j)
if __name__ == "__main__":

	#Field til ad syna hvad gerist
	Field = [[True,False,False,False,False,False,True], [False,False,False,False,False,False,False], [False,False,False,True,False,False,False], [False,False,False,True,False,False,False],[False,False,False,True,False,False,False], [False,False,False,False,False,False,False], [True,False,False,False,False,False,True]]
	
	

	
	GOL = GameOfLife(7, 7,True, None)	
	GOL.setField(Field)
	GOL.savePattern('orig.rle')
	x = input('Hve morg generation viltu reikna?: ')
	i = 0
	GOL.openPattern('orig.rle')
	GOL.setWrap(True)
	print 'Generation: ' + str(i)
	printer(GOL.getField())
	while i < int(x):
		GOL.play()
		i += 1
		print 'Generation: ' + str(i)
		printer(GOL.getField())
		
