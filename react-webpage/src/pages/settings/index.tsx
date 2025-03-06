import { useState } from "react";
import TimezoneSelect, { ITimezoneOption } from "react-timezone-select";
import Select from "react-select";


import { EventTag, Settings } from "@/interfaces/global_interfaces";
import { useAccountDataStore, useEventsStore } from "@/hooks";
import { SettingRow } from "./components";

import "./settings.css";
import * as settingHelpers from "./setting-helpers";

export default function SettingsPage() {
    const { settings, updateSettings } = useAccountDataStore();
    const { tags } = useEventsStore();
    const [changedSettings, setChangedSettings] = useState<Partial<Settings>>(settings);

    const updateTimezone = (tz: ITimezoneOption) => {
        setChangedSettings((state) => ({
            ...state,
            accountSettings: {
                ...state.accountSettings!,
                timezone: tz.value
            }
        }))
    }

    const updateAutoFetch = (value: boolean) => {
        setChangedSettings((state) => ({
            ...state,
            accountSettings: {
                ...state.accountSettings!,
                auto_fetch_emails: value
            }
        }))
    }

    const updateParseableEventCats = (categories: EventTag[]) => {
        setChangedSettings((state) => ({
            ...state,
            eventSettings: {
                ...state.eventSettings!,
                categories: categories
            }
        }))
    }

    useEffect(() => {

    }, []);

    return (
        <>
            <div className="settings-page-header">
                <h1 style={{margin: "0"}}>Settings</h1>
            </div>

            <div style={{padding: "1rem"}}>
                <hr className="settings-cat-divider"/>

                <SettingRow
                    settingName="Event timezone"
                    description="Dates found in events will be given this timezone.
                                 This setting only applies if the e-mail does not mention what timezone the events take place in."
                >
                    <TimezoneSelect 
                        isDisabled={!settings.accountSettings}
                        value={changedSettings.accountSettings?.timezone || ""}
                        onChange={updateTimezone}
                    />
                </SettingRow>

                <hr className="settings-cat-divider"/>
                <SettingRow
                    settingName="Auto-fetch emails"
                    description="Makes the event parser automatically read new emails and find events in them."
                >
                    <div>
                        <input 
                            type="checkbox" 
                            id="autofetchemails" 
                            name="autofetchemails" 

                            disabled={!settings.accountSettings}
                            checked={changedSettings.accountSettings?.auto_fetch_emails}
                            onChange={e => updateAutoFetch(e.target.checked)}
                        />
                        <label htmlFor="autofetchemails">Enabled</label>
                    </div>
                </SettingRow>

                <hr className="settings-cat-divider"/>
                <SettingRow
                    settingName="Event categories"
                    description="Only parse events from emails that can be associated with these categories."
                >
                    <Select
                        options={tags}
                        isMulti
                        isSearchable
                        getOptionLabel={tag => tag.name}
                        getOptionValue={tag => tag.id.toString()}

                        value={changedSettings.eventSettings?.categories}
                        isDisabled={!settings.eventSettings}
                        onChange={(newCategories) => updateParseableEventCats(newCategories as EventTag[])}
                    />
                    <div style={{display: "inline-flex"}}>
                        <button
                            onClick={() => updateParseableEventCats(tags)}
                        >
                            Select all
                        </button>
                        <button 
                            className="warning"
                            onClick={() => updateParseableEventCats([])}
                        >
                            Deselect all
                        </button>
                    </div>
                </SettingRow>

                <hr className="settings-cat-divider"/>

                <button
                    disabled={settingHelpers.areSettingsFullyLoaded(settings)}
                >
                    Save settings
                </button>
            </div>
        </>
    );
}