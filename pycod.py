#!/usr/bin/env python

__version__ = '0.0.2'

import json
import argparse
import sys 
import logging
from subprocess import Popen, PIPE
import shlex

CONTAINERS_PATH = "/volume1/docker/"
DOCKER_BIN = "docker"

global CONF_FILE 
global DRY_RUN

def main():
	# handle parameters
	###################
	parser = argparse.ArgumentParser(description="doc parser")
	parser.add_argument("command", help = "command to launch", choices=["info", "shell", "start", "stop", "restart", "refresh", "run", "remove"])
	parser.add_argument("application", help ="application name")
	parser.add_argument("--dry-run", action="store_true", dest="dry_run")
	args = parser.parse_args()

	command = args.command
	application = args.application
	global DRY_RUN
	DRY_RUN = args.dry_run

	# logging
	#########
	#logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
	log_file = ("%s%s/%s.log" % (CONTAINERS_PATH, args.application, args.application))
	if DRY_RUN:
		logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format="%(levelname)s - %(message)s")
	else:
		logging.basicConfig(filename=log_file, level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
	logging.info("\n***********************\n*** New doc session ***\n***********************") #debug, info, warning, error, critical
	logging.info("command: %s " % command)
	logging.info("dry-run ? %s" % str(DRY_RUN))

	# open container configuration file
	###################################
	global CONF_FILE
	#CONF_FILE = "".join((CONTAINERS_PATH, args.application, "/", args.application, ".json"))
	CONF_FILE = ("%s%s/%s.json" % (CONTAINERS_PATH, args.application, args.application))
	logging.debug("Opening conf file %s" % CONF_FILE)

	with open(CONF_FILE) as json_data:
		try:
			params = json.load(json_data)
			logging.debug("configuration file loaded")
		except:
			logging.error("Error opening config file %s" % CONF_FILE)
			print ("Error opening config file %s" % CONF_FILE)
			sys.exit(2)

	# handle commands
	#################
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

# functions
###########
def callDocker (command_options):
	# Is it a good idea ?
	docker_cmd = "%s %s" % (DOCKER_BIN, command_options)
	logging.info(docker_cmd)
	if (DRY_RUN): return
	process = Popen(shlex.split(docker_cmd))
	try:
		(output, err) = process.communicate()
		exit_code = process.wait()
	except:
		logging.error("Docker command failed %s" % docker_cmd)
		logging.error("%s" % err)
		sys.exit(2)
	logging.debug(output)
	return output

def getContainerId (params):
	logging.debug("Always take id from docker command, unless in DRY_RUN") # docker ps --filter "name=params['name']" --format "{{.ID}}"
	cmd = "ps --filter 'name=%s' --format '{{.ID}}'" % (params["name"])
	logging.debug(cmd)
	output = callDocker(cmd)
	if (DRY_RUN): output = params["id"]
	return str(output).rstrip()

def setContainerId ( newId ):
	# Need to bulletproof this later
	if (DRY_RUN): return
	try:
		with open(CONF_FILE, "r+") as confFile:
			jsonData = json.load(confFile)
			jsonData["id"] = newId
			confFile.seek(0)
			json.dump(jsonData, confFile)
	except:
		logging.error("Can't write to file %s" % CONF_FILE)
		

def updateImage (params):
	logging.info("Updating image %s:%s for container %s" % (params["image"], params["image_tag"], params["name"] ))
	cmd = "pull %s:%s" % (params["image"], params["image_tag"])
	output = callDocker (cmd)

def info ( params ):
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
                        print ("   > %s = %s" % (str(env_variable["name"]), str(env_variable["value"])))
        else:
                print ("no variable")

	return;


def shell ( params ):
	id_container = getContainerId (params)
	if (id_container <> params["id"]):
		logging.info("different ids found, update json file with %s" % id_container)
		# for synology compatibility for now
		setContainerId(id_container)

	# Launch Shell
	##############
	if "prefered_shell" in params:
		prefered_shell = params["prefered_shell"]
	else:
		prefered_shell = "/bin/bash"
	cmd = "exec -it %s %s" % (id_container, prefered_shell)
	logging.info("Launching %s on %s" % (prefered_shell, params["name"]))
	output = callDocker(cmd)
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
	
# application main
##################
if __name__ == "__main__":
    main()
