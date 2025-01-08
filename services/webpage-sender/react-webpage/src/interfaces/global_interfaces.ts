export interface EventDetails {
    id: number,
    event_name: string,
    start_date: string | null,
    end_date: string | null,
    address: string,
    tags: EventTag[]
}

export interface EventTag {
    id: number,
    name: string
}