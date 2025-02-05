export interface EventDetails {
    id: number,
    event_name: string,
    start_date: string | null,
    end_date: string,
    address: string,
    tags: EventTag[]
}

export interface EventTag {
    id: number,
    name: string
}

export enum ActiveTab {
    PAST,
    ONGOING,
    UPCOMING,
}
