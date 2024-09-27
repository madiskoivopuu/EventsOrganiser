import { useEffect, useState } from 'react';

import Stack from 'react-bootstrap/Stack';
import Card from 'react-bootstrap/Card';
import Form from 'react-bootstrap/Form';
import InputGroup from 'react-bootstrap/InputGroup';
import DatePicker from "react-datepicker";

import Select from 'react-select';

import "react-datepicker/dist/react-datepicker.css";
import 'bootstrap-icons/font/bootstrap-icons.css';

function SearchBar({ tags, searchFiltersChanged }) {
    const [useExtraOpts, setUseExtraOpts] = useState(false);
    const [startDate, setStartDate] = useState(null);
    const [endDate, setEndDate] = useState(null);

    const onExtraOpsChecked = (e) => {
        searchFiltersChanged("additionalOptsEnabled", e.target.checked);
        setUseExtraOpts(e.target.checked);
    }

    const onStartDateSelected = (date) => {
        if(date !== null) {
            var diffInSec = (new Date().getTime() - date.getTime()) / 1000;
            if(diffInSec <= 1) // <DatePicker> gives us almost the current time when the user clicks enter, but we do not care about the time it gives
                date.setHours(0,0,0,0);
        }

        searchFiltersChanged("startDate", date);
        setStartDate(date);
    }

    const onEndDateSelected = (date) => {
        if(date !== null) {
            var diffInSec = (new Date().getTime() - date.getTime()) / 1000;
            if(diffInSec <= 1) // <DatePicker> gives us almost the current time when the user clicks enter, but we do not care about the time it gives
                date.setHours(0,0,0,0);
        }

        setEndDate(date);
        searchFiltersChanged("endDate", date);
    }

    const onSelectedTagsChanged = (e) => {
        let tags = Array.from(e, option => option.value);
        searchFiltersChanged("tags", tags);
    };

    const optionsForSelect = Array.from(tags, (tag) => ({ value: tag, label: tag }) );

    return (
        <Card>
            <Card.Body>
                <Card.Title>Filter listed events</Card.Title>
                <hr />

                <InputGroup className="mb-3">
                    <Form.Control type="search" placeholder="Event name or Description" />
                    <InputGroup.Text onChange={(e) => searchFiltersChanged("query", e.target.value) }>
                        <i class="bi bi-search"></i>
                    </InputGroup.Text>
                </InputGroup>

                <Form.Check type="checkbox" label="Use extra search options" onChange={onExtraOpsChecked} />

                <fieldset disabled={!useExtraOpts}>
                    <Form.Group className="mb-3">
                        <Form.Label>Start Date</Form.Label> <br />
                        <DatePicker className="form-control" selected={startDate} onChange={onStartDateSelected}/>
                    </Form.Group>

                    <Form.Group className="mb-3">
                        <Form.Label>End Date</Form.Label> <br />
                        <DatePicker className="form-control" selected={endDate} onChange={onEndDateSelected} />
                    </Form.Group>

                    <Form.Group>
                        <Form.Label>Tags</Form.Label> <br />
                        <Select className="testos" isMulti isDisabled={!useExtraOpts} options={optionsForSelect} onChange={onSelectedTagsChanged}>
                        </Select>
                    </Form.Group>
                </fieldset>

            </Card.Body>
        </Card>
    );
}

export default SearchBar;