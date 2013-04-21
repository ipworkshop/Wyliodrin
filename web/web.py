from flask import Flask, render_template, request, redirect, session, url_for
from pymongo import MongoClient
import hashlib
import json
from xmpp import WylioXMPP

SECRET_KEY = "key"

web = Flask (__name__)
web.config.from_object(__name__)
web.debug = True

xmpp = dict ()

client = MongoClient ()
db = client.wyliodrin

def user_online():
	if "email" in session:
		return session["email"]
	else:
		return None

@web.route ("/")
def start():
	if user_online() != None:
		return redirect (url_for ("fluid"))
	else:
		return render_template ("start.html")

@web.route ("/values")
def values():
	if user_online() != None:
		email = user_online()
		print email
		signals = db.values.find ({"email":email})
		print signals.count ()
		values = []
		for value in signals:	
			del value['_id']
			values.append (value)
		return json.dumps (values)
	else:
		return ""

@web.route ("/send", methods=['POST'])
def send():
	if user_online() != None:
		email = user_online()
		if email in xmpp:
			if "red" in request.form:
				red = request.form["red"]
				xmpp[email].send_value ("red", red, "wylio.project@gmail.com/raspy")
			
			if "green" in request.form:
				green = request.form["green"]
				xmpp[email].send_value ("green", green, "wylio.project@gmail.com/raspy")
				
			if "blue" in request.form:
				blue = request.form["blue"]
				xmpp[email].send_value ("blue", blue, "wylio.project@gmail.com/raspy")
		return ""
	else:
		return ""


@web.route ("/fluid")
def fluid():
	if user_online() != None:
		return render_template ("fluid.html")
	else:
		return redirect (url_for ("start"))

@web.route ("/signup", methods=['POST'])
def signup():
	result = "0";
	email = request.form["email"];
	password = request.form["password"];
	if len(email)>0 and len(password)>0:
		md5pass = hashlib.md5(password).hexdigest()
		if db.users.find ({"email":email}).count() > 0:
			result = "0"
		else:
			if db.users.insert ({"email":email, "password":md5pass}):
				result = "1"
	return json.dumps ({"result":result})

@web.route ("/newproject", methods=['POST'])
def newproject():
	if user_online() != None:
		result = "0";
		name = request.form["name"]
		email = session["email"]
		if (len(name)>0):
			if db.projects.find ({"name":name, "email": email}).count() > 0:
				result = "0";
			else:
				db.projects.insert ({"name":name, "email": email});
				result = "1";
		return json.dumps ({"result":result})
	else:
		return ""
		
@web.route ("/listprojects")
def listprojects():
	if user_online() != None:
		result = [];
		email = user_online ()
		projectslist = db.projects.find ({"email":email})
		for project in projectslist:
			result.append (project["name"])
		print "Result ",
		print result
		return json.dumps (result)
	else:
		return ""

@web.route ("/load")
def load():
	result = "0"
	if user_online() != None:
		email = user_online ()
		source_data = db.users.find_one ({"email": email})
		if source_data != None:
			if "source" in source_data:
				source = source_data["source"]
			else:
				source = ""
			return source
		else:
			result = "0"
		return ""
	else:
		return ""

	
@web.route ("/save", methods=['POST'])
def save():
	result = "0"
	if user_online() != None:
		email = user_online ()
		source = request.form["source"];
		if db.users.update ({"email": email}, {"$set": {"source":source}})!=None:
			result = "1"
		else:
			result = "0"
		return json.dumps ({"result":result})	
	else:
		return ""

@web.route ("/run", methods=['POST'])
def run():
	result = "0"
	if user_online() != None:
		email = user_online ()
		source = request.form["source"];
		if db.users.update ({"email": email}, {"$set": {"source":source}})!=None:
			result = "1"
			if email in xmpp:
				db.values.remove ({"email":email})
				xmpp[email].run_source (source, "wylio.project@gmail.com/raspy")
		else:
			result = "0"
		return json.dumps ({"result":result})	
	else:
		return ""


@web.route ("/login", methods=['POST'])
def login():
	result = "0";
	email = request.form["email"];
	password = request.form["password"];
	if (len(email)>0):
		md5pass = hashlib.md5(password).hexdigest()
		if db.users.find ({"email":email, "password": md5pass}).count() > 0:
			result = "1";
			session["email"]=email
			xmpp[email] = WylioXMPP (email, db)
			xmpp[email].connect ("server@ipworkshop.ro", "raspberrypi")
			session.modified = True
	return json.dumps ({"result":result})

@web.route ("/logout")
def logout ():
	if "email" in session:		
		email = session["email"]
		del session["email"]
		if email in xmpp:
			xmpp[email].disconnect ()
			del xmpp[email]
	return redirect (url_for ("start"))

if __name__ == '__main__':
	web.run (host="0.0.0.0", port=8000)
