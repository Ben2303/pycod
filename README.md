# pycod 
Simple command line docker local management in python

# dev branch :)
- [x] New container wizard (dsm gui's console cousin)
- [x] Silly code issues
- [x] Better docker commands support
- [ ] Better coding
- [ ] Better logging
- [ ] Better error handling
- [ ] Create json config from docker inspect or...
- [ ] ..trash everything and directly use docker inspect instead of json file

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
			"key": "PUID",
			"value": 0
		},
		{
			"key": "PGID",
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
              {info,shell,start,stop,restart,refresh,run,remove,wizard} application
```
With the example json file stored in CONTAINERS_PATH/deluge/deluge.json :
```shell
pycod run deluge
```
will run a new container fully configured! Logs of all operations can be found in application folder.

# Anything else ?
I couldn't find another project usable on synology's dsm with the same features, feel free to indicate me if there's any! (yes I know about fugu which is much better than pycod on many levels, but I'm too scared to die if use it :p)
