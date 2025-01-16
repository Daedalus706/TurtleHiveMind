---@class WebsocketAPI

local websocket = nil
local running = true
local PING_INTERVAL = 5
local TIMEOUT_INTERVAL = 10
local lastMessageTime = os.clock()
local _url = nil


--- Initialize WebSocket-Connection
---@param url string the url the turtle sould connect to
---@return boolean success 
local function connect(url)
    _url = url
    if websocket then
        return true
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
        return
    end
    local return_table = {
        type = type,
        payload = data
    }
    local success, message = pcall(websocket.send, textutils.serialiseJSON(return_table))
    if not success then
        print("Error while sending data: " .. tostring(message))
        pcall(websocket.close)
        websocket = nil
    end
end


--- sends a ping to the server
local function sendPing()
    if websocket then
        send("ping", nil)
    end
end


--- answers a ping from the server
local function sendPong()
    if websocket then
        send("pong", nil)
    end
end


local function performHandshake()
    if websocket then
        send("turtle_handshake", os.getComputerID())
    end
end


local function sendError(message)
    if websocket then
        send("error", message)
    end
end

---@return table websocket
local function attemptReconnect()
    print("Attempt reconnect...")
    local i = 0
    while not websocket do
        i = i + 1
        print("Attempt " .. i)
        local success, newSocket = pcall(http.websocket, _url)

        if success and newSocket then
            print("Successfully reconnected.")
            lastMessageTime = os.clock()
            newSocket.send(textutils.serialiseJSON({
                type = "handshake",
                payload = os.getComputerID()
            }))
            return newSocket
        else
            sleep(5)
        end
    end
end


--- Starts the websocket listener thread.
---@param messageHandler function
local function startListener(messageHandler)
    print("starting websocket listener")
    parallel.waitForAny(
        function()
            while running do
                if not websocket then
                    websocket = attemptReconnect()
                    print("got new websocket")
                end

                local successRecive, message = pcall(websocket.receive)
                if not successRecive then
                    print(message)
                    websocket = nil
                else
                    lastMessageTime = os.clock()
                    local successJson, data = pcall(textutils.unserializeJSON, message)

                    if not successJson then
                        print("Invalid message reveived: " .. tostring(message))
                    else

                        if data.type == "ping" then
                            sendPong()
                        else
                            messageHandler(data)
                        end

                    end
                end
            end
        end,
        function ()
            while running do
                if not websocket then
                    sleep(1)
                else
                    if os.clock() - lastMessageTime > PING_INTERVAL then
                        sendPing()
                    end

                    sleep(1)

                    if os.clock() - lastMessageTime > TIMEOUT_INTERVAL then
                        print("Connection Timeout")
                        pcall(websocket.close)
                        websocket = nil
                    end
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
    sendError = sendError,
    performHandshake = performHandshake,
    startListener = startListener,
    isConnected = isConnected,
    isRunning = isRunning,
}

return API
