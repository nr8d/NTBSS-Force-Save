local UEHelpers = require("UEHelpers")

local cmdPath = "C:/temp/ue_cmd.txt"

print("[MySaveTest] Command listener started")

--------------------------------------------------
-- DUMP SAVE
--------------------------------------------------
function DumpSave()

    local GI = UEHelpers.GetGameInstance()

    if not GI:IsValid() then
        print("[MySaveTest] GI invalid")
        return
    end

    local saveObj = GI.SaveGameObject

    print("[MySaveTest] SaveGameObject: " .. tostring(saveObj))

    local ok, err = pcall(function()

        local result = UEHelpers.GetGameplayStatics():SaveGameToSlot(
            saveObj,
            "dumped_save",
            0
        )

        print("[MySaveTest] SaveGameToSlot result: " .. tostring(result))
    end)

    if not ok then
        print("[MySaveTest] Dump Error: " .. tostring(err))
    end
end

--------------------------------------------------
-- UPLOAD SAVE
--------------------------------------------------
function UploadSave()

    local GI = UEHelpers.GetGameInstance()

    if not GI:IsValid() then
        print("[MySaveTest] GI invalid")
        return
    end

    local ok, err = pcall(function()

        local GS = UEHelpers.GetGameplayStatics()

        local exists = GS:DoesSaveGameExist(
            "dumped_save",
            0
        )

        print("[MySaveTest] Backup exists: " .. tostring(exists))

        if exists then

            local loadedSave = GS:LoadGameFromSlot(
                "dumped_save",
                0
            )

            print("[MySaveTest] Loaded: " .. tostring(loadedSave))

            if loadedSave and loadedSave:IsValid() then

                GI:SetSaveDataForSteam(loadedSave)

                print("[MySaveTest] Pushed to Steam!")
            end
        end
    end)

    if not ok then
        print("[MySaveTest] Upload Error: " .. tostring(err))
    end
end

--------------------------------------------------
-- COMMAND LOOP
--------------------------------------------------
LoopAsync(500, function()

    local f = io.open(cmdPath, "r")

    if f then

        local cmd = f:read("*all")
        f:close()

        os.remove(cmdPath)

        cmd = cmd:gsub("%s+", "")

        print("[MySaveTest] Command: " .. cmd)

        --------------------------------------------------
        -- DUMP
        --------------------------------------------------
        if cmd == "dump" then

            ExecuteInGameThread(function()
                DumpSave()
            end)

        --------------------------------------------------
        -- UPLOAD
        --------------------------------------------------
        elseif cmd == "upload" then

            ExecuteInGameThread(function()
                UploadSave()
            end)
        end
    end

    return false
end)

print("[MySaveTest] Ready")