import { EventDetails, EventTag } from "@/interfaces/global_interfaces";

export const formatTags = (event: EventDetails) => {
    let tagNames: string[] = event.tags.map(tag => tag.name);
    return tagNames.join(", ");
}

export enum EventType {
    INVALID,
    DEADLINE,
    SINGLEDAY,
    MULTIDAY
};

export const getEventType = (event: EventDetails): EventType => {
    if(!event.start_date && !event.end_date)
        return EventType.INVALID;

    if(!event.start_date && event.end_date) 
        return EventType.DEADLINE;

    if(event.start_date && !event.end_date)
        return EventType.SINGLEDAY;

    // extra check to see if start and end date are within the same day
    let startDateObj: Date = new Date(event.start_date!);
    let endDateObj: Date = new Date(event.end_date!);
    if(startDateObj.getDate() === endDateObj.getDate())
        return EventType.SINGLEDAY;
    else
        return EventType.MULTIDAY;
}

export interface EditableEventDetails {
    event_name: string,
    address: string,
    start_date: Date | null,
    start_time: string | null,
    end_date: Date | null,
    end_time: string | null,
    tags: EventTag[]
};

export const createEditableEventObject = (event: EventDetails): EditableEventDetails => {
    return {
        event_name: event.event_name,
        address: event.address,
        start_date: event.start_date ? new Date(new Date(event.start_date).toDateString()) : null,
        start_time: format8601TimestampToTime(event.start_date),
        end_date: event.end_date ? new Date(new Date(event.end_date).toDateString()) : null,
        end_time: format8601TimestampToTime(event.end_date),
        tags: event.tags
    };
}

export const editableEventToEventDetails = (event: EditableEventDetails): EventDetails => {

}

export const format8601TimestampToTime = (utcDateTime: string | null): string | null => {
    if(!utcDateTime)
        return null;

    return new Date(utcDateTime).toLocaleString("default", { hour: "2-digit", minute: "2-digit" })
}

export const exactlyOneNull = (a: any, b: any): boolean => {
    return (!a) !== (!b);
}

export const validateEditableEvent = (event: EditableEventDetails): string[] => {
    let errors: string[] = [];
    if(!event.start_date && !event.start_time && !event.end_date && !event.end_time)
        errors.push("The event must have either a start date or an end date");

    if(exactlyOneNull(event.start_date, event.start_time))
        errors.push("Both start time and start date must be chosen");

    if(exactlyOneNull(event.end_date, event.end_time))
        errors.push("Both end time and end date must be chosen");

    return errors;
}