---@class util



local function digTree()

    local woodTypes = {
        ["minecraft:oak_log"] = true,
        ["minecraft:spruce_log"] = true,
        ["minecraft:birch_log"] = true,
        ["minecraft:jungle_log"] = true,
    }

    local function isWood(block)
        if not block or not block.name then
            return false
        end
        return woodTypes[block.name] or false
    end

    -- check if a tree is present
    local _, blockInFront = turtle.inspect()
    if not isWood(blockInFront) then
        return false
    end

    -- move up the whole tree
    local turtleHeight = 0
    while isWood(blockInFront) do
        turtleHeight = turtleHeight + 1
        if turtle.detectUp() then
            turtle.digUp()
        end
        turtle.up()
        _, blockInFront = turtle.inspect()
    end

    turtle.dig()
    turtle.turnLeft()

    -- dig the feaves on the top of the tree
    for i = 1, 4, 1 do
        turtle.dig()
        turtle.digDown()
        turtle.forward()
        turtle.digDown()
        turtle.turnRight()
        turtle.dig()
        turtle.forward()
    end

    turtle.down()
    turtle.down()
    turtleHeight = turtleHeight - 2

    -- mine the next layer of leaves
    for i = 1, 4, 1 do
        turtle.dig()
        turtle.digDown()
        turtle.turnLeft()
        turtle.dig()
        turtle.turnRight()
        turtle.forward()
        turtle.turnLeft()
        turtle.dig()
        turtle.turnRight()
        turtle.dig()
        turtle.digDown()
        turtle.turnRight()
        turtle.dig()
        turtle.forward()
    end

    -- move back to the top of the tree
    turtle.turnRight()
    turtle.up()
    turtleHeight = turtleHeight + 1

    -- dig the tree
    for i = 1, turtleHeight, 1 do
        turtle.dig()
        turtle.down()
    end
    turtle.dig()

    -- replant tree
    if not storageAPI.isSelected("minecraft:birch_sapling") then
        storageAPI.selectItem("minecraft:birch_sapling")
    end
    turtle.place()

    local itemsTransferedToChest = 0
    itemsTransferedToChest = storageAPI.pushItemToChest("bottom", "minecraft:birch_log")
    print("Logs deposited: " .. tostring(itemsTransferedToChest[2]))
    itemsTransferedToChest = storageAPI.pushItemToChest("bottom", "minecraft:stick")
    print("Sticks deposited: " .. tostring(itemsTransferedToChest[2]))

    return true
end


return {
    digTree = digTree,
}