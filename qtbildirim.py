#!/usr/bin/env python3
#-*- coding: utf-8 -*-
import time
import uuid    
import os 
import sys
from sys import argv, exit
import ayarlar as ayar
import subprocess
import pkgutil
import threading

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import pyqtSlot

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWebKit import *
from PyQt5.QtWebKitWidgets import *
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow

if pkgutil.find_loader("gsocketpool") is None:
	os.system("pip3 install gsocketpool")
	
import gsocketpool.pool

if pkgutil.find_loader("mprpc") is None:
	os.system("pip3 install mprpc")

from mprpc import RPCPoolClient

#from gi.repository import Notify
#Notify.init("App Name")
#Notify.Notification.new("Hi").show()
kimlik=str(uuid.UUID(int=uuid.getnode()))
kimlik=kimlik.split("-")[4]
kimlik=ayar.kimlik+"#"+kimlik

MESAJ_DIZINI="./mesajlar/"
BILDIRIM_SURE=10000

os.makedirs(MESAJ_DIZINI, exist_ok=True)

from PyQt5.QtWidgets import QSystemTrayIcon, QApplication

class SystemTray(QSystemTrayIcon):
	def __init__(self, parent):
		super().__init__()
		self.parent = parent
		self.setVisible(True)
		self.setIcon(QIcon("./icon.png"))

		self.updateToolTip()

		self.activated.connect(self.parentShow)
		self.messageClicked.connect(self.parentShow)

	def updateToolTip(self):
		#db = ReaderDb()
		#db.execute("select * from store where iscache=1")
		#unread = db.cursor.fetchall()
		#db.execute("select * from store where isstore=1")
		#store = db.cursor.fetchall()
		#db.execute("select * from store where istrash=1")
		#trash = db.cursor.fetchall()
		unread="--"
		store="--"
		trash="--"
		self.setToolTip(self.tr('''<span style='font-size:14pt'>{} - {}</span>
		<br><span style='font-size:10pt'>Unread: {}</span>
		<br><span style='font-size:10pt'>Stored: {}</span>
		<br><span style='font-size:10pt'>Deleted: {}</span>''').format(QApplication.applicationName(),
		QApplication.applicationVersion(), len(unread), len(store), len(trash)))

	def parentShow(self):
		self.parent.show()


class bildirim(QMainWindow):
	def __init__(self):
		super().__init__()
		self.init_ui()
		self.systemTray = SystemTray(self)
		
	def init_ui(self):
		main_layout = QWidget()
		grid = QGridLayout()
		main_layout.setLayout(grid)
		
		self.setCentralWidget(main_layout)
		self.setWindowTitle('Milis Linux Bildirim Sistemi')
		self.statusBar().showMessage('hazır')
		self.setWindowIcon(QIcon('./img/icon.png'))
		self.setGeometry(100, 100, 640, 240)
		self.createTable()
		
		grid.addWidget(self.tableWidget) 
		thread = threading.Thread(target=self.dinle)
		thread.start()
		print("0")
		
		self.show()
        
	def createTable(self):
	# Create table
		self.tableWidget = QTableWidget()
		self.tableWidget.setRowCount(30)
		self.tableWidget.setColumnCount(3)
		liste=[]
		satirno=0
		for mesajd in os.listdir(MESAJ_DIZINI):
			print(mesajd)
			icerik=open(MESAJ_DIZINI+mesajd,"r").read()
			satirlar=icerik.split("\n")
			satir=satirlar[0]
			print(satir)
			gmsj=satirlar[1]
			kaynak=satir.split("@")[0]
			zaman=satir.split("@")[1]
			self.tableWidget.setItem(satirno,0, QTableWidgetItem(kaynak))
			self.tableWidget.setItem(satirno,1, QTableWidgetItem(zaman))
			self.tableWidget.setItem(satirno,2, QTableWidgetItem(gmsj))
			satirno+=1
		self.tableWidget.move(0,0)

		# table selection change
		self.tableWidget.doubleClicked.connect(self.on_click)
		
		
	def ilet(self,baslik,message,sure=3000):
		
		subprocess.Popen(['notify-send',"--expire-time="+str(sure),baslik, message])
		return

	

	def mliste_al(self):
		liste=[]
		for mesajd in os.listdir(MESAJ_DIZINI):
			dosya=os.path.basename(mesajd)
			liste.append(dosya)
		return liste


	def dinle(self):
		client_pool = gsocketpool.pool.Pool(RPCPoolClient, dict(host=ayar.sunucu, port=ayar.port))
		while True: 
			time.sleep(2) 
			#print ("sunucu bağlanıyor...")
			try:
				#print ("sunucu bağlanıyor2...")
				with client_pool.connection() as client:
					print ("sunucu bağlanıyor...")
					#canlılık kaydı gönder
					mesaj=client.call('nabiz_at',kimlik)
					mesaj=str(mesaj)
					print(mesaj)
					ymliste=client.call('mesaj_al',kimlik,mliste_al())
					if ymliste:
						for ym in ymliste:
							 open(MESAJ_DIZINI+ym[0],"w").write(ym[1])
							 ilet("ileti",ym[1],BILDIRIM_SURE)
					print ("ymliste >>> ",ymliste)
					#ilet("ileti",mesaj)
					print ("sunucu bağlandı...")
			except:
				print("bağlantıda sorun var",ayar.sunucu,ayar.port)
		
		
		
	@pyqtSlot()
	def on_click(self):
		print("\n")
		for currentQTableWidgetItem in self.tableWidget.selectedItems():
			print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())


	

if "__main__" == __name__:
	app = QApplication(argv)
	print("1")
	ex = bildirim()
	print("2")
	exit(app.exec_())
