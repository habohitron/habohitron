#!/usr/bin/env python

import sys
import argparse
import sqlite3
import io
from hitroncontrol import *
	
class HitronCryptDB:
	def __init__(self, database):
		self.db = database
	def __enter__(self):
		self.con = sqlite3.connect(self.db)
		return self
	def __exit__(self, exc_type, exc_value, traceback):
		self.con.close()
		return False
	def getClear(self, enc):
		cur = self.con.cursor()
		cur.execute("select clr from pair where enc=?", 
			[
				sqlite3.Binary(enc)
			]
		)
		clr = cur.fetchone()
		cur.close()
		if clr is not None:
			return clr[0]
		else:
			return None
	def insert(self, enc, clr):
		cur = self.con.cursor()
		cur.execute("insert into pair values(?, ?)", 
			[
				sqlite3.Binary(enc),
				sqlite3.Binary(clr)
			]
		)
		self.con.commit()
		cur.close()

class HitronCrypt:
	def __init__(self, host, user, password, baseconfigfile):
		self.baseconfig = bytearray(open(baseconfigfile, "rb").read())
		self.user = user
		self.password = password
		self.ctrl = HitronControl(host)
		self.fields = 410
		self.magic = {
			'ipfilter': {'offset':0x1A60, 'next':0x40, 'fields':100},
			'ipv6filter': {'offset':0x3620, 'next':0x80, 'fields':35},
			'hostport': {'offset':0x690, 'next':0x30, 'fields':35},
			'machostport': {'offset':0x47D8, 'next':0x40, 'fields':35},
		}
		self.chunklen = 8
	def prepareConfig(self, encs):
		config = self.baseconfig
		o = 0
		for tab in self.magic:
			for i in range(0, self.magic[tab]['fields']):
				offset = self.magic[tab]['offset'] + i * self.magic[tab]['next']
				if o >= len(encs):
					return config
				config[offset:offset+self.chunklen] = encs[o]
				o+=1
				if o >= len(encs):
					return config
				config[offset+self.chunklen:offset+self.chunklen*2] = encs[o]
				o+=1
		return config
	def decrypt(self, encs):
		config = self.prepareConfig(encs)
		self.ctrl.login(self.user, self.password)
		self.ctrl.uploadConfig(config)
		self.ctrl.waitOnline()
		# erneuter login hier, weil der router neustartet und
		# die session verloren geht, wenn eine config hochgeladen wird
		self.ctrl.login(self.user, self.password)
		clrs = self.ctrl.readIpFilterRules() + self.ctrl.readHostPortRules()
		self.ctrl.logout()
		return clrs[:len(encs)]

def main(args):
	'''
	hc = HitronControl(args.host)
	hc.login(args.user, args.password)
	hc.createIpFilterRules([])#range(0, 100))
	hc.createIpv6FilterRules([])#range(0, 100))
	hc.createHostPortRules([])#range(0, 100))
	hc.createMacHostPortRules([])#range(0, 100))
	hc.logout()
	'''

	hc = HitronCrypt(args.host, args.user, args.password, "cmconfig_base.cfg")
	with io.open(args.file, "rb") as f:
		with HitronCryptDB('hitroncrypt.db') as hcdb:
			encs = []
			while True:
				d = f.read(8)
				if len(d) != 8:
					break
				clr = hcdb.getClear(d)
				if clr is not None:
					sys.stdout.write(clr)
					continue
				encs.append(d)
				if len(encs) == hc.fields:
					clrs = hc.decrypt(encs)
					for i in range(0, len(clrs)):
						hcdb.insert(encs[i], clrs[i])
						sys.stdout.write(clrs[i])
					encs = []
			if len(encs) > 0:
				clrs = hc.decrypt(encs)
				for i in range(0, len(clrs)):
					hcdb.insert(encs[i], clrs[i])
					sys.stdout.write(clrs[i])
				encs = []
	return 0

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Entschluesselt Konfigurationsdateien von Hitron-Routern')
	parser.add_argument('file', type=str)
	parser.add_argument('host', type=str)
	parser.add_argument('user', type=str)
	parser.add_argument('password', type=str)
	args = parser.parse_args()
	sys.exit(main(args))
