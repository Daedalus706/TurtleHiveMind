

---@return integer intValue
local function getInputInt(name)
    local variable = nil
    while not variable do
        write(name..": ")
        local userInput = read()
        variable = textutils.unserialise(userInput)
        if not variable then
            print("Please enter a valid number")
        end
    return variable
    end
end


---@return integer direction
local function getDirection()
    print("north, east, south, west")   -- 0 = north, 1 = east, 2 = south, 3 = west
    local direction = -1
    while direction < 0 do
        write("direction: ")
        local userInput = read()
        if userInput == "north" then direction = 0 end
        if userInput == "east" then direction = 1 end
        if userInput == "south" then direction = 2 end
        if userInput == "west" then direction = 3 end
        if not direction then
            print("Please enter a valid direction")
        end
    return direction
    end
end

local function downloadFile(filename)
    local response = http.get("https://magnus-rpg.de/file/" .. filename)
    if response then
        local file = fs.open(filename, "w")
        if file then
            file.write(response.readAll())
            file.close()
            response.close()
            print("Loaded file: " .. filename)
            return true
        end
    else
        print("Can't load file " .. filename)
    end
    return false
end


local function downloadFiles()
    downloadFile("file_index_table.lua")
    local files = dofile("file_index_table.lua")

    local failedToLoad = false
    for i = 1, #files do
        if not downloadFile(files[i]) then
            failedToLoad = true
        end
    end
    if failedToLoad then
        print("not all files were loaded")
    end

end


downloadFiles()

_G.positionAPI = dofile("/positionApi.lua")


local x = getInputInt("x")
local y = getInputInt("y")
local z = getInputInt("z")
local d = getDirection()


positionAPI.setDirection(d)
positionAPI.setPosition(x, y, z)

os.setComputerLabel("turtle_" .. os.getComputerID())
os.reboot()