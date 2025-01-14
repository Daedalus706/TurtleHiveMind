---@class StorageAPI

---@return table inventory itemName and count for all inventory slots of the turtle
local function getInventory()
    local inventory = {}
    for i = 1, 16, 1 do
        local itemData = turtle.getItemDetail(i)
        table.insert(inventory, i, itemData)
    end
    return inventory
end


---@return number slot the slot or 0 if no empty slots are left
---@param except number? (optional) a slot to be excluded from the search
local function findEmptySlot(except)
    except = except or 0
    local slotLookUp = {4, 8, 12, 13, 14, 15, 2, 3, 5, 6, 7, 9, 10, 11, 1, 16}
    for _, slot in ipairs(slotLookUp) do
        if turtle.getItemCount(slot) == 0 and slot ~= except then
            return slot
        end
    end
    return 0
end

---@return number slot the first slot or 0 if no empty slots are left
local function findFirstEmptySlot()
    for i = 1, 16, 1 do
        if turtle.getItemCount(i) == 0 then
            return i
        end
    end
    return 0
end

---@param itemName string? the name of the item that should fit in the turtle, leave blank or nil if no specific item is required
---@return number space the number of items of the specified type, that can fit in the turtles inventory
local function spaceForItem(itemName)
    local space = 0
    for i = 1, 16, 1 do
        local itemDetail = turtle.getItemDetail(i)
        if not itemDetail then
            space = space + 64
        elseif itemName then
            if itemDetail.name == itemName then
                space = space + turtle.getItemSpace(i)
            end
        end
    end
    return space
end


--- moves the item in the slot to another free position
---@return boolean success
---@param slot number
local function clearSlot(slot)
    if not turtle.getItemCount(slot) == 0 then
        local emptySlot = findEmptySlot()
        if emptySlot == 0 then
            return false
        end
        turtle.transferTo(emptySlot)
    end
    return true
end


--- selects the specified Item, if present
---@return boolean sucess
---@param itemName string
local function selectItem(itemName)
    for i = 1, 16, 1 do
        turtle.select(i)
        local detail = turtle.getItemDetail()
        if detail and detail.name == itemName then
            return true
        end
    end
    return false
end


--- checks if the specified item is selected
---@return boolean isSelected
---@param itemName string
local function isSelected(itemName)
    local detail = turtle.getItemDetail(turtle.getSelectedSlot())
    if detail and detail.name == itemName then
        return true
    end
    return false
end

---If a chest is st the specified chest, the Items will be moved to the chest
---@param side string top, bottom, front
---@return table successState 0 = success, 1 = side not found
local function dropAllItems(side)
    local transferCount = 0
    local drop = nil

    if side == "top" then
        drop = turtle.dropUp
    elseif side == "front" then
        drop = turtle.drop
    elseif side == "bottom" then
        drop = turtle.dropDown
    else
        return {1, transferCount}
    end

    for i = 1, 16, 1 do
        turtle.select(i)
        local itemCount = turtle.getItemCount()
        if drop() then
            transferCount = transferCount + itemCount
        end
    end

    return {0, transferCount}

end

---@param side string top, bottom, front, left, right, back
---@return table? content a table with chest slots as keys and a table with name, count 
local function getChestContent(side)
    local chest = peripheral.wrap(side)
    if chest then
        return chest.list()
    end
    return nil
end


---@param side string top, bottom, front, left, right, back
---@return table? content a table with chest slots as keys and a table with name, count 
local function getChestSize(side)
    local chest = peripheral.wrap(side)
    if chest then
        return chest.size()
    end
    return nil
end


---@param side string top, bottom, front
---@param itemName string? the name of the item that should fit in the chest, leave blank or nil if no specific item is required
---@param itemLimit number? default 64, if an item can't be stacked or the stack size is not 64 (like 16) you can provide the appropriate stacksize
---@return table success {success = number, transferCount = number} 0 = success, 1 = wrong siden name
local function spaceForItemInChest(side, itemName, itemLimit)
    if not itemLimit then
        itemLimit = 64
    end
    -- check if the peripheral is present
    local chest = peripheral.wrap(side)
    if not chest then
        return {1, 0}
    end

    local space = 0
    local content = chest.list()
    for i = 1, #content, 1 do
        if not content[i] then
            space = space + itemLimit
        elseif itemName and content[i].name == itemName then
            space = space + itemLimit - content[i]
        end
    end
    return {0, space}
