#!/usr/bin/python -u

'''
	Program Name: AppIT
	Author:       Ronak Kogta, Sambuddha Basu
	Description:  git for your desktop Applications
'''

import dropbox
import glob, re, pickle, math, random
import dropbox
import getpass
import hashlib
import sys
import os

AUTH_TOKEN = 'R42X2fA2rIIAAAAAAAAAC_7-3E13jb7lSq_1VgY3DTtAKh9qRsCMrDtWoxKY2qK6'
username = ''
password = ''
client=''
def help():
	print "./appit.py"
	print "\t search <app>\t\tSearches appIT repositories"
	print "\t pull <app>\t\tPulls repository and your application data"
	print "\t push <app>\t\tPushes repository and your application data"
	print "\t reset <app> meta|appl\tReset your application's meta data and application data"
	print "\t run <app>\t\tCompose your commands into a Dockerfile and create image"
	print "\t "
	sys.exit(-1) 
	 
class appIT():
	VOLUMES=''; 
	ENV_VAR=''; 
	CAPABILITIES='';
	def  pullAll(self,appName):
		global username, password, client
	# pulling image from dockerhub 
		os.system('docker search appit/'+appName+'  >out')
		os.system('docker search '+appName+'  >out1' )
		fp=open('out','r');
		count=len(fp .readlines())
		fp.close()
		image=''
		if ( count == 1):
			#print "Appit Repository does not exist"
			fp=open('out1','r');
			count=len(fp .readlines())
			fp.close()
			
			if (count == 1):
				print "no such repository exists"
				sys.exit(-1)
			image=appName; 
		else: 
			image="appit/"+appName;
		os.system('docker pull '+image)			
		os.system('rm out out1')
	# pulling data from dropbox
		home = os.path.expanduser("~")
		app_dirs =[];
		fp=open(appName+"/config.yml",'r');
		configData=fp.readlines()
		fp.close()
		for i in configData:
			configOpt=i.split(' ');
			if(configOpt[0]=='METAMOUNT'):
				mount=configOpt[1].split("\n")[0];
				app_dirs.append(home+"/.appit/"+appName+"/"+mount);
			elif(configOpt[0]=='APPLMOUNT'):
				mount=configOpt[1].split("\n")[0];
				app_dirs.append(home+"/.appit/"+appName+"/"+mount);
		
		for app_dir in app_dirs:
			if not os.path.exists(app_dir):
				os.makedirs(app_dir);

				 	
		self.get_cred()
		orig_username = username
		# Pull ApplData
		app_dirs =[];
		fp=open(appName+"/config.yml",'r');
		configData=fp.readlines()
		fp.close()
		for i in configData:
			configOpt=i.split(' ');
			if(configOpt[0]=='METAMOUNT'):
				mount=configOpt[1].split("\n")[0];
				app_dirs.append(home+"/.appit/"+appName+"/"+mount);
			elif(configOpt[0]=='APPLMOUNT'):
				mount=configOpt[1].split("\n")[0];
				app_dirs.append(home+"/.appit/"+appName+"/"+mount) 
		WORK_DIR = app_dirs[1]
		username = orig_username + "_cache"
		self.pull_data()
		# Pull Metadata 
		WORK_DIR = app_dirs[0]
		username = orig_username + "_mozilla"
		self.pull_data()		
		return 0;		

	def pushAll(self,appName):
		global username, password, client
	# push image to dockerhub
		os.system('export DOCKER_CONTENT_TRUST=1');
		os.system('docker push appit/'+appName)	
	# push data to dropbox
		home = os.path.expanduser("~")
		app_dirs =[];
		fp=open(appName+"/config.yml",'r');
		configData=fp.readlines()
		fp.close()
		for i in configData:
			configOpt=i.split(' ');
			if(configOpt[0]=='METAMOUNT'):
				mount=configOpt[1].split("\n")[0];
				app_dirs.append(home+"/.appit/"+appName+"/"+mount);
			elif(configOpt[0]=='APPLMOUNT'):
				mount=configOpt[1].split("\n")[0];
				app_dirs.append(home+"/.appit/"+appName+"/"+mount);
	
		self.get_cred()
		orig_username = username
		# Push .cache
		WORK_DIR = app_dirs[1]
		username = orig_username + "_cache"
		self.push_data(WORK_DIR)
		# Push .mozilla
		WORK_DIR = app_dirs[0]
		username = orig_username + "_mozilla"
		self.push_data(WORK_DIR)	
	
	def get_cred(self):
		global username, password, client
		username = raw_input('Enter Dropbox username: ')
		password = getpass.getpass('Enter Dropbox password: ')

	def recur_pull_data(self,details,WORK_DIR):
		# If it is a directory, recursively pull all the files.
		if details['is_dir'] == True:
			contents = client.metadata(details['path'])
			for content in contents['contents']:
				recur_pull_data(content)
		else:
			filename = details['path'].split('/')
			filename = "/" + "/".join(filename[3:])
			filename = WORK_DIR + filename
			if not os.path.exists(os.path.dirname(filename)):
				os.makedirs(os.path.dirname(filename))
			file_data = client.get_file(details['path'])
			output = open(filename, 'wb')
			output.write(file_data.read())
			output.close()

	def pull_data(self,WORK_DIR):
		global username, password, client
		try:
			orig_pass = client.get_file(username + "/.password")
			verify_pass = hashlib.md5()
			verify_pass.update(password)
			if verify_pass.hexdigest() == orig_pass.read():
				contents = client.metadata(username + "/content")
				print "Pulling data from the server."
				for cont in contents['contents']:
					recur_pull_data(cont,WORK_DIR)
			else:
				print "Authentication failure."
				sys.exit(-1)
		except dropbox.rest.ErrorResponse:
			print "Nothing to pull from."
			sys.exit(-1)

	def push_data(self,WORK_DIR):
		global username, password, client
		verify_pass = hashlib.md5()
		verify_pass.update(password)
		try:
			orig_pass = client.get_file(username + "/.password")
			if verify_pass.hexdigest() != orig_pass.read():
				print "Authentication failure."
				sys.exit(-1)
		except dropbox.rest.ErrorResponse:
			print "Creating new account."
			client.put_file(username + "/.password", verify_pass.hexdigest())
		try:
			client.file_delete(username + "/content")
		except:
			pass

		# Finally, push the files to the server.
		print "Pushing data to the server."
		for root, dirnames, filenames in os.walk(WORK_DIR):
			root = os.path.abspath(root) + "/"
			for filename in filenames:
				file_data = open(root + filename, 'rb')
				file_path = username + "/content/" + os.path.relpath(root + filename, WORK_DIR)
				client.put_file(file_path, file_data.read())
	
	''' Prepare your run file'''			
	def run(self,appName):
		
		user=getpass.getuser();
		dockerRun='docker run -ti --rm '
		if(not os.path.exists(appName)):
			os.system("git clone https://github.com/getAppIT/"+appName);

		fp=open(appName+"/config.yml",'r');
		configData=fp.readlines();
		fp.close();
		'''fp=open(appName+"/Dockerfile",'r');
		dockerConfig=fp.read();'''
		for i in configData:
			configOpt=i.split(' ');
			if(configOpt[0]=='INTERFACE'):
				if (configOpt[1]=='X11'):
					self.VOLUMES+="--volume=/tmp/.X11-unix:/tmp/.X11-unix ";
			elif(configOpt[0]=='SOUND' and configOpt[1]=='yes\n'):
				self.VOLUMES+="--volume=/run/user/1000/pulse:/run/pulse "
			elif(configOpt[0]=='METAMOUNT'):
					mount=configOpt[1].split("\n")[0];
					self.VOLUMES+="--volume=/home/"+user+"/.appit/"+appName+"/"+mount+":/home/developer/"+mount+" "; 
			elif(configOpt[0]=='APPLMOUNT'):
					mount=configOpt[1].split("\n")[0];
					self.VOLUMES+="--volume=/home/"+user+"/.appit/"+appName+"/"+mount+":/home/developer/"+mount+" ";			
		#print self.VOLUMES
		self.ENV_VAR+=" -e DISPLAY=$DISPLAY "
		dockerRun+=self.ENV_VAR+self.VOLUMES +"appit/"+appName
		fp=open(appName+".desktop",'w'); 
		fp.writelines('[Desktop Entry]\n');
		fp.writelines('Version=0.1\n')
		fp.writelines('Name=AppIT'+appName[0].upper()+appName[1:]+'\n')
		fp.writelines('Comment=git for Desktop Application Environment\n')
		fp.writelines('Exec= '+dockerRun+'\n')
		fp.writelines('Terminal=true\n')
		fp.writelines('Type=Application\n')
		fp.writelines('Categories=Utility;Application;\n') 
		fp.close()
		os.system('chmod +x '+appName+".desktop")
		#os.system('rm -rf '+appName)
		os.system(dockerRun);			

if __name__ == '__main__':
	if len(sys.argv) < 3:
		help()
	client = dropbox.client.DropboxClient(AUTH_TOKEN)
	engine = appIT(); 

	if(sys.argv[1]=='search'):
		print "==========\nAppIT Repositories\n=========="
		os.system("docker search appit/"+sys.argv[2]);
		print 
		print "==========\nOthers Availiable\n=========="
		os.system("docker search "+sys.argv[2]); 

	elif(sys.argv[1]=='pull'):
		engine.pullAll(sys.argv[2]);
	elif(sys.argv[1]=='push'):
		engine.pushAll(sys.argv[2]);
	elif(sys.argv[1]=='reset'):
		engine.run(sys.argv[2]);
	elif(sys.argv[1]=='run'):
		engine.run(sys.argv[2]);
	