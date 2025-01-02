
local handled_messages = 0

local function perform_handshake()
    local data = {
        position = positionAPI.getPosition(),
        direction = positionAPI.getDirection()
    }
    websocketAPI.send("handshake", data)
end


local function messageHandler(data)
    handled_messages = handled_messages + 1
    print("handled_messages: " .. handled_messages .. "type: " .. data.type)
end


local function setup()
    perform_handshake()
end

local function main()
    while true do
        os.sleep(1)
    end

end

setup()
parallel.waitForAny(
    websocketAPI.startListener(messageHandler),
    main()
)
