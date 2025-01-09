-- positionApi.lua

---@class PositionAPI
---@field loadPosition fun(): nil
---@field savePosition fun(): nil
---@field getPosition fun(): table
---@field getDirection fun(): number

local position = { x = 0, y = 0, z = 0 }
local direction = 0 -- 0 = Norden, 1 = Osten, 2 = Süden, 3 = Westen

local function loadPosition()
    if fs.exists("position.txt") then
        local file = fs.open("position.txt", "r")
        local data = textutils.unserialize(file.readAll())
        file.close()
        position = data.position or position
        direction = data.direction or direction
    end
    print("Turtle position and direction loaded")
end

local function savePosition()
    local data = {
        position = position,
        direction = direction,
    }
    local file = fs.open("position.txt", "w")
    file.write(textutils.serialize(data))
    file.close()
end

local oldForward = turtle.forward
local oldBack = turtle.back
local oldUp = turtle.up
local oldDown = turtle.down
local oldTurnLeft = turtle.turnLeft
local oldTurnRight = turtle.turnRight

function turtle.forward()
    if oldForward() then
        if direction == 0 then position.z = position.z - 1
        elseif direction == 1 then position.x = position.x + 1
        elseif direction == 2 then position.z = position.z + 1
        elseif direction == 3 then position.x = position.x - 1
        end
        savePosition()
        return true
    end
    return false
end

function turtle.back()
    if oldBack() then
        if direction == 0 then position.z = position.z + 1
        elseif direction == 1 then position.x = position.x - 1
        elseif direction == 2 then position.z = position.z - 1
        elseif direction == 3 then position.x = position.x + 1
        end
        savePosition()
        return true
    end
    return false
end

function turtle.up()
    if oldUp() then
        position.y = position.y + 1
        savePosition()
        return true
    end
    return false
end

function turtle.down()
    if oldDown() then
        position.y = position.y - 1
        savePosition()
        return true
    end
    return false
end

function turtle.turnLeft()
    if oldTurnLeft() then
        direction = (direction - 1) % 4
        savePosition()
        return true
    end
    return false
end

function turtle.turnRight()
    if oldTurnRight() then
        direction = (direction + 1) % 4
        savePosition()
        return true
    end
    return false
end

---@return table position {x, y, z}
local function getPosition()
    return position
end

---@return number direction 0 = north, 1 = east, 2 = south, 3 = west
local function getDirection()
    return direction
end

-- API-Export
return {
    loadPosition = loadPosition,
    savePosition = savePosition,
    getPosition = getPosition,
    getDirection = getDirection,
}
