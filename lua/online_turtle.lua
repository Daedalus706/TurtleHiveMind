
local handled_messages = 0


local function sendTurtleInfo(data_type, payload)
    local data = {
        position = positionAPI.getPosition(),
        direction = positionAPI.getDirection(),
        fuel = turtle.getFuelLevel(),
        inventory = storageAPI.getInventory()
    }
    websocketAPI.send("turtle_info", data)
end


local function sendItemInfo(data_type, payload)
    local info = turtle.getItemDetail(payload.slot, true)
    local data = {
        slot = payload.slot,
        name = info.name,
        count = info.count,
        max_count = info.max_count,
        tags = info.tags
    }
    websocketAPI.send("item_info", data)
end


local function updateTurtle(data_type, payload)
    websocketAPI.downloadFiles(payload.no_reboot)
end


local function inspect_block(data_type, payload)
    local inspect_result = nil
    local pos = positionAPI.getPosition()
    if payload.direction and payload.direction == "up" then
        inspect_result = turtle.inspectUp()
        pos.y = pos.y + 1
    elseif payload.direction and payload.direction == "down" then
        inspect_result = turtle.inspectDown()
        pos.y = pos.y - 1
    elseif not payload.direction or payload.direction == "front" then
        inspect_result = turtle.inspect()
        local direction = positionAPI.getDirection()
        if direction == 0 then pos.z = pos.z - 1
        elseif direction == 1 then pos.x = pos.x + 1
        elseif direction == 2 then pos.z = pos.z + 1
        elseif direction == 3 then pos.x = pos.x - 1
        end
    else
        websocketAPI.sendError("invalid inspect direction. Try: 'up' 'down' 'front'", data_type)
        return
    end
    inspect_result.pos = pos
    websocketAPI.send("block_info", inspect_result)
end


local messageTable = {
    request_turtle_info = sendTurtleInfo,
    request_item_info = sendItemInfo,
    turtle_update = updateTurtle,
    inspect_block = inspect_block,
}


local function messageHandler(data)
    handled_messages = handled_messages + 1
    print("handled_messages: " .. handled_messages .. "type: " .. tostring(data.type))
    if not data or type(data) ~= "table" then
        print("Invalid data received: " .. type(data))
    else
        if not data.type then
            print("Invalid data type received: " .. tostring(data.type))
        else
            local handler = messageTable[data.type]
            if handler then
                local success, err = pcall(handler, data.type, data.payload)
                if not success then
                    print("Error handleing " .. data.type .. " " .. err)
                    websocketAPI.sendError(err, data.type)
                end
            end
        end
    end
end


local function setup()
end

local function main()
    while true do
        os.sleep(1)
    end

end

parallel.waitForAny(
    websocketAPI.startListener(messageHandler),
    function ()
        sleep(.5)
        setup()
        while true do
            local success, err = pcall(main)
            if not success then
                local errorMessage = "Critical Error: " .. tostring(err)
                print(errorMessage)
                websocketAPI.sendError(errorMessage)
                sleep(2)
            end
        end
    end
    
)
