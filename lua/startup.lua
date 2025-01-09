shell.run("load_file no_reboot")


local url = "ws://4.245.190.111:5020"


_G.positionAPI = require("PositionAPI")
_G.websocketAPI = require("WebsocketAPI")
_G.storageAPI = require("StorageAPI")

-- Load position data from file
positionAPI.loadPosition()

-- Connect to websocket
--websocketAPI.connect(url)
--websocketAPI.performHandshake()

--shell.run("online_turtle")

