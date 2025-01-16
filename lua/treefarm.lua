

while true do
    local startFuel = turtle.getFuelLevel()
    while not util.digTree() do
        sleep(5)
    end
    print("fuel used = " .. startFuel-turtle.getFuelLevel())
end