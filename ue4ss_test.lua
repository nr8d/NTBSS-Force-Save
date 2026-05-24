local UEHelpers = require("UEHelpers")

RegisterKeyBind(Key.F5, function()
    local GI = UEHelpers.GetGameInstance()
    if not GI:IsValid() then print("[MySaveTest] GI invalid") return end

    local saveObj = GI.SaveGameObject
    print("[MySaveTest] SaveGameObject: " .. tostring(saveObj))

    -- Try to serialize to local slot using UGameplayStatics
    local ok, err = pcall(function()
        -- This writes a proper UE4 binary .sav file to:
        -- D:\steam\steamapps\common\Naruto To Boruto\Saved\SaveGames\NarutoBackup.sav
        local result = UEHelpers.GetGameplayStatics():SaveGameToSlot(saveObj, "dumped_save", 0)
        print("[MySaveTest] SaveGameToSlot result: " .. tostring(result))
    end)
    if not ok then print("[MySaveTest] Error: " .. tostring(err)) end
end)

RegisterKeyBind(Key.F6, function()
    -- Load from local .sav back into memory
    local GI = UEHelpers.GetGameInstance()
    if not GI:IsValid() then return end

    local ok, err = pcall(function()
        local GS = UEHelpers.GetGameplayStatics()
        -- Check if our backup exists
        local exists = GS:DoesSaveGameExist("dumped_save", 0)
        print("[MySaveTest] Backup exists: " .. tostring(exists))

        if exists then
            -- Load it back
            local loadedSave = GS:LoadGameFromSlot("dumped_save", 0)
            print("[MySaveTest] Loaded: " .. tostring(loadedSave))
            if loadedSave and loadedSave:IsValid() then
                -- Push it back to Steam Cloud via SetSaveDataForSteam
                GI:SetSaveDataForSteam(loadedSave)
                print("[MySaveTest] Pushed to Steam!")
            end
        end
    end)
    if not ok then print("[MySaveTest] Error: " .. tostring(err)) end
end)

print("[MySaveTest] Ready - F5=Download to .sav, F6=Upload from .sav")