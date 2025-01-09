import { useRef, useState } from "react";
import { IoIosArrowDown } from "react-icons/io";
import { IoCalendarClearOutline  } from "react-icons/io5";
import DatePicker from "react-datepicker";

import { InputWithIcon } from '@/components';
import { EventDetails } from "@/interfaces/global_interfaces";
import { EventType, EditableEventDetails } from "./helpers";
import * as helpers from "./helpers";

import "./event-accordion.scss";
import "./date.scss";

interface TimeFragmentProps {
    header: string,
    text: JSX.Element | string | null
}

function EventDetailFragment({ header, text }: TimeFragmentProps) {
    let displayedText: JSX.Element | string = text ? text : "N/A";

    return (
        <div className="event-detailed-info">
            <h3>{header}</h3>
            <span>{displayedText}</span>
        </div>
    )
}

interface DateFragmentProps {
    date: string | null,
    threeDots?: boolean
}

function DateFragment({ threeDots, date }: DateFragmentProps) {
    if(!date) 
        return null;
    
    let dayNr: string = new Date(date).toLocaleString("default", { day: "2-digit" });
    let monthShort: string = new Date(date).toLocaleString("default", { month: "short" }).toUpperCase();
    
    if(threeDots) {
        dayNr = "...";
        monthShort = " ";
    }
        
    return (
        <div className="event-date">
            <h2>{dayNr}</h2>
            <span>{monthShort}</span>
        </div>
    );
}

interface ElementProps {
    event: EventDetails,
    deleteEvent?: (event: EventDetails) => void,
    updateEvent?: (newEvent: EventDetails) => void,
};

interface EditableElementProps {
    event: EditableEventDetails,
    setKeyOfEditableEvent: <K extends keyof EditableEventDetails>(key: K, value: EditableEventDetails[K]) => void
}

function EventDateDisplay({ event }: ElementProps) {
    if(!event.start_date && !event.end_date) {
        console.error("Invalid event start & end date for: ", event);
        return null;
    }


    let startDateElement: JSX.Element | null = null; //event.start_date ? <DateFragment date={event.start_date} /> : null;
    let endDateElement: JSX.Element | null = null; //event.end_date ? <DateFragment date={event.end_date} /> : null;

    switch(helpers.getEventType(event)) {
        case EventType.DEADLINE: {
            startDateElement = <DateFragment threeDots={true} date={"-"} />
            endDateElement = <DateFragment date={event.end_date} />;
            break;
        }
        case EventType.SINGLEDAY: {
            startDateElement = <DateFragment date={event.start_date} />
            break;
        }
        case EventType.MULTIDAY: {
            startDateElement = <DateFragment date={event.start_date} />
            endDateElement = <DateFragment date={event.end_date} />;
        }
    }

    let lineBetweenDates = startDateElement && endDateElement ? <hr/> : null;

    return (
        <>
            {startDateElement}
            {lineBetweenDates}
            {endDateElement}
        </>
    )
}

function EditableEventHeaderDisplay({ event, setKeyOfEditableEvent }: EditableElementProps) {
    return (
        <div style={{display: "flex", flexFlow: "wrap", alignItems: "center"}}>
            <DatePicker 
                selected={event.start_date}
                onChange={newDate => setKeyOfEditableEvent("start_date", newDate)}

				formatWeekDay={name => name.substring(0, 1)} 
                placeholderText="DD/MM/YYYY"
				customInput={
					<InputWithIcon className="search-bar" type="text">
						<IoCalendarClearOutline className="icon" />
					</InputWithIcon>
				}
			/>
            <h3 style={{margin: "0.5rem"}}>to</h3>
            <DatePicker 
                selected={event.end_date}
                onChange={newDate => setKeyOfEditableEvent("end_date", newDate)}

				formatWeekDay={name => name.substring(0, 1)} 
                placeholderText="DD/MM/YYYY"
				customInput={
					<InputWithIcon className="search-bar" type="text">
						<IoCalendarClearOutline className="icon" />
					</InputWithIcon>
				}
			/>

            <input type="text" placeholder="Event name" value={event.event_name} onChange={(e) => setKeyOfEditableEvent("event_name", e.target.value)} />
        </div>
    );
}

function EventHeaderDisplay({ event }: ElementProps) {
    return (
        <>
            <div className="event-date-container">
                <EventDateDisplay event={event} />
            </div>

            <div className="event-name">
                <h2>{event.event_name}</h2>
            </div>
        </>
    )
}

function EventAccordion({ event, updateEvent, deleteEvent }: ElementProps) {
    const [editableEvent, setEditableEvent] = useState<EditableEventDetails>(helpers.createEditableEventObject(event));
    const [isBeingEdited, setIsBeingEdited] = useState<boolean>(false);
    const modalRef = useRef<HTMLDialogElement | null>(null);

    const setKeyOfEditableEvent = <K extends keyof EditableEventDetails>(key: K, value: EditableEventDetails[K]) => {
        setEditableEvent(prev => ({
                ...prev,
                [key]: value
            })
        );
    }

    const saveEventChanges = () => {
        // TODO: request to server

        setIsBeingEdited(true);

        // TODO: parent callback
        // updateEvent(newEvent)
    }

    const deleteEventChanges = () => {
        // TODO: request to server

        modalRef.current?.close();

        // TODO: parent callback
        // deleteEvent(event)
    }

    let formErrors = helpers.validateEditableEvent(editableEvent);
    let eventButtons: JSX.Element = <></>;
    if(isBeingEdited) {
        eventButtons = (
            <>
                <button disabled={formErrors.length !== 0} onClick={saveEventChanges}>Save</button>
                <button className="warning" onClick={() => setIsBeingEdited(false)}>Cancel</button>
            </>
        );
    } else {
        eventButtons = (
            <>
                <button onClick={() => setIsBeingEdited(true)}>Edit</button>
                <button className="warning" onClick={() => modalRef.current?.showModal()}>Delete</button>
            </>
        );
    }

    let errorText: JSX.Element[] = formErrors.map(text => <span style={{color: "red"}}>{text}</span>);
    return (
        <>
            <details className="event-accordion">
                <summary className="event-accordion-header">
                    {isBeingEdited ? <EditableEventHeaderDisplay event={editableEvent} setKeyOfEditableEvent={setKeyOfEditableEvent}/> : <EventHeaderDisplay event={event} /> }
        
                    <div className="dd-icon-container">
                        <IoIosArrowDown className="dd-icon" />
                    </div>
                </summary>

                <div className="event-accordion-body">
                    <div className="event-details">
                        <EventDetailFragment 
                            header={"Start time"} 
                            text={isBeingEdited ? <input type="time" value={editableEvent.start_time || ""} onChange={(e) => setKeyOfEditableEvent("start_time", e.target.value)} /> : helpers.format8601TimestampToTime(event.start_date)} 
                        />
                        <EventDetailFragment 
                            header={"End time"} 
                            text={isBeingEdited ? <input type="time" value={editableEvent.end_time || ""} onChange={(e) => setKeyOfEditableEvent("end_time", e.target.value)} /> : helpers.format8601TimestampToTime(event.end_date)}
                        />
                        <EventDetailFragment 
                            header={"Venue"} 
                            text={isBeingEdited ? <input type="text" value={editableEvent.address} onChange={(e) => setKeyOfEditableEvent("address", e.target.value)}/> : event.address} 
                        />
                        <EventDetailFragment 
                            header={"Event categories"} 
                            text={helpers.formatTags(event)} // TODO: make tags editable
                        />
                    </div>
                    <div className="event-buttons-container">
                        <div className="event-buttons">
                            {eventButtons}
                        </div>
                    </div>
                </div>
                {isBeingEdited ? <div style={{padding: "0.25rem"}}>{errorText}</div> : <></>}
            </details>

            <dialog ref={modalRef}>
                <h2>Delete confirmation</h2>
                <p>Are you sure you want to delete <b>{event.event_name}</b>?</p>

                <div style={{display: "flex", justifyContent: "flex-end"}}>
                    <button className="plain" onClick={() => modalRef.current?.close()}>Cancel</button>
                    <button className="warning" onClick={deleteEventChanges}>Delete</button>
                </div>
            </dialog>
        </>
    )
}

export default EventAccordion;