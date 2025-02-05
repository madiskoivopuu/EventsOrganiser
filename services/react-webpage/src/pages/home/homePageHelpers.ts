import { EventDetails, ActiveTab } from "@/interfaces/global_interfaces";
import { SearchOptions } from "./components";

export const __events: EventDetails[] = [
    {
        id: 1,
        event_name: "TEST event",
        start_date: "2025-01-01T07:00:00Z",
        end_date: "2025-01-01T22:00:00Z",
        address: "Estonia, Tartu, Raekoja plats",
        tags: [
            {id: 1, name: "Computer Science"},
            {id: 2, name: "Wowe2"},
            {id: 3, name: "Wowe3"},
            {id: 4, name: "Wowe4"},
            {id: 5, name: "Wowe5"},
        ]
    },
    {
        id: 2,
        event_name: "School meeting",
        start_date: "2025-04-01T07:00:00Z",
        end_date: "2025-04-07T22:00:00Z",
        address: "Estonia, Tartu, Raekoja plats",
        tags: [
            {id: 1, name: "Wowe1"},
            {id: 2, name: "Wowe2"},
            {id: 3, name: "Wowe3"},
            {id: 4, name: "Wowe4"},
            {id: 5, name: "Wowe5"},
        ]
    },
    {
        id: 3,
        event_name: "Deadline",
        start_date: "",
        end_date: "2025-04-06T22:00:00Z",
        address: "Estonia, Tartu, Raekoja plats",
        tags: [
            {id: 1, name: "Deadline"},
        ]
    },
    {
        id: 4,
        event_name: "Deadline",
        start_date: "",
        end_date: "2022-04-06T22:00:00Z",
        address: "Estonia, Tartu, Raekoja plats",
        tags: [
            {id: 1, name: "Deadline"},
        ]
    },
    {
        id: 5,
        event_name: "Deadline",
        start_date: "",
        end_date: "2027-04-06T22:00:00Z",
        address: "Estonia, Tartu, Raekoja plats",
        tags: [
            {id: 1, name: "Deadline"},
        ]
    },
    {
        id: 6,
        event_name: "Deadline",
        start_date: "",
        end_date: "2027-04-07T22:00:00Z",
        address: "Estonia, Tartu, Raekoja plats",
        tags: [
            {id: 1, name: "Deadline"},
        ]
    },
    {
        id: 7,
        event_name: "Deadline",
        start_date: "",
        end_date: "2027-04-08T22:00:00Z",
        address: "Estonia, Tartu, Raekoja plats",
        tags: [
            {id: 1, name: "Deadline"},
        ]
    },
]

export const filterEventsForTab = (events: EventDetails[], showEvtType: ActiveTab) => {
    let filtered: EventDetails[] = [];
    const currDate = new Date();

    switch(showEvtType) {
        case ActiveTab.PAST: {
            filtered = events.filter((event) => new Date(event.end_date) < currDate);
            break;
        }
        case ActiveTab.ONGOING: {
            filtered = events.filter((event) => currDate <= new Date(event.end_date) && (!event.start_date || new Date(event.start_date) <= currDate));
            break;
        }
        case ActiveTab.UPCOMING: {
            filtered = events.filter((event) => (event.start_date && currDate < new Date(event.start_date)) || (event.end_date && currDate < new Date(event.end_date)));
            break;
        }
    }

    return filtered;
};

export const applySearchQuery = (events: EventDetails[], searchOptions: SearchOptions): EventDetails[] => {
    if(searchOptions.eventName && searchOptions.eventName?.length > 1)
        events = events.filter((event) => event.event_name.toLowerCase().includes(searchOptions.eventName!.toLowerCase()) );
    
    if(searchOptions.startDate)
        events = events.filter((event) => event.start_date && new Date(event.start_date) >= searchOptions.startDate!); // TODO: fix possible bug with events that have no start date

    if(searchOptions.endDate)
        events = events.filter((event) => event.end_date && new Date(event.end_date) <= searchOptions.endDate!);

    if(searchOptions.tags && searchOptions.tags.length > 0)
        events = events.filter((event) => {
            let eventTagIds: Set<number> = new Set(event.tags.map(tag => tag.id));

            return searchOptions.tags!.map(tag => tag.id).every(tagId => eventTagIds.has(tagId))
        });

    return events;
}