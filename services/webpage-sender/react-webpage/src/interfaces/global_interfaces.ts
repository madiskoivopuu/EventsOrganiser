export interface EventDetails {
    id: number,
    event_name: string,
    start_date: string | null,
    end_date: string | null,
    country: string,
    city: string,
    address: string,
    room: string,
    tags: EventTag[]
}

export interface EventTag {
    id: number,
    name: string
}