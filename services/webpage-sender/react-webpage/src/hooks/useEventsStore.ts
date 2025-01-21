import { EventDetails } from "@/interfaces/global_interfaces";
import { create } from "zustand";

interface EventsState {
    events: EventDetails[],
    addOrUpdate: (events: EventDetails[]) => void,
    deleteEvents: (events: EventDetails[]) => void
}

function addOrUpdateEvents(prevEvents: EventDetails[], newEvents: EventDetails[]) {
    let idToEvent = new Map(prevEvents.map(event => [event.id, event]));

    newEvents.forEach(event => idToEvent.set(event.id, event));

    return [ ...idToEvent.values() ];
}

function deleteEvents(prevEvents: EventDetails[], removeEvents: EventDetails[]) {
    let removableEventIds: Set<number> = new Set(removeEvents.map(event => event.id));

    return prevEvents.filter(event => !removableEventIds.has(event.id));
}

const useEventsStore = create<EventsState>((set) => ({
    events: [],

    addOrUpdate: (newEvents: EventDetails[]) => {
        set((state) => ({
                events: addOrUpdateEvents(state.events, newEvents)
            })
        );
    },
    deleteEvents: (removeEvents: EventDetails[]) => {
        set((state) => ({
                events: deleteEvents(state.events, removeEvents)
            })
        );
    }
}));

export default useEventsStore;