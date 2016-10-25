#!/usr/bin/env python

__version__ = '0.0.8'

import json
import argparse
import sys, os
import logging
from subprocess import Popen, PIPE
import shutil, shlex

global CONTAINERS_PATH
global CONF_FILE 
global DRY_RUN

CONTAINERS_PATH = "/volume1/docker/"
CONTAINERS_PATH = "./"
DOCKER_BIN = "docker"
DOCKER_BIN = "faker"

def main():
	# handle parameters
	###################
	parser = argparse.ArgumentParser(description="doc parser")
	parser.add_argument("command", help = "command to launch", choices=["info", "wizard", "shell", "start", "stop", "restart", "refresh", "run", "remove"])
	parser.add_argument("application", help ="application name")
	parser.add_argument("--dry-run", action="store_true", dest="dry_run")
	args = parser.parse_args()

	command = args.command
	application = args.application
	global DRY_RUN
	if command == "wizard":
		DRY_RUN = True
	else:
		DRY_RUN = args.dry_run
	global CONF_FILE
	CONF_FILE = os.path.join(CONTAINERS_PATH, application, "%s.json" % application)


	# logging
	#########
	if DRY_RUN:
		logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format="%(levelname)s - %(message)s")
	else:
		log_file = os.path.join(CONTAINERS_PATH, application, "%s.log" % application)
		logging.basicConfig(filename=log_file, level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
	logging.info("\n***********************\n*** New doc session ***\n***********************") #debug, info, warning, error, critical
	logging.info("command: %s " % command)
	logging.info("dry-run ? %s" % str(DRY_RUN))


	# handle commands
	#################
	if command == "wizard":
	    wizard(application)
	    print("Wizard is going home!")
	else:
	    params = readParams(application)
 	    if command == "info":
		info(params)
	    elif command == "shell":
		shell(params)
	    elif command == "start":
		start(params)
	    elif command == "stop":
		stop(params)
	    elif command == "restart":
		stop(params)
		start(params)
	    elif command == "refresh":
		updateImage(params)
		stop(params)
		start(params)
	    elif command == "remove":
		stop(params)
		remove(params)
	    elif command == "run":
		run(params)
		
	sys.exit(0)

# functions
###########
def readParams ( application ):
	logging.debug("Opening conf file %s" % CONF_FILE)

	with open(CONF_FILE) as conf_file:
		try:
			params = json.load(conf_file)
			logging.debug("configuration file loaded")
			return params
		except:
			logging.error("Error opening config file %s" % CONF_FILE)
			print ("Error opening config file %s" % CONF_FILE)
			sys.exit(2)

def writeJson ( out_file, data ):
	tmp_file = "%s%s" % (out_file, ".tmp")
	with open(tmp_file, "w") as conf_file:
		try:
			json.dump(data, conf_file, indent=4, sort_keys=True)
		except:
			logging.error("Error writing tmp file %s" % tmp_file)
			logging.error(os.error)
			print os.error
	bak_file = "%s%s" % (out_file, ".bak")
	if (os.path.isfile(out_file)):
		shutil.move(out_file, bak_file)
	shutil.move(tmp_file, out_file)
	
def writeParams ( params ):
	if (not os.path.isdir(os.path.dirname(CONF_FILE))):
		try:
			os.mkdir(os.path.dirname(CONF_FILE))
			logging.info("directory didn't exist, I created it for you!")
		except:
			logging.error(os.error)
			print os.error

	if (os.path.isfile(CONF_FILE)):
		logging.warning("%s already exists :|" % CONF_FILE)
		bad_idea_confirmation = raw_input ("Configuration file exists, replacing it seems to be a bad idea, do you want to do it anyway? y/[n]: ") or "n"
		if (bad_idea_confirmation == "y"):
			#os.path.join(path, *paths)
			print("you are so dead")
		else:
			# save tempory conf file anyway
			print params
			sys.exit(1)

	writeJson (CONF_FILE, params)	
	logging.info("New configuration file created %s" % CONF_FILE)
	logging.debug("configuration file check needed %s" % CONF_FILE)
	
	
def callDocker (command_options, interactive = False): 
	# Is it a good idea ?
	docker_cmd = "%s %s" % (DOCKER_BIN, command_options)
	logging.info(docker_cmd)
	
	if (DRY_RUN): return
	
	if interactive:
		process = Popen(shlex.split(docker_cmd))
	else:
		process = Popen(shlex.split(docker_cmd), stdout=PIPE)

	try:
		(output, err) = process.communicate()
		exit_code = process.wait()
		logging.debug("callDocker: %s / %s" % (output, err))
	except:
		logging.error("Docker command failed %s" % docker_cmd)
		logging.error("%s" % err)
		sys.exit(2)
	logging.debug("callDocker: %s" % output)
	return output

def getContainerId (params):
	logging.debug("Always take id from docker command, unless in DRY_RUN") # docker ps --filter "name=params['name']" --format "{{.ID}}"
	cmd = "ps --filter 'name=%s' --format '{{.ID}}'" % (params["name"])
	logging.debug(cmd)
	output = callDocker(cmd)
	logging.debug(output)
	if (DRY_RUN): output = params["id"]
	return str(output).rstrip()

def setContainerId ( params, new_id ):
	# Need to bulletproof this later
	if (DRY_RUN): return
	params["id"] = str(new_id)
	writeParams(params)
	logging.info("Writen new id %s in file %s" % (new_id, CONF_FILE))
		

def updateImage (params):
	logging.info("Updating image %s:%s for container %s" % (params["image"], params["image_tag"], params["name"] ))
	cmd = "pull %s:%s" % (params["image"], params["image_tag"])
	output = callDocker (cmd)

def info ( params ):
	# print json.dumps(params, sort_keys=True, indent=4, separators=(',', ': '))
	#docker inspect -f {{.Mounts}} deluge
	print ("**** %s **** based on %s:%s" % (params["name"], params["image"], params["image_tag"]))
	print (" > id: %s" % params["id"])
	print (" > restart: %s" % params["restart"])
	print (" > shell: %s" % params["prefered_shell"])
	print (" > net: %s" % params["net"])
	if "port_bindings" in params:
		print ("** Ports bindings **")
		for port_binding in params["port_bindings"]:
			print ("   > %s->%s/%s" % (str(port_binding["container_port"]), str(port_binding["host_port"]), port_binding["type"])) 
	else:
		print ("no port")

	if "volumes_bindings" in params:
		print ("** Volumes bindings **")
		for volume_binding in params["volumes_bindings"]:
			print ("   > %s:%s - %s" % (volume_binding["host_volume_file"], volume_binding["mount_point"], volume_binding["type"]))
	else:
		print ("no volume")

	if "env_variables" in params:
                print ("** Env variables **")
                for env_variable in params["env_variables"]:
                        print ("   > %s = %s" % (str(env_variable["key"]), str(env_variable["value"])))
        else:
                print ("no variable")

	return;


def shell ( params ):
	id_container = getContainerId (params)
	if (id_container <> params["id"]):
		logging.info("different ids found, update json file with %s" % id_container)
		# for synology compatibility for now
		setContainerId(params, id_container)

	# Launch Shell
	##############
	if "prefered_shell" in params:
		prefered_shell = params["prefered_shell"]
	else:
		prefered_shell = "/bin/bash"
	cmd = "exec -it %s %s" % (id_container, prefered_shell)
	logging.info("Launching %s on %s" % (prefered_shell, params["name"]))
	output = callDocker(cmd, interactive=True)
	print ("Back to docker host :) ")
	
def start ( params ):
	logging.info("Starting container %s" % params["name"] )
	cmd = "start %s" % (params["name"])
	callDocker(cmd)
	cmd = "ps --filter 'name=%s'" % (params["name"])
	output = callDocker(cmd)
	logging.info("%s " % output)

def stop ( params ):
	logging.info("Stopping container %s" % params["name"] )
	cmd = "stop %s" % (params["name"])
	output = callDocker(cmd)

def remove ( params ):
	logging.warning("Removing container %s" % params["name"])
	cmd = "rm %s" % params["name"]
	output = callDocker(cmd)

def run ( params ):
	logging.info("Running new container !")
	cmd =("run -d --name=%s --restart=%s" % (params["name"], params["restart"]))
	if params["net"]:
		cmd  = "%s --net=\"%s\"" % (cmd, params["net"])
	if "env_variables" in params:
                for env_variable in params["env_variables"]:
                        cmd = "%s -e %s=%s" % (cmd, str(env_variable["name"]), str(env_variable["value"]))
	if "port_bindings" in params:
		for port_binding in params["port_bindings"]:
			cmd = "%s -p %s:%s/%s" % (cmd, port_binding["host_port"], port_binding["container_port"], port_binding["type"])
	if "volumes_bindings" in params:
		for volume_binding in params["volumes_bindings"]:
			cmd = "%s -v %s:%s" % (cmd, volume_binding["host_volume_file"], volume_binding["mount_point"])
	cmd = "%s %s:%s" % (cmd, params["image"], params["image_tag"])
	output = callDocker(cmd)
	logging.info(output)
	print(output)

def wizard ( application ):
	global CONTAINERS_PATH
	params = {}
	confirm = "n"
	while (confirm != "y"):
		print("Wilkommen im Wizard!")
		params["name"] = application
		params["id"] = ""
		output = callDocker("images")
		print output
		params["image"] = raw_input("Image: ")
		params["image_tag"] = raw_input("Image tag [latest]: ") or "latest"
		confirm = raw_input("%s based on %s:%s, confirm? [y]/n: " % (params["name"], params["image"], params["image_tag"])) or "y"

	confirm = "n"
	while (confirm != "y"):
		params["restart"] = raw_input("restart [always]: ") or "always"
		params["net"] = raw_input("net: ")
		params["prefered_shell"] = raw_input("prefered shell [/bin/bash]: ") or "/bin/bash"
		confirm = raw_input("confirm previous values? [y]/n: ") or "y"
	
	volumes_bindings = []
	add_volume = raw_input("Do you want to add volumes? [y]/n: ") or "y"
	if (add_volume == "y"):
		confirm = "y"
		while (confirm == "y"):
			volume_binding = {}
			volume_binding["host_volume_file"] = raw_input("host volume : ")
			volume_binding["mount_point"] = raw_input("mount point: ")
			volume_binding["type"] = raw_input("mount type [rw]: ") or "rw"
			volumes_bindings.append(volume_binding.copy())
			confirm = raw_input("add another volume? y/n:  ")
	print volumes_bindings	
	params["volumes_bindings"] = volumes_bindings
	
	port_bindings = []
	add_port = raw_input("Do you want to add ports mapping? [y]/n: ") or "y"
	if (add_port == "y"):
		confirm = "y"
		while (confirm == "y"):
			port_binding = {}
			port_binding["container_port"] = raw_input("container port: ")
			port_binding["host_port"] = raw_input("host port [%s]: " % port_binding["container_port"]) or port_binding["container_port"]
			port_binding["type"] = raw_input("port type [tcp]: ") or "tcp"
			port_bindings.append(port_binding.copy())
			confirm = raw_input("add another port? y/n: ")	
	print port_bindings
	params["port_bindings"] = port_bindings

	env_variables = []
	add_variables = raw_input("Do you want to add environment variables? y/n: ")
	if (add_variables == "y"):
		confirm = "y"
		while (confirm == "y"):
			env_variable = {}
			env_variable["key"] = raw_input("variable key: ")
			env_variable["value"] = raw_input("variable value: ")
			env_variables.append(env_variable.copy())
			confirm = raw_input("add another variable? y/n: ")
	print env_variables
	params["env_variables"] = env_variables

	# Configuration file management
	###############################
	writeParams(params)
	
	

# application main
##################
if __name__ == "__main__":
    main()
