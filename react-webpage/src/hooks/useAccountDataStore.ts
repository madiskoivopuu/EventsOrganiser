import { EventDetails } from "@/interfaces/global_interfaces";
import { create } from "zustand";

interface AccountData {
    authenticated: boolean,
    settings: AccountSettings | null,
}

interface AccountSettings {
    auto_fetch_emails: boolean,
    timezone: string // IANA timezone
    // tags...
}

const useAccountDataStore = create<AccountData>((set) => ({
    authenticated: false,
    settings: null
}));

export default useAccountDataStore;