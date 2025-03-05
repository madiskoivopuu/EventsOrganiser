import { AccountSettings } from "@/interfaces/global_interfaces";
import { create } from "zustand";

interface AccountData {
    authenticated: boolean,
    settings: AccountSettings | null,

    setAuthenticated: (val: boolean) => void;
    updateSettings: (newSettings: AccountSettings) => void;
}

const useAccountDataStore = create<AccountData>((set) => ({
    authenticated: false,
    settings: null,
    
    setAuthenticated: (val) => {
        set((state) => ({
            ...state,
            authenticated: val,
        }));
    },
    updateSettings: (newSettings) => {
        set((state) => ({
            ...state,
            settings: newSettings,
        }));
    }
}));

export default useAccountDataStore;