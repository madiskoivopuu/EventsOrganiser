import { useRef, useState } from "react";
import { IoIosArrowDown } from "react-icons/io";

import {EventAccordionEditableHeader, EventAccordionHeader, EventDetailColumn} from "./Fragments";
import { StyledSelect } from '@/components';
import { EventDetails, EventTag } from "@/interfaces/global_interfaces";
import { EditableEventDetails } from "./interfaces";
import * as helpers from "./helpers";
import { useEventsStore } from "@/hooks";

import "./event-accordion.scss";
import "./date.scss";

interface EventAccordionProps {
	event: EventDetails,
	allTags: EventTag[]
}

function EventAccordion({ event, allTags }: EventAccordionProps) {
	const [editableEvent, setEditableEvent] = useState<EditableEventDetails>(helpers.createEditableEventObject(event));
	const [isBeingEdited, setIsBeingEdited] = useState<boolean>(false);
	const modalRef = useRef<HTMLDialogElement | null>(null);

	const { addOrUpdate, deleteEvents } = useEventsStore();

	const setKeyOfEditableEvent = <K extends keyof EditableEventDetails>(key: K, value: EditableEventDetails[K]) => {
		setEditableEvent(prev => ({
				...prev,
				[key]: value
			})
		);
	}

	const saveEventChanges = () => {
		// TODO: request to server

		setIsBeingEdited(false);
		let updatedEvent = helpers.editableEventToEventDetails(event, editableEvent);
		addOrUpdate([updatedEvent]);
	}

	const deleteEventChanges = () => {
		// TODO: request to server

		modalRef.current?.close();
		deleteEvents([event]);
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

	let errorsList: JSX.Element[] = formErrors.map(text => <span style={{color: "red"}}>{text}</span>);
	return (
		<>
			<details className="event-accordion">
				<summary className="event-accordion-header">
					{isBeingEdited 
						? <EventAccordionEditableHeader event={editableEvent} setKeyOfEditableEvent={setKeyOfEditableEvent}/> 
						: <EventAccordionHeader event={event} /> }
		
					<div className="dd-icon-container">
						<IoIosArrowDown className="dd-icon" />
					</div>
				</summary>

				<div className="event-accordion-body">
					<div className="event-details">
						<EventDetailColumn 
							header={"Start time"} 
							text={isBeingEdited 
									? <input type="time" value={editableEvent.start_time || ""} onChange={(e) => setKeyOfEditableEvent("start_time", e.target.value)} /> 
									: helpers.format8601TimestampToTime(event.start_date)} 
						/>
						<EventDetailColumn 
							header={"End time"} 
							text={isBeingEdited 
									? <input type="time" value={editableEvent.end_time || ""} onChange={(e) => setKeyOfEditableEvent("end_time", e.target.value)} required /> 
									: helpers.format8601TimestampToTime(event.end_date)}
						/>
						<EventDetailColumn 
							header={"Venue"} 
							text={isBeingEdited 
									? <input type="text" value={editableEvent.address} onChange={(e) => setKeyOfEditableEvent("address", e.target.value)}/> 
									: event.address} 
						/>
						<EventDetailColumn 
							header={"Event categories"} 
							text={isBeingEdited
									? <StyledSelect
										options={allTags}
										defaultValue={editableEvent.tags}

										menuPortalTarget={document.body}
										menuPosition={'fixed'} 

										isMulti
										isSearchable
										getOptionLabel={tag => tag.name}
										getOptionValue={tag => tag.id.toString()}
										onChange={(newValues) => setKeyOfEditableEvent("tags", newValues as EventTag[])}
									/>
									: helpers.formatTags(event)}
						/>
					</div>
					<div className="event-buttons-container">
						<div className="event-buttons">
							{eventButtons}
						</div>
					</div>
				</div>
				{isBeingEdited 
					? <div style={{padding: "0.25rem", display: "flex", flexDirection: "column"}}>{errorsList}</div> 
					: <></> }
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