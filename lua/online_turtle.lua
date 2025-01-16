
local handled_messages = 0


local function sendTurtleInfo()
    local data = {
        position = positionAPI.getPosition(),
        direction = positionAPI.getDirection(),
        fuel = turtle.getFuelLevel(),
        inventory = storageAPI.getInventory()
    }
    websocketAPI.send("turtle_info", data)
end


local function sendItemInfo(slot)
    local info = turtle.getItemDetail(slot, true)
    local data = {
        slot = slot,
        name = info.name,
        count = info.count,
        max_count = info.max_count,
        tags = info.tags
    }
    websocketAPI.send("item_info", data)
end


local function messageHandler(data)
    handled_messages = handled_messages + 1
    print("handled_messages: " .. handled_messages .. "type: " .. tostring(data.type))
    if not data or type(data) ~= "table" then
        print("Invalid data received: " .. type(data))
    else
        if not data.type then
            print("Invalid data type received: " .. tostring(data.type))
        else

            if data.type == "request_turtle_info" then
                sendTurtleInfo()
            end

            if data.type == "request_item_info" then
                if data.payload.slot then
                    sendItemInfo(data.payload.slot)
                else
                    websocketAPI.error("missing parameter: 'slot'", data.type)
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
