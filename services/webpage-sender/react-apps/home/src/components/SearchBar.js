import { useEffect, useState } from 'react';

import Card from 'react-bootstrap/Card';
import Form from 'react-bootstrap/Form';
import InputGroup from 'react-bootstrap/InputGroup';
import DatePicker from "react-datepicker";
import Tags from "bootstrap5-tags/tags";

import "react-datepicker/dist/react-datepicker.css";
import 'bootstrap-icons/font/bootstrap-icons.css';

function SearchBar({ searchFiltersChanged }) {
    useEffect(() => { // runs select to tagslist conversion after render
        Tags.init();
    });

    const [useExtraOpts, setUseExtraOpts] = useState(false);

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
                        <DatePicker className="form-control" />
                    </Form.Group>

                    <Form.Group>
                        <Form.Label>Tags</Form.Label> <br />
                        <Form.Select className="form-control" multiple data-allow-clear="true">
                            <option disabled hidden value="">Choose a tag...</option>
                            <option value="1">First</option>
                            <option value="2">Second</option>
                        </Form.Select>
                    </Form.Group>
                </fieldset>

            </Card.Body>
        </Card>
    );
}

export default SearchBar;