# pycod
Simple command line docker local management in python

# Why pycod?
Docker is awesome and surrounded with great tools, so why create something else ? Well my friends, isn't it what's internet is all about ? :)

For the most curious ones, here's the story, feel free to skip it anytime!
I 'm using docker on a synology nas (to be honest, on a HP N54L running xpenology/DSM 5), and it comes with a nice gui. 
Really, it's nice, it has integrated images search, containers creation helper using a wizard or parsing a "docker run" command, easy start and stop, host and containers ressource monitoring, integrated interactive shell, and a great import/export of container configuration. That last point is useful imho, and is in a way the start of pycod.

Back to synology os, dsm, it's a lightweight linux based os with a great gui and poor command line support. This can be improved with ipkg support, but that's not the point  here, because python is already installed and ready to go, so let's use it to deal with docker's magic containers! What? Never used it before and code like crap? Who cares, it's internet, it's not like someone's gonna notice in the zillions github repositories?

# Features
- Based on outdated docker 1.6 on dsm 5 :(
- Single file simple python script, nothing fancy to install
- Json file container configuration
- Made for dsm/xpenology, but should work anywhere you may fool enough to run it
- Everyday's docker commands
- (Almost)Backward compatible with dsm's exported container configuration
- Opérations history

# Future possible features
- Better docker commands support
- Better dsm export compatibility
- Much better error handling
- Json configuration file toolbox (wizard, generate from existing docker container, editor, etc...)
- Better code quality

# Installation and configuration
Download the python file (make it executable if needed), and set the CONTAINERS_PATH to wherever you want to store your configuration and history files, and you're ready to go!

# Containers configuration file
Simple json file loosely based on dsm's export, here's an example :
```json
	{
		"name": "deluge",
		"image": "someRepo/deluge",
		"image_tag": "latest",
		"id": "",
		"restart": "always",
		"net": "",
	"prefered_shell": "/bin/bash",
	"env_variables": [
		{
			"name": "PUID",
			"value": 0
		},
		{
			"name": "PGID",
			"value": "0"
		}
		],
	"volumes_bindings": [
		{
			"host_volume_file": "/volume1/docker/deluge/config",
			"mount_point": "/config",
			"type": "rw"
		},
		{
			"host_volume_file": "/volume2/Downloads/torrent",
			"mount_point": "/data",
			"type": "rw"
		}
	],
	"port_bindings": [
		{
			"host_port": 58846,
			"type": "tcp",
			"container_port": 58846
		},
		{
			"host_port": 8112,
			"type": "tcp",
			"container_port": 8112
		},
		{
			"host_port": 53160,
			"type": "udp",
			"container_port": 53160
		},
		{
			"host_port": 53160,
			"type": "tcp",
			"container_port": 53160
		}
	]
}

```

# Usage
```shell
usage: pycod [-h] [--dry-run]
              {info,shell,start,stop,restart,refresh,run,remove} application
```
With the example json file stored in CONTAINERS_PATH/deluge/deluge.json :
```shell
pycod run deluge
```
will run a new container fully configured! Logs of all operations can be found in application folder.

# Anything else ?
dev branch is definitly more interesting than master, but can be quite unstable.
I couldn't find another project usable on synology's dsm with the same features, feel free to indicate me if there's any! (yes I know about fugu which is much better than pycod on many levels, but I'm too scared to die if use it :p)