end



---Puts specific items into a chest.
---@param side string top, bottom, front
---@param itemName string
---@param itemCount number? can be left empty if all items should be put into the chest
---@return table successState {success = number, transferCount = number} 0 = success, 1 = item not found, 2 = not enough in store, 3 = not enough chest space, 5 = wrong siden name, 6 = peripheral not found
local function pushItemToChest(side, itemName, itemCount)
    if not itemCount then
        itemCount = 64 * 16
    end

    -- check if the peripheral is present
    local chest = peripheral.wrap(side)
    if not chest then
        return {6, 0}
    end

    -- select the function for the specified peripheral location
    local drop = nil
    if side == "top" then
        drop = turtle.dropUp
    elseif side == "front" then
        drop = turtle.drop
    elseif side == "bottom" then
        drop = turtle.dropDown
    else
        return {5, 0}
    end


    local transferCount = 0
    for i = 1, 16, 1 do
        turtle.select(i)
        local detail = turtle.getItemDetail()
        if detail and detail.name == itemName then
            local dropAmount = math.min(64, itemCount, detail.count)
            drop(dropAmount)
            transferCount = transferCount + dropAmount
        end
    end


    return {0, transferCount}

end

---Fetches specific items from a chest to the turtles inventory.
---@param itemName string
---@param itemCount number
---@param side string top, bottom, front
---@return table successState {success: number, transferCount: number} 0 = success, 1 = item not found, 2 = not enough in store, 3 = not enough inventory space, 4 = no space to move items, 5 = wrong siden name, 6 = peripheral not found
local function pullItemFromChest(side, itemName, itemCount)

    -- check if the peripheral is present
    local chest = peripheral.wrap(side)
    if not chest then
        return {6, 0}
    end

    -- select the function for the specified peripheral location
    local suck = nil
    local drop = nil
    if side == "top" then
        suck = turtle.suckUp
        drop = turtle.dropUp
    elseif side == "front" then
        suck = turtle.suck
        drop = turtle.drop
    elseif side == "bottom" then
        suck = turtle.suckDown
        drop = turtle.dropDown
    else
        return {5, 0}
    end

    -- Check if the turtle has space for any item if the specified type
    local turtleItemSpace = spaceForItem(itemName)
    if turtleItemSpace == 0 then
        return {3, 0}
    end

    -- get item from first slot, if present
    local totalTransferedItems = 0
    local suckAmount = 64
    if chest.getItemDetail(1) and chest.getItemDetail(1).name == itemName then
        suckAmount = math.min(itemCount, 64, turtleItemSpace, chest.getItemDetail(1).count)
        suck(suckAmount)
        itemCount = itemCount - suckAmount
        totalTransferedItems = totalTransferedItems + suckAmount
    end


    -- probe the chest
    local storeItemSlots = {}
    local storeItemCount = 0
    local content = chest.list()
    local emptySlot = 0
    for i = 1, chest.size(), 1 do
        if content[i] then
            if content[i].name == itemName then
                storeItemCount = storeItemCount + content[i].count
                table.insert(storeItemSlots, i)
            end
        else
            if emptySlot == 0 then
                emptySlot = i
            end
        end
    end

    -- Chest does not have the provided item
    if storeItemCount == 0 then
        return {1, 0}
    end

    -- Check if the chest is full
    local turtleTempSlot = nil
    if emptySlot == 0 then
        turtleTempSlot = findEmptySlot()
        if content[1].name == itemName then
            suckAmount = math.min(64, itemCount, turtleItemSpace, content[1].count)

            suck(suckAmount)
            if not chest.getItemDetail(1) then
                content[1] = nil
                emptySlot = 1
            else
                content[1].count = content[1].count-suckAmount
            end

            totalTransferedItems = totalTransferedItems + suckAmount
            turtleItemSpace = turtleItemSpace - suckAmount
            if totalTransferedItems == itemCount then
                return {0, totalTransferedItems}
            end
        end
        if turtleTempSlot == 0 and chest.getItemDetail(1) then
            return {4, totalTransferedItems}
        end
        if not chest.getItemDetail(1) then
            emptySlot = 1
        end
    end

    -- empty slot 1 for item transfer
    if emptySlot == 0 then
        turtleTempSlot = findEmptySlot()
        turtle.select(turtleTempSlot)
        suck()
    elseif storeItemSlots[1] == 1 then
        local inSlot1 = 0
        if chest.getItemDetail(1) then
            inSlot1 = chest.getItemDetail(1).count
        end
        suckAmount = math.min(itemCount-totalTransferedItems, 64, turtleItemSpace, inSlot1)
        suck(suckAmount)
        totalTransferedItems = totalTransferedItems + suckAmount
        turtleItemSpace = turtleItemSpace - suckAmount
    else
        chest.pushItems(side, 1, 64, emptySlot)
    end

    -- transfer items (loop starts at 2 because slot 1 is already cleared)
    for i = 1, #storeItemSlots, 1 do
        local slot = storeItemSlots[i]
        local itemsInFirst = chest.pushItems(side, slot, 64, 1)
        local itemsLeftToTernsfer = itemCount - totalTransferedItems

        suckAmount = math.min(64, itemsLeftToTernsfer, itemsInFirst, turtleItemSpace)
        suck(suckAmount)

        totalTransferedItems = totalTransferedItems + suckAmount
        turtleItemSpace = turtleItemSpace - suckAmount
        itemsLeftToTernsfer = itemCount - totalTransferedItems

        if turtleItemSpace == 0 and itemsLeftToTernsfer ~= 0 then
            return {3, totalTransferedItems}
        elseif itemsLeftToTernsfer == 0 then
            break
        end
    end

    -- move temporarely stored items back to chest
    if turtleTempSlot then
        turtle.select(turtleTempSlot)
        drop()
    end

    -- check if not enough items were in chest
    if itemCount - totalTransferedItems > 0 then
        return {2, totalTransferedItems}
    end

    return {0, totalTransferedItems}
