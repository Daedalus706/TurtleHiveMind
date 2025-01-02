---@class StorrageAPI


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


---@return table successState {success = boolean, transferCount = number}
local function transferAllUp()
    local transferCount = 0
    clearSlot(16)
    turtle.select(16)
    while turtle.suckDown() do
        if not turtle.dropUp() then
            turtle.dropDown()
            return {success = false, transferCount = transferCount}
        else
            transferCount = transferCount + 1
        end
    end
    return {success = true, transferCount = transferCount}
    
end


--- Fetch specific items from the chest above to the turtles inventory. Needs a chest underneath, for temporary storage
---@return number successState 0 = success, 1 = item not found, 2 = not enough in store, 3 = not enough inventory space
---@param itemName string
---@param itemCount number
local function fetchItem(itemName, itemCount)

    return 0
end


return {
    findEmptySlot = findEmptySlot,
    clearSlot = clearSlot,
    transferAllUp = transferAllUp,
    fetchItem = fetchItem,
}