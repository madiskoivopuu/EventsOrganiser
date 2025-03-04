import { ActiveTab } from "@/interfaces/global_interfaces";
import { create } from "zustand";

interface TabPage {
    currPage: number,
    maxPages: number,
    //error?: string
}

type TabsPagination = {
    [key in ActiveTab]: TabPage
}

interface PaginationState extends TabsPagination {
    a: () => void;
}

const useEventPagination = create<PaginationState>((set) => ({
    [ActiveTab.PAST]: {
        currPage: 1,
        maxPages: Number.MAX_SAFE_INTEGER
    },
    [ActiveTab.ONGOING]: {
        currPage: 1,
        maxPages: 0
    },
    [ActiveTab.UPCOMING]: {
        currPage: 1,
        maxPages: Number.MAX_SAFE_INTEGER
    },
    a: () => {}
})
);

export default useEventPagination;