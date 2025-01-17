local url = "ws://4.245.190.111:5020"


_G.stateAPI = require("StateAPI")
_G.positionAPI = require("PositionAPI")
_G.websocketAPI = require("WebsocketAPI")
_G.storageAPI = require("StorageAPI")
_G.stateAPI = require("StateAPI")
_G.util = require("util")

-- Load position data from file
stateAPI.loadStates()
positionAPI.loadPosition()

-- Connect to websocket
websocketAPI.connect(url)
websocketAPI.performHandshake()

shell.run("online_turtle")

-- wget run "https://magnus-rpg.de/file/seed.lua"

