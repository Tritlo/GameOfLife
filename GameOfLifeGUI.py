#Copyright 2012, Matthias Pall Gissurason
#This file is part of GameOfLife.
#
#    GameOfLife is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    GameOfLife is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with GameOfLife.  If not, see <http://www.gnu.org/licenses/>.

#Matthias Pall Gissurarson	mpg3@hi.is	Elvar Helgason	12. mars 2012
#GTK interface Fyrir GameOfLife leikinn. GameOfLife er utfaerdur i GameOfLife.py i somu moppu
import pygtk
pygtk.require("2.0")
import gtk.glade
import warnings
import re
import time
import gobject
from multiprocessing import Process
from threading import Condition,Thread
from GameOfLife import GameOfLife	

class GameOfLifeGUI:
	'''This is a class which creates a GUI for the GameOfLife. It should be created with GameOfLifeGUI(GOL) where GOL is a GameOfLife,
	and then run with 
	
	while(GUI.Running):
		gtk.main_iteration(True)
		if gtk.events_pending():
			continue
		if(GUI.Play):
			GUI.tick()
			time.sleep(1/float(GUI.PlaySpeed*5))
	'''
	MaxWidth = 500
	MaxHeight = 300
	condition = Condition()
	FieldIsNew = False
	__Pollrate = 200
	__Born = []
	__Survives = []
	__pixmap = None
	__GOL = None
	__gladeskjal = 'GameOfLifeGUI.glade'	
	Play = False
	__Width, __Height = 7,7
	__Wrap = False
	__DrawX, __DrawY, __DrawH, __DrawW = 0,0,0,0
	PlaySpeed = 2.5 
	Running = True
	__Grid = True
	__gcGrid = None
	__gcCells = None
	__gcBackground = None
	__Color = None #Litur frumnanna
	__GridColor = None #Litur nets
	__BackgroundColor = None #Litur bakgrunns
	filename = None #Nafn skjals

	#Kallad a thegar glugganum er lokad. Hofum gtk.main_quit() ef klasinn skyldi vera keyrdur med gtk.main()
	def on_window_destroy (self, widget, data = None):
		self.Running = False
		try:
			gtk.main_quit()
		except RuntimeError:
			pass

		return True
	
	#Kallad a thegar hradanum er breytt, og uppfyllir skilyrdid um ad hrada a hermun
	def Speed_ValueChange(self,widget,data = None):
		self.PlaySpeed = self.Speed.get_value()


	#Kveikir og slekkur a Wrappinu, thad er ad allir endarnir eru tengdir vid byrjun sina
	#Kallad a thegar ytt er a wrap takkann
	def Wrap_toggled(self, widget, data = None):
		self.__Wrap = not self.__Wrap
		self.__GOL.setWrap(self.__Wrap)
		self.updateStrings()
		return True
	
	#Kveikir og slekkur a linum
	def Grid_Toggle(self, widget, data = None):
		self.__Grid = not self.__Grid
		self.drawField(self.Teiknibord)
		return True

	#Kallad a til ad fa nuverandi hrada.
	def getSpeed(self):
		return self.PlaySpeed
	
	#Tokum inn stadsetningu og breytum thar hvort fruman se lifandi eda daud.
	#Uppfyllir skilyrdid um ad teikna frumur
	def changeCell(self,xin,yin):
		jin = xin/float(self.__DrawW) * self.__Width
		iin = yin/float(self.__DrawH) * self.__Height
		self.__GOL.changeCell(int(iin),int(jin))
		return True
		
	#Fall til ad teikna myndina af frumunum
	def drawField(self,widget):
		if not self.__gcGrid:
			self.__gcGrid = widget.window.new_gc()
		self.__gcGrid.set_rgb_fg_color(gtk.gdk.color_parse(self.__GridColor))
		
		if not self.__gcCells:
			self.__gcCells = widget.window.new_gc()
		self.__gcCells.set_rgb_fg_color(gtk.gdk.color_parse(self.__Color))
	
		if not self.__gcBackground:
			self.__gcBackground = widget.window.new_gc()
		self.__gcBackground.set_rgb_fg_color(gtk.gdk.color_parse(self.__BackgroundColor))

		
		width = self.__DrawW/float(self.__Width)	
		height = self.__DrawH/float(self.__Height)
		self.__pixmap.draw_rectangle(self.__gcBackground,True,0,0,self.__DrawW, self.__DrawH)		
		
		Keys = self.__GOL.getGOLKeys()
		for key in Keys:
			i,j = key
			self.__pixmap.draw_rectangle(self.__gcCells, True,int(j*width),int(i*height),int(width),int(height))
			
		for i in range(self.__Height):
			if self.__Grid:
				self.__pixmap.draw_line(self.__gcGrid,0,int(i*height),self.__DrawW,int(i*height))

		for j in range(self.__Width):
			if self.__Grid:
				self.__pixmap.draw_line(self.__gcGrid,int(j*width),0,int(j*width),self.__DrawH)
		
		self.Teiknibord.queue_draw_area(self.__DrawX, self.__DrawY, self.__DrawW, self.__DrawH)
	
	#Finnum ut hvar var ytt a myndina og uppfaerum tha frumu
	#Kallad a thegar ytt er a takka a myndinni
	def mouseButtonPressed(self, widget, event):		
		self.changeCell( int(event.x), int(event.y))
		self.drawField(widget)
		return True

	#Keyrt thegar ramma er breytt og i fyrsta skipti til ad upphafsstilla breytur. Configure_event signals vidbrogd
	def fieldChanged(self, widget, event):
		#Upphafsstillum
		self.__DrawX, self.__DrawY,self.__DrawW,self.__DrawH = widget.get_allocation()
	
		self.__pixmap = gtk.gdk.Pixmap(widget.window, self.__DrawW, self.__DrawH)
		self.__pixmap.draw_rectangle(widget.get_style().white_gc,True,0,0,self.__DrawW, self.__DrawH)
		
		widget.queue_draw_area(self.__DrawX,self.__DrawY,self.__DrawW,self.__DrawH)		
		
		self.drawField(self.Teiknibord)
		return True
	
	#Spilum eina umferd af Game of Life.
	#Uppfyllir skilyrdid um ad herma eftir.
	def tick(self):
		self.__GOL.play()
		self.Gens.set_text(str(self.__GOL.getGenerations()))
		self.drawField(self.Teiknibord)
	
	# Expose_event signals vidbrogd	sem teiknar rammann i upphafi
	def reDraw(self, widget, event):
		x,y,width,height = event.area
	
		self.__DrawX, self.__DrawY,self.__DrawW,self.__DrawH = event.area
		widget.window.draw_drawable(widget.get_style().fg_gc[gtk.STATE_NORMAL],self.__pixmap, x,y,x,y,width,height)
		return False

	#Breytum fylkinu, svaedinu og reglunum okkar. Keyrt thegar ytt er a set takkann. 
	#Uppfyllir skilyrdunum um ad geta breytt reglum leiksvaedis, og einnig staerd thess.
	def Set_Clicked(self, widget, data = None):
		a = self.WidthText.get_text()
		b = self.HeightText.get_text()
		changed = False
		#Max = 1000000 #Hann raedur vid thad, en thad sest ekki i individual frumur.
		Max = 500
		if not (re.match('\\d+',a) and re.match('\\d+',b)) :
			print 'Sla verdur inn tolur'
			return
		if(self.__Width != int(a)):
			if int(a) in range(1,self.MaxWidth):
				self.__Width = int(a)
				changed = True
			elif int(a) >= self.MaxWidth:
				self.__Width = self.MaxWidth;
				changed = True
		if(self.__Height != int(b)):
			if int(b) in range(1,self.MaxHeight):
				self.__Height = int(b)
				changed = True
			elif int(b) >= self.MaxHeight:
				self.__Height = self.MaxHeight;
				changed = True
		if(changed):
			self.__GOL = GameOfLife(self.__Width,self.__Height,self.__Wrap,None)
		self.__GOL.setBS(self.BornText.get_text(),self.SurvivesText.get_text())
		self.__Born, self.__Survives = self.__GOL.Born, self.__GOL.Survives
		self.updateStrings()
		self.drawField(self.Teiknibord)
		return True
	
	#Keyrt thegar ytt er a clear takkann. Hreinsar svaedid.
	def Clear_Clicked(self, widget, data = None):
		self.__GOL = GameOfLife(self.__Width,self.__Height,self.__Wrap,None)
		self.__GOL.resetGenerations()
		self.updateStrings()
		self.drawField(self.Teiknibord)
		return True

	#Lokar Open glugganum.
	def Cancel_Open_Clicked(self,widget,data = None):
		self.OpenDial.hide()
		return True

	#Opnar nytt skjal
	def Open_Clicked(self, widget, data = None):
		self.filename =  self.OpenDial.get_filename()
		if self.filename:
			self.__GOL.openPattern(self.filename)
	
		self.__Born, self.__Survives = self.__GOL.Born, self.__GOL.Survives
		self.__Width, self.__Height = self.__GOL.width, self.__GOL.height
		self.__Wrap = self.__GOL.Wrap
		
		self.__GOL.resetGenerations()
		self.updateStrings()
		
		self.drawField(self.Teiknibord)
		self.OpenDial.hide()
		return True

	#Opnar Open gluggann
	def Open_Menu_Clicked(self, widget, data = None):
		self.OpenDial.show_all()
		return True

	#Save-ar fra menuinum
	def Save_Menu_Clicked(self, widget, data = None):
		self.__GOL.savePattern(self.filename)
		return True

	#Opnar save gluggann
	def Save_As_Menu_Clicked(self, widget, data = None):
		self.SaveDial.show_all()
		self.SaveDial.set_current_name(self.filename.split('.rle')[0] + ' - Copy')
		return True

	#Lokar Save glugganum
	def Cancel_Save_Clicked(self, widget, data = None):
		self.SaveDial.hide()
		return True

	#Save-ar skjalid
	def Save_Clicked(self, widget, data = None):
		filename = self.SaveDial.get_filename()
		filename = filename.rsplit('.rle')[0] + '.rle'
		if filename:
			self.__GOL.savePattern(filename)
			self.filename = filename
		self.updateStrings()
		self.SaveDial.hide()
		return True

	#Lokar about glugganum
	def Close_About(self, widget, data =None):
		self.About.hide()
		return True

	#Opnar about gluggann
	def About_Clicked(self, widget, data = None):
		self.About.show_all()
		return True

	#Til ad opna velja lit glugga.
	def Change_Cell_Color_Menu_Clicked(self, widget, data = None):
		self.Cell_Color.show_all()
		self.Cell_Color_Sel.set_current_color(gtk.gdk.Color(self.__Color))
		return True

	#Til thess ad velja lit a frumum
	def Cell_Color_Choose(self, widget, data = None):
		self.__Color = self.Cell_Color_Sel.get_current_color().to_string()
		self.Cell_Color.hide()
		self.drawField(self.Teiknibord)
		return True

	#Til ad loka velja lit glugga
	def Cell_Color_Close(self, widget, data = None):
		self.Cell_Color.hide()
		return True

	#Til opna velja lit glugga.
	def Change_Background_Color_Menu_Clicked(self, widget, data = None):
		self.Background_Color.show_all()
		self.Background_Color_Sel.set_current_color(gtk.gdk.Color(self.__BackgroundColor))
		return True

	#Til ad velja lit a bakgrunni
	def Background_Color_Choose(self, widget, data = None):
		self.__BackgroundColor = self.Background_Color_Sel.get_current_color().to_string()
		self.Background_Color.hide()
		self.drawField(self.Teiknibord)
		return True

	#Til ad loka velja lit glugga
	def Background_Color_Close(self, widget, data = None):
		self.Background_Color.hide()
		return True

	#Til opna velja lit glugga.
	def Change_Grid_Color_Menu_Clicked(self, widget, data = None):
		self.Grid_Color.show_all()
		self.Grid_Color_Sel.set_current_color(gtk.gdk.Color(self.__GridColor))
		return True
	
	#Til ad velja lit a linum
	def Grid_Color_Choose(self, widget, data = None):
		self.__GridColor = self.Grid_Color_Sel.get_current_color().to_string()
		self.Grid_Color.hide()
		self.drawField(self.Teiknibord)
		return True

	#Til ad loka velja lit glugga
	def Grid_Color_Close(self, widget, data = None):
		self.Grid_Color.hide()
		return True
	
		
	#Keyrt thegar ytt er a Play/Stop takkann. Breytir thvi hvort verid er ad spila leikinn eda ekki. Viljum breyta fieldinu i byrjun til ad fordast hikst.
	def Play_toggled(self, widget, data = None):
		self.Play = not self.Play
		if(self.Play):
			self.PlayButton.set_label('Stop')
		else:
			self.PlayButton.set_label('Play')
					
		self.fieldChanged(self.Teiknibord,'configure_event')
		return True

	#Getum breytt hamarks og lagmarks hrada, og hamark haed og breidd.
	def SetMinSpeed_Clicked(self, widget, data = None):	
		p = float(self.MinSpeedBox.get_text())		
		if p > 0:		
			self.Speed.set_lower(p)
		else:
			self.Speed.set_lower(0.1)
			self.MinSpeedBox.set_text('0.1')
		if self.Speed.get_value() < p:
			self.Speed.set_value(p)

	def SetMaxHeight_Clicked(self, widget, data = None):	
		p = int(self.MaxHeightBox.get_text())		
		if p > 0:		
			self.MaxHeight = p
		else:
			self.MaxHeight = 1
			self.MaxHeightBox.set_text(str(1))

		if self.__Height > self.MaxHeight:
			self.HeightText.set_text(str(self.MaxWidth))
			self.Set_Clicked(widget, data = None)
	
	def SetMaxWidth_Clicked(self, widget, data = None):	
		p = int(self.MaxWidthBox.get_text())		
		if p > 0:		
			self.MaxWidth = p
		else:
			self.MaxWidth = 1
			self.MaxWidthBox.set_text(str(1))

		if self.__Width > self.MaxWidth:
			self.WidthText.set_text(str(self.MaxWidth))
			self.Set_Clicked(widget, data = None)

	def SetMaxSpeed_Clicked(self, widget, data = None):	
		p = float(self.MaxSpeedBox.get_text())		
		if p > 0:		
			self.Speed.set_upper(p)
		else:
			self.Speed.set_upper(50)
			self.MaxSpeedBox.set_text('50')

		if self.Speed.get_value() > p:
			self.Speed.set_value(p)

	#Til ad breyta hve oft er tjekkad a vidmoti 
	def getPollrate(self):
		return self.__Pollrate
	
	def updatePollrate(self, widget, data = None):	
		p = int(self.Pollbox.get_text())		
		if p > 0:		
			self.__Pollrate = p
		else:
			self.__Pollrate = 1
			self.Pollbox.set_text('1')
	
	#Valmoguleikar
	def closeSettings(self, widget, data = None):
		self.Settings.hide()	
		return True
	
	def Settings_Menu(self, widget, data = None):
		self.Settings.show_all()
		self.Pollbox.set_text(str(self.__Pollrate))
		self.MinSpeedBox.set_text(str(self.Speed.get_lower()))
 		self.MaxSpeedBox.set_text(str(self.Speed.get_upper()))
		self.MaxHeightBox.set_text(str(self.MaxHeight))
 		self.MaxWidthBox.set_text(str(self.MaxWidth))

	#Notum til ad geta keyrt forritid
	class Simulator(Process):
		def run(self,GUI):
			if gtk.gdk.event_peek() is gtk.gdk.MOTION_NOTIFY  or not gtk.gdk.events_pending():
				GUI.condition.acquire()
				GUI.Simulate()
				GUI.FieldIsNew = True
				GUI.condition.release()
	def Simulate(self):
		self.__GOL.play()
	
	class Waiter(Process):
		def run(self,GUI):
			GUI.condition.acquire()
			speed = GUI.getSpeed()
			pollrate = GUI.getPollrate()
			for i in range(pollrate):
				if  gtk.gdk.event_peek() is not gtk.gdk.MOTION_NOTIFY:
					if gtk.events_pending():
						GUI.condition.release()
						while gtk.events_pending():
							gtk.main_iteration(False)
						GUI.condition.acquire()
						speed = GUI.getSpeed()
				time.sleep((1/float(speed*pollrate*5)))
				i += 1
			if  not gtk.events_pending() or gtk.gdk.event_peek() is None :
				GUI.condition.release()

	#Uppfaerir mynd og generations eftir ad umferd hefur verid spilur
	class Updater(Process):
		def run(self, GUI):
			if GUI.FieldIsNew:
				GUI.condition.acquire()
				GUI.updateAfterPlay()
				GUI.condition.release()
	
	def updateAfterPlay(self):
			self.Gens.set_text(str(self.__GOL.getGenerations()))
			self.drawField(self.Teiknibord)
			self.FieldIsNew = False
	
	#Viljum ad thad standi rett i kossunum svo folk geti vitad hve stadan er nuna.
	def updateStrings(self):
		self.WidthText.set_text(str(self.__Width))
		self.HeightText.set_text(str(self.__Height))
		self.Gens.set_text(str(self.__GOL.getGenerations()))
		BornString = ''
		for t in self.__Born:
			BornString  += str(t)
		SurvivesString = ''
		for t in self.__Survives:
			SurvivesString += str(t)
		if(self.__Wrap):
			self.WrapLabel.set_text('On')
		else: 
			self.WrapLabel.set_text('Off')
		self.BornText.set_text(BornString)
		self.SurvivesText.set_text(SurvivesString)
		string = "Game of Life - " + self.filename
		self.Window.set_title(string)	

	# Smidurinn okkar
	def __init__(self,GameOfL):		
		global GOL
		self.__GOL = GameOfL
		self.__Width, self.__Height, self.__Wrap, self.__Born, self.__Survives = self.__GOL.width, self.__GOL.height, self.__GOL.Wrap, self.__GOL.Born, self.__GOL.Survives
	
		#Setjum glade skjalid
		self.builder = gtk.Builder()
		self.gladefile = self.__gladeskjal
		with warnings.catch_warnings():
			warnings.simplefilter("ignore")
			self.builder.add_from_file(self.gladefile)


		#Skilgreinum hlutina okkar sem vid notum i follunum
		self.Window = self.builder.get_object("Gluggi")	
		self.Teiknibord = self.builder.get_object("Teiknibord")		
		self.WidthText = self.builder.get_object('WidthT')
		self.HeightText = self.builder.get_object('HeightT')
		self.PlayButton = self.builder.get_object('Play')
		self.WrapLabel = self.builder.get_object('WrapL')
		self.Gens = self.builder.get_object('Generations')	
		self.BornText = self.builder.get_object('Born')
		self.SurvivesText = self.builder.get_object('Survives')
		
		self.OpenDial = self.builder.get_object('OpenPattern')
		self.About = self.builder.get_object('About')
		self.SaveDial = self.builder.get_object('SavePattern')
		self.Cell_Color = self.builder.get_object('CellColor')
		self.Cell_Color_Sel = self.builder.get_object('CellColorSel')	
		self.Background_Color = self.builder.get_object('BackgroundColor')
		self.Background_Color_Sel = self.builder.get_object('BackgroundColorSel')
		self.Grid_Color = self.builder.get_object('GridColor')
		self.Grid_Color_Sel = self.builder.get_object('GridColorSel')
		self.Pollbox = self.builder.get_object('Pollrater')			
		self.Settings = self.builder.get_object('Settings')		
		self.__Pollrate = 200
		self.MinSpeedBox = self.builder.get_object('MinSpeedBox')		
		self.MaxSpeedBox = self.builder.get_object('MaxSpeedBox')		
		self.MaxHeightBox = self.builder.get_object('MaxHeightBox')		
		self.MaxWidthBox = self.builder.get_object('MaxWidthBox')		
		
		self.__Color = '#00FF00' #Litur frumunnar
		self.__GridColor = '#2F2F2F' #Litur Gridsins
		self.__BackgroundColor = '#000000'#Litur bakgrunnsins
		if(self.__Wrap):
			self.WrapLabel.set_text('On')
		else: 
			self.WrapLabel.set_text('Off')

		self.Speed = self.builder.get_object('Speed')
		self.condition = Condition()
		self.Teiknibord.show()
		self.__Grid = True
		self.filename = "Default.rle"
		self.Window.set_title("Game of Life")	
		gtk.Widget.show_all(self.Window)
		self.updateStrings()
		#og ad hafa keyrt allavegana eitt configure_event
		self.fieldChanged(self.Teiknibord,'configure_event')	
	
		self.builder.connect_signals(self)
		

if __name__ == "__main__":
	

	
	GOL = GameOfLife(50, 30,False, None)
	##ToffMunstur til ad byrja med
	GOL.openPattern('Default.rle')
	GUI = GameOfLifeGUI(GOL)	
	p, g = None, None
	
	#Thad er ekki haegt ad hafa thetta i thradum/processum, thvi badir thurfa ad keyra gtk.main_iteration til ad nota vidmotid/teikna
	g = Process(target = gtk.main_iteration, args = (False,))
	w = GUI.Waiter()
	s = GUI.Simulator()
	u = GUI.Updater()
	gtk.gdk.threads_init()
	gtk.gdk.threads_enter()
	while(GUI.Running):
		while gtk.events_pending(): 
			g.run()
		if(GUI.Play):
			if not w.is_alive():
				w.run(GUI)
			if not s.is_alive():
				s.run(GUI)
			if not u.is_alive():
				u.run(GUI)
		
	gtk.gdk.threads_leave()
