import { EventDetails, EventTag } from "@/interfaces/global_interfaces.ts";

export type EventFetchDirection = "forward" | "backward";

export interface EventsGetResponse {
    items: EventDetails[],
    total: number,
    page: number,
    size: number,
    pages: number,
}

export function getTags(): Promise<EventTag[]> {
    return fetch(`${import.meta.env.VITE__DOMAIN_URL}/api/events/tags`, {
        credentials: import.meta.env.VITE__CREDENTIALS_SETTING
    }).then((resp) => resp.json()
    ).then(resp => {
        return resp as EventTag[]
    })
}

export function getEvents(
    direction: EventFetchDirection,
    from_time: string, // ISO8601 date
    page: number = 1,
): Promise<EventsGetResponse> {
    var url = new URL(`${import.meta.env.VITE__DOMAIN_URL}/api/events`);
    url.searchParams.append("direction", direction);
    url.searchParams.append("from_time", from_time);
    url.searchParams.append("page", page.toString());

    return fetch(url, {
        credentials: import.meta.env.VITE__CREDENTIALS_SETTING
    }).then((resp) => resp.json()
    ).then(resp => {
        return resp as EventsGetResponse;
    })
}

export function updateEvent(event: EventDetails) {
    return fetch(`${import.meta.env.VITE__DOMAIN_URL}/api/events/${event.id}`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ ...event }),
        credentials: import.meta.env.VITE__CREDENTIALS_SETTING
    }).then((_) => {
        return;
    })
}

export function deleteEvent(event: EventDetails) {
    return fetch(`${import.meta.env.VITE__DOMAIN_URL}/api/events/${event.id}`, {
        method: "DELETE",
        credentials: import.meta.env.VITE__CREDENTIALS_SETTING
    }).then((_) => {
        return;
    })
}