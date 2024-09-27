import { useEffect, useState } from 'react';

import Stack from 'react-bootstrap/Stack';
import Card from 'react-bootstrap/Card';
import Form from 'react-bootstrap/Form';
import InputGroup from 'react-bootstrap/InputGroup';
import DatePicker from "react-datepicker";
import Tags from "bootstrap5-tags/tags";


import "./SearchBar.css";
import "react-datepicker/dist/react-datepicker.css";
import 'bootstrap-icons/font/bootstrap-icons.css';

function SearchBar({ tags, searchFiltersChanged }) {
    const [useExtraOpts, setUseExtraOpts] = useState(false);
    const [startDate, setStartDate] = useState(null);
    const [endDate, setEndDate] = useState(null);
    const [selectedTags, setSelectedTags] = useState(null);
    
    useEffect(() => { // runs select to tagslist conversion after each render
        Tags.init("select[multiple]", {}, true);
    });

    const onSelectedTagsChanged = (e) => {
        let tags = Array.from(e.target.selectedOptions, option => option.value);
        searchFiltersChanged("tags", tags);
    };

    return (
        <Card>
            <Card.Body>
                <Card.Title>Filter listed events</Card.Title>
                <hr />

                <InputGroup className="mb-3">
                    <Form.Control type="search" placeholder="Event name or Description" />
                    <InputGroup.Text>
                        <i class="bi bi-search"></i>
                    </InputGroup.Text>
                </InputGroup>

                <Form.Check type="checkbox" label="Use extra search options" onChange={(e) => setUseExtraOpts(e.target.checked)} />

                <fieldset disabled={!useExtraOpts}>
                    <Form.Group className="mb-3">
                        <Form.Label>Start Date</Form.Label> <br />
                        <DatePicker className="form-control" />
                    </Form.Group>

                    <Form.Group className="mb-3">
                        <Form.Label>End Date</Form.Label> <br />
                        <DatePicker onChange={date => console.log(date)} className="form-control" />
                    </Form.Group>

                    <Form.Group>
                        <Form.Label>Tags</Form.Label> <br />
                        <Form.Select className="form-control" multiple data-allow-clear="true" disabled={!useExtraOpts} option={tags} onChange={onSelectedTagsChanged}>
                            {
                                tags.map(tag => <option value={tag}>{tag}</option>)
                            }
                        </Form.Select>
                    </Form.Group>
                </fieldset>

            </Card.Body>
        </Card>
    );
}

export default SearchBar;