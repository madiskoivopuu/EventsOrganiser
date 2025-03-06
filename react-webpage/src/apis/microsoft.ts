import { AccountSettings } from "@/interfaces/global_interfaces";

export function getMicrosoftAccountSettings(): Promise<AccountSettings> {
    return fetch(`${import.meta.env.VITE__DOMAIN_URL}/api/microsoft/settings`, {
        method: "GET",
        credentials: import.meta.env.VITE__CREDENTIALS_SETTING
    }).then((resp) => resp.json()
    ).then(resp => {
        return resp as AccountSettings;
    })
}

export function updateMicrosoftAccountSettings(newSettings: AccountSettings) {
    return fetch(`${import.meta.env.VITE__DOMAIN_URL}/api/microsoft/settings`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(newSettings),
        credentials: import.meta.env.VITE__CREDENTIALS_SETTING
    }).then(_ => {
        return;
    })
}