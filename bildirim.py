#!/usr/bin/env python3
#-*- coding: utf-8 -*-
import time
import uuid    
import os 
import sys
import ayarlar as ayar
import subprocess
import pkgutil

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

def ilet(baslik,message,sure=3000):
    
    subprocess.Popen(['notify-send',"--expire-time="+str(sure),baslik, message])
    return

client_pool = gsocketpool.pool.Pool(RPCPoolClient, dict(host=ayar.sunucu, port=ayar.port))

def mliste_al():
	liste=[]
	for mesajd in os.listdir(MESAJ_DIZINI):
		dosya=os.path.basename(mesajd)
		liste.append(dosya)
	return liste
while True: 
	time.sleep(2) 
	try:
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
