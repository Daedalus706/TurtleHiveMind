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
    send("ping", nil)
end


--- answers a ping from the server
local function sendPong()
    send("pong", nil)
end


local function performHandshake()
    send("turtle_handshake", os.getComputerID())
end


local function sendError(message, command)
    send("error", {message=message, command=command})
end


local function sendInfo(message)
    send("info", {message=message})
end

local function sendStateChange(stateName, value)
    send("state_change", {name=stateName, value=value})
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
                type = "turtle_handshake",
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
                    print("failed to receive message: " .. tostring(message))
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


---@return boolean success
local function downloadFile(filename)
    local response = http.get("https://magnus-rpg.de/file/" .. filename)
    if response then
        local file = fs.open(filename, "w")
        if file then
            file.write(response.readAll())
            file.close()
            response.close()
            return true
        else
            sendError("failed to load file " .. filename)
        end
    else
        sendError("failed to download file " .. filename)
    end
    return false
end


---@param no_reboot boolean if true, the turtle won't reboot, after loading files
local function downloadFiles(no_reboot)
    local failed_to_load_file = false
    failed_to_load_file = (not downloadFile("file_index_table.lua")) or failed_to_load_file

    local files = dofile("file_index_table.lua")

    for i = 1, #files do
        local success = downloadFile(files[i])
        if not success then
            failed_to_load_file = true
            print("Error: failed to load " .. files[i])
        end
    end

    if not failed_to_load_file then
        sendInfo("updated")
    else
        sendError("failed to fully update")
    end

    if no_reboot then
        sleep(1)
        os.reboot()
    end
    
end


-- API-Tabelle
local API = {
    downloadFiles = downloadFiles,
    connect = connect,
    disconnect = disconnect,
    send = send,
    sendError = sendError,
    sendInfo = sendInfo,
    sendStateChange = sendStateChange,
    performHandshake = performHandshake,
    startListener = startListener,
    isConnected = isConnected,
    isRunning = isRunning,
}

return API
