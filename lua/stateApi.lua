---@class StateAPI


local stateTable = {
    disconnected = "disconnected",
    connected = "connected",
    idle = "idle",
    traveling = "traveling",
    building = "building",
    farming = "farming"
}

local state = "idle"
local lastState = "idle"


local function loadStates()
    if fs.exists("state.txt") then
        local file = fs.open("state.txt", "r")
        local data = textutils.unserialize(file.readAll())
        file.close()
        state = data.state or state
        lastState = data.lastState or lastState
    end
    print("Turtle states loaded")
end

local function saveStates()
    local file = fs.open("state.txt", "w")
    file.write(textutils.serialize({state=state, lastState=lastState}))
    file.close()
end


---@param newState string the current buisy state of the turtle
local function setState(newState)
    lastState = state
    state = newState
    saveStates()
end


local function getState()
    return state
end

local function getLastState()
    return state
end


return {
    stateTable = stateTable,
    loadStates = loadStates,
    setState = setState,
    getState = getState,
    getLastState = getLastState,
}