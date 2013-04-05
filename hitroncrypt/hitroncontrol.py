#!/usr/bin/env python

import requests
import re
import time
import StringIO

class HitronControl:
	def __init__(self, host):
		self.host = host
		self.s = requests.Session()
		self.reFieldMatch = re.compile(r'(?:\b\":\"\b|\|)(.{8})(.{8})?,')
	def login(self, username, password):
		r = self.s.get(
			"http://"+self.host+"/login.asp",
			timeout=3
		)
		r = self.s.post(
			"http://"+self.host+"/goform/login",
			timeout=3,
			data={
				"user":username,
				"pws":password
			}
		)
		if "<script>location.replace('/login.asp');</script>" in r.content:
			raise Exception("Login Failed")
	def uploadConfig(self, config):
		with StringIO.StringIO(config) as fconfig:
			r = self.s.post(
				"http://"+self.host+"/goform/Config",
				timeout=3,
				files={
					"binary": ("cmconfig.cfg", fconfig)
				},
				data={
					"file":"feat-lan-backup",
					"dir":"admin/",
					"Restore":"1"
				}
			)
	def logout(self):
		try:
			r = self.s.get(
				"http://"+self.host+"/goform/logout",
				timeout=1
			)
		except:
			pass
	def readIpFilterRules(self):
		r = self.s.get(
			"http://"+self.host+"/admin/feat-firewall-port-lan.asp",
			timeout=3
		)
		l = []
		for m in self.reFieldMatch.findall(r.content):
			l.append(m[0])
			l.append(m[1])
		return l
	def readHostPortRules(self):
		r = self.s.get(
			"http://"+self.host+"/admin/feat-firewall-port-forward-v6.asp",
			timeout=3
		)
		l = []
		for m in self.reFieldMatch.findall(r.content):
			l.append(m[0])
			l.append(m[1])
		return l
	def waitOnline(self):
		# hier bessere methode einfuegen den online-status des routers zu lesen
		time.sleep(60 * 3) # 3 mins
	def activateWifi(self):
		try:
			r = self.s.post(
				"http://"+self.host+"/goform/Wls",
				timeout=1,
				data={
					"dir":"admin/",
					"WFReset":"Wifi%20Factory%20Reset%20",
					"file":"wireless"
				}
			)
		except:
			pass
	def createIpFilterRules(self, numbers):
		data = {
			"ServiceB":"1",
			"dir":"admin/",
			"file":"feat-firewall-port-lan",
		}
		for number in numbers:
			data["Service"+str(number)] = ("%08d" % (number+1))+",3,0,192.168.0."+str(number+1)+",192.168.0."+str(number+1)+",6666,6666,0.0.0.0,0.0.0.0,1,1"
		
		try:
			r = self.s.post(
				"http://"+self.host+"/goform/Firewall",
				timeout=5,
				data=data,
				headers={
					"Content-Type":"application/x-www-form-urlencoded",
					"Referer":"http://"+self.host+"/admin/feat-firewall-port-lan-edit.asp?id=-1"
				}
			)
		except:
			pass
	def createIpv6FilterRules(self, numbers):
		data = {
			"ServiceB":"1",
			"dir":"admin/",
			"file":"feat-firewall-port-lan",
		}
		for number in numbers:
			data["Service"+str(number)] = ("%08d" % (number+1)) + ",3,0,2001:0db8:85a3:08d3:1319:8a2e:0370:"+str(number+1)+",2001:0db8:85a3:08d3:1319:8a2e:0370:"+str(number+1)+",6666,6666,0.0.0.0,0.0.0.0,1,1"
		
		try:
			r = self.s.post(
				"http://"+self.host+"/goform/FirewallIPv6",
				timeout=5,
				data=data,
				headers={
					"Content-Type":"application/x-www-form-urlencoded",
					"Referer":"http://"+self.host+"/admin/feat-firewall-port-lan-edit-v6.asp?id=-1"
				}
			)
		except:
			pass
	def createHostPortRules(self, numbers):
		data = {
			"ServiceAPrivate":"1",
			"dir":"admin/",
			"file":"feat-firewall-port-forward-v6",
		}
		for number in numbers:
			data["Service"+str(number)] = ("%08d" % (number+1))+",3,2,2001:0db8:85a3:08d3:1319:8a2e:0370:7345,2001:0db8:85a3:08d3:1319:8a2e:0370:7345,"+str(number+1)+","+str(number+1)+","+str(number+1)+","+str(number+1)+",0.0.0.0,0.0.0.0,0,1"
		
		try:
			r = self.s.post(
				"http://"+self.host+"/goform/FirewallIPv6",
				timeout=5,
				data=data,
				headers={
					"Content-Type":"application/x-www-form-urlencoded",
					"Referer":"http://"+self.host+"/admin/feat-firewall-port-forward-edit-v6.asp?id=-1"
				}
			)
		except:
			pass
	def createMacHostPortRules(self, numbers):
		data = {
			"ServiceAPrivate_Mac":"1",
			"dir":"admin/",
			"file":"feat-firewall-port-forward-v6",
		}
		for number in numbers:
			data["Service"+str(number)] = ("%08d" % (number+1))+",3,1,"+str(number+1)+",00-80-41-ae-fd-7e"
		
		try:
			r = self.s.post(
				"http://"+self.host+"/goform/FirewallIPv6",
				timeout=5,
				data=data,
				headers={
					"Content-Type":"application/x-www-form-urlencoded",
					"Referer":"http://"+self.host+"/admin/feat-firewall-port-forward-mac-edit-v6.asp?id=-1"
				}
			)
		except:
			pass
			
if __name__ == "__main__":
	from Tkinter import *
				
	class App(Frame):
		def __init__(self, parent=None):
			Frame.__init__(self, parent)
			self.parent = parent
			self.parent.title("HitronControl")
			
			self.columnconfigure(0, pad=3)
			self.columnconfigure(1, pad=3)
			self.rowconfigure(0, pad=3)
			self.rowconfigure(1, pad=3)
			self.rowconfigure(2, pad=3)
			self.rowconfigure(3, pad=3)
			
			l = Label(self, text="Router-IP:")
			l.grid(row=0, column=0)
			self.enHost = Entry(self)
			self.enHost.insert(0, "192.168.0.1")
			self.enHost.grid(row=0, column=1)
			
			l = Label(self, text="Username:")
			l.grid(row=1, column=0)
			self.enUser = Entry(self)
			self.enUser.insert(0, "admin")
			self.enUser.grid(row=1, column=1)
			
			l = Label(self, text="Password:")
			l.grid(row=2, column=0)
			self.enPassword = Entry(self, show="*")
			self.enPassword.focus_set()
			self.enPassword.grid(row=2, column=1)

			self.buActivate = Button(self, text="Aktiviere", command=self.activate)
			self.buActivate.grid(row=3, columnspan=2)
			
			self.pack()
			
		def activate(self):
			hc = HitronControl(self.enHost.get())
			hc.login(self.enUser.get(), self.enPassword.get())
			hc.activateWifi()
			hc.logout()

	root = Tk()
	app = App(root)
	root.mainloop()
