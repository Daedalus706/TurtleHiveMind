---@class Queue
---@field new fun(): Queue
---@field enqueue fun(self: Queue, item: any): nil
---@field dequeue fun(self: Queue): table
---@field isEmpty fun(self: Queue): boolean
---@field lockQueue fun(self: Queue): nil
---@field unlockQueue fun(self: Queue): nil


local Queue = {}

function Queue:new()
    local obj = {lock = false, first = 0, last = -1, items = {}}
    setmetatable(obj, self)
    self.__index = self
    return obj
end

function Queue:lockQueue()
    while self.lock do
        os.sleep(0.001)
    end
    self.lock = true
end

function Queue:unlockQueue()
    self.lock = false
end

function Queue:enqueue(item)
    self:lockQueue()
    self.last = self.last + 1
    self.items[self.last] = item
    self:unlockQueue()
end

function Queue:dequeue()
    self:lockQueue()
    if self.first > self.last then
        error("Queue is empty")
    end
    local item = self.items[self.first]
    self.first = self.first + 1
    self.items[self.first] = nil
    self:unlockQueue()
    return item

end function Queue:isEmpty()
    return self.first > self.last
end

return Queue