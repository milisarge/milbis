#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import pkgutil

if pkgutil.find_loader("gsocketpool") is None:
	os.system("pip3 install gsocketpool")
	
import gsocketpool.pool

if pkgutil.find_loader("mprpc") is None:
	os.system("pip3 install mprpc")
	
if pkgutil.find_loader("gevent") is None:
	os.system("pip3 install gevent")

from gevent.server import StreamServer
from mprpc import RPCServer
from time import gmtime, strftime
from sqlite3 import *
import hashlib
import os
import sys

SIFRE="Sqe4F5GSDax*-5"
VT_ADI="./sunucu.db"
MESAJ_DIZINI="./smesajlar/"

os.makedirs(MESAJ_DIZINI, exist_ok=True)

def fliste_icerik(fliste):
	icerik=[]
	for dos in fliste:
		veri=[]
		if os.path.exists(MESAJ_DIZINI+dos):
			veri.append(dos)
			veri.append(open(MESAJ_DIZINI+dos).read())
			icerik.append(veri)
	return icerik
def gliste_al(mliste):
	sliste=[]
	fliste=[]
	for mesajd in os.listdir(MESAJ_DIZINI):
		dosya=os.path.basename(mesajd)
		sliste.append(dosya)
	
	fliste=tuple(set(mliste) ^ set(sliste))
	#print ("mesaj fark listesi >>> ",fliste)
	return fliste_icerik(fliste)

def yeni_mesaj(kimlik,icerik):
    icerikpak=kimlik+"@"+strftime("%Y-%m-%d %H:%M:%S", gmtime())+"\n"+icerik
    dosya_adi=hashlib.md5(icerikpak.encode("utf")).hexdigest()
    open(MESAJ_DIZINI+dosya_adi,"w").write(icerikpak)
    return [dosya_adi,icerikpak]
	
class Vt():
	
	connection = connect(VT_ADI)
		
	def tablo_kontrol(self,tablo):
		sql="SELECT name FROM sqlite_master WHERE type='table' AND name='"+tablo+"';"
		sonuc=self.connection.execute(sql)
		for row in sonuc:
			return row
	def tablo_olustur(self,ad):
		if ad=="istemciler":
			self.connection.execute("CREATE TABLE istemciler (id text primary key,sonaktif text,durum int)")
			sonuc="tm"
		else:
			sonuc="olumsuz"
		return sonuc
	def tablo_veri_al(self,ad):
		veri=[]
		sonuc=self.connection.execute('SELECT * FROM '+ad)
		for row in sonuc:
			return row
	def istemci_kontrol(self,kimlik):
		sql="SELECT * FROM istemciler where id='"+kimlik+"'"
		sonuc=self.connection.execute(sql)
		if sonuc:
			for row in sonuc:
				return row	
			return None
		
	def istemciler(self):
		sonuc=self.connection.execute('SELECT * FROM istemciler')
		for row in sonuc:
			return row		
	def tablo_veri_ekle(self,ad,veri):
		if ad=="istemciler":
			self.connection.execute("INSERT INTO "+ad+" (id,sonaktif,durum) VALUES (?,?,?)",veri)
			self.connection.commit()
		return "tm"
	def istemci_ekle(self,veri,mod):
		tad="istemciler"
		sql=""
		if mod=="y":
			sql="INSERT INTO "+tad+" (id,sonaktif,durum) VALUES (?,?,?)"
			yeni_mesaj("sunucu",veri[0]+" kullanıcısı eklendi.")
		else:
			sql="UPDATE "+tad+" SET id = ? , sonaktif = ? , durum = ? WHERE id = ? "
			veri.append(veri[0])
		#print("istemci > ",veri)
		self.connection.execute(sql,veri)
		self.connection.commit()
		return "tm"
		

class MilisBildirimSunucu(RPCServer):
	
	cliste=[]
	global vt
	vt=Vt()
	
	def calistir(self):
		return "yapimda"
	
	def tablo_olustur(self,sifre,vt_adi):
		if sifre==SIFRE: 
			vt.tablo_olustur(ad)
	
	def sum(self, x, y):
		return x + y
	
	def nabiz_at(self,kimlik):
		kimlik=str(kimlik)
		#kimlik kaydet
		zaman=strftime("%Y-%m-%d %H:%M:%S", gmtime())
		veri=[kimlik,zaman,1]
		mod=""
		if vt.istemci_kontrol(kimlik):
			mod="g"
		else:
			mod="y"
		snc=vt.istemci_ekle(veri,mod)
		print (kimlik,mod)
		#aktivlerin liste gönder
		if snc=="tm":
			return "sunucu bağlandı"
		else:
			return "hata"
			
	def mesaj_al(self,kimlik,mliste):
		#print (kimlik,">>>",mliste)
		ymliste=gliste_al(mliste) 
		return ymliste	
		
	def mesaj_gonder(self,kimlik,icerik,sifre):
		if sifre==SIFRE: 
			print (kimlik,">>> mesaj gönderdi.")
			snc=yeni_mesaj(kimlik,icerik)
			return snc	
		else:
			return "yanlış şifre!"
			
	def sor(self,param1):
		if param1=="zaman":
			return strftime("%Y-%m-%d %H:%M:%S", gmtime())

vtilk=Vt()

if vtilk.tablo_kontrol("istemciler") is None:
	print("veritabanı ilklemesi yapılacak.")
	snc=vtilk.tablo_olustur("istemciler")
	if snc=="olumsuz":
		print("Veritabanı oluşturmada sorun oluştu!")
		sys.exit(0)
	else:
		print("veritabanı ilklemesi yapıldı.")

    
server = StreamServer(('0.0.0.0', 8003), MilisBildirimSunucu())
server.serve_forever()
