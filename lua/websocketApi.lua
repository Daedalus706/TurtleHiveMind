---@class WebsocketAPI

local websocket = nil
local running = true
local PING_INTERVAL = 5
local TIMEOUT_INTERVAL = 10
local lastMessageTime = os.clock()


--- Initialize WebSocket-Connection
---@param url string the url the turtle sould connect to
---@return boolean success 
local function connect(url)
    if websocket then
        print("Already connected")
        return false
    end
    local success, ws = pcall(http.websocket, url)
    if success then
        websocket = ws
        print("WebSocket connected: " .. url)
        return true
    else
        print("Connection failed: " .. ws)
        return false
    end
end


-- Closes WebSocket-Connection
local function disconnect()
    if websocket then
        websocket.close()
        websocket = nil
        print("WebSocket connection closed")
    end
end


--- Sends the data to the server
---@param type string 
---@param data table?
local function send(type, data)
    if not websocket then
        error("WebSocket not connected")
        running = false
    end
    local return_table = {
        turtle_id = os.getComputerID(),
        type = type,
        payload = data
    }
    websocket.send(textutils.serialiseJSON(return_table))
end


--- sends a ping to the server
local function sendPing()
    if websocket then
        send("ping", nil)
        print("Ping an den Server gesendet.")
    end
end


--- answers a ping from the server
local function sendPong()
    if websocket then
        send("pong", nil)
    end
end


--- Starts the websocket listener thread.
---@param messageHandler function
local function startListener(messageHandler)
    if not websocket then
        error("WebSocket not connected")
    end

    parallel.waitForAny(
        function()
            while running do
                local message = websocket.receive()
                if message then
                    lastMessageTime = os.clock()
                    local success, data = pcall(textutils.unserializeJSON, message)

                    if not success then
                        print("Invalid message reveived: " .. message)
                    end

                    if data.type == "ping" then
                        sendPong()
                    else
                        messageHandler(data)
                    end

                end
            end
        end,
        function ()
            while running do
                if os.clock() - lastMessageTime > PING_INTERVAL then
                    sendPing()
                end

                sleep(1)

                if os.clock() - lastMessageTime > TIMEOUT_INTERVAL then
                    print("Connection Timeout")
                    websocket.close()
                    running = false
                end
            end
        end
    )
end


--- Checks if the websocket is connected
---@return boolean status
local function isConnected()
    return websocket ~= nil
end


--- Checks if the listener is running
---@return boolean status 
local function isRunning()
    return running
end


-- API-Tabelle
local API = {
    connect = connect,
    disconnect = disconnect,
    send = send,
    startListener = startListener,
    isConnected = isConnected,
    isRunning = isRunning,
}

return API