end


---combines all broken stacks in a chest and moves them to the front
---@param side string top, bottom, front, left, right, back
---@return number success 0 if successful, 1 if no chest was found at the specified side
local function compactChest(side)
    local chest = peripheral.wrap(side)
    if not chest then
        return 1
    end

    for i = 1, chest.size(), 1 do
        local iDetail = chest.getItemDetail(i)

        -- if slot empty, move any item to slot
        if not iDetail then
            local itemsRemain = false
            for j = i+1, chest.size(), 1 do
                if chest.getItemDetail(j) then
                    chest.pushItems(side, j, 64, i)
                    iDetail = chest.getItemDetail(i)
                    itemsRemain = true
                    break
                end
            end
            if not itemsRemain then -- end if no items are left to compact
                return 0
            end
        end

        -- move all items from other slots to i, until i is full
        local itemsRemain = false
        for j = i+1, chest.size(), 1 do
            local jDetial = chest.getItemDetail(j)

            -- move to next slot if the current slot is full
            if chest.getItemLimit(i) - iDetail.count == 0 then
                goto continue
            end

            
            if jDetial then
                itemsRemain = true
                if jDetial.name == iDetail.name then
                    chest.pushItems(side, j, 64, i)
                end
            end
        end
        if not itemsRemain then -- end if no items are left to compact
            return 0
        end
        ::continue::
    end
    return 0
end


return {
    getInventory = getInventory,
    findEmptySlot = findEmptySlot,
    findFirstEmptySlot = findFirstEmptySlot,
    spaceForItem = spaceForItem,
    clearSlot = clearSlot,
    selectItem = selectItem,
    isSelected = isSelected,
    dropAllItems = dropAllItems,
    spaceForItemInChest = spaceForItemInChest,
    pushItemToChest = pushItemToChest,
    pullItemFromChest = pullItemFromChest,
    getChestContent = getChestContent,
    getChestSize = getChestSize,
    compactChest = compactChest,
}