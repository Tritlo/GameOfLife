#Copyright 2012 Matthias Pall Gissurarson
#This file is part of GameOfLife.
#Licensed under the MIT X License. See LICENSE for details

from multiprocessing import Process

class Cell(Process):
	Alive = False

	def __init__(self):
		Process.__init__(self)
		Alive = True

		
	def run(self, GOL, io, jo, wr, countlist, width,height):
		'''Counts how many neighbour the cell at io,jo has in the field Field and with or without wrap as set by wr'''
		counter,itemp,jtemp = 0,0,0
		for i in range(3):
			itemp = io - 1 + i
			if wr:
				if itemp < 0:
					itemp = height-1
				elif itemp == height:
					itemp = 0
			for j in range(3):
				jtemp = jo -1 + j
				if itemp == io and jtemp == jo:
					continue
				if wr:
					if jtemp < 0:
						jtemp = width - 1
					elif jtemp == width:
						jtemp = 0
					if GOL.hasCell(itemp,jtemp) :
						counter += 1
				else :	
					if itemp >= 0 and jtemp >= 0 and  itemp < height and jtemp < width and GOL.hasCell(itemp,jtemp):
						counter += 1
		countlist[(io,jo)] = counter
