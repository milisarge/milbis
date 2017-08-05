#!/usr/bin/env python3

import os    
import uuid    
import sys 
import hashlib
from time import gmtime, strftime
import pkgutil
import ayarlar as ayar

if pkgutil.find_loader("gsocketpool") is None:
	os.system("pip3 install gsocketpool")
	
import gsocketpool.pool

if pkgutil.find_loader("mprpc") is None:
	os.system("pip3 install mprpc")

from mprpc import RPCPoolClient

baskimlik="milistgn"
SIFRE="Sqe4F5GSDax*-5"

#from gi.repository import Notify
#Notify.init("App Name")
#Notify.Notification.new("Hi").show()
kimlik=str(uuid.UUID(int=uuid.getnode()))
kimlik=kimlik.split("-")[4]
kimlik=baskimlik+"#"+kimlik

dizin="./smesajlar/"

def yeni(kimlik,icerik,mod):
	if mod=="rpc":
		client_pool = gsocketpool.pool.Pool(RPCPoolClient, dict(host=ayar.sunucu, port=ayar.port))
		with client_pool.connection() as client:
			mesaj=client.call('mesaj_gonder',kimlik,icerik,SIFRE)
			mesaj=str(mesaj)
	else:
		icerikpak=kimlik+"@"+strftime("%Y-%m-%d %H:%M:%S", gmtime())+"\n"+icerik
		dosya_adi=hashlib.md5(icerikpak.encode("utf")).hexdigest()
		open(dizin+dosya_adi,"w").write(icerikpak)
		return [dosya_adi,icerikpak]



if sys.argv[1]:
	icerik=sys.argv[1]
	mod="yerel"
	if "rpc:" in icerik:
		mod="rpc"
		icerik=icerik.split("rpc:")[1]
	yeni(kimlik,icerik,mod)
