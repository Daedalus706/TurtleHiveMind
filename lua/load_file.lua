local url = "https://magnus-rpg.de/file/"
local failed_to_load_file = false

local function download_file(filename)
    local response = http.get(url .. filename)
    if response then
        local file = fs.open(filename, "w")
        if file then
            file.write(response.readAll())
            file.close()
            print("Loaded File: " .. filename)
        else
            failed_to_load_file = true
            print("Failed to save " .. filename)
        end
        response.close()
    else
        failed_to_load_file = true
        print("Failed to download " .. filename)
    end
end

download_file("file_index_table.lua")

local files = dofile("file_index_table.lua")

for i = 1, #files do
    download_file(files[i])
end




if not failed_to_load_file then
    print("All files loaded")

    local args = {...}
    if #args < 1 or not (args[1] == "no_reboot") then
        print("Reboot in 1 seconds")
        sleep(1)
        os.reboot()
    end
else
    print("Not all files were loaded")
end