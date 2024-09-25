const template = document.createElement("template");
template.innerHTML = `
<div class="card card-body">
    <div class="input-group mb-3">
        <input class="form-control" type="search" placeholder="Search..." aria-label="Search">
        <button class="btn btn-secondary" type="button">
            <i class="fa fa-search">ICON</i>
        </button>
    </div>

    <div class="row">
        <div class="col-12">
            <div class="form-check mb-3">
                <input class="form-check-input" type="checkbox" value="" id="enableAdvancedSearch">
                <label class="form-check-label" for="enableAdvancedSearch">Use extra search options</label>
            </div>
        </div>

        <fieldset id="searchExtraOpts">
            <div class="col-12">
                <label for="startDate" class="form-label">Start Date</label>
                <input id="startDate">
            </div>
            <div class="col-12">
                <label for="endDate" class="form-label">End Date</label>
                <input id="endDate">
            </div>
            <div class="col-12">
                <label for="tagsField" class="form-label">Includes tags</label>
                <select class="form-select" id="tagsField" multiple>
                    <option disabled hidden value="">Choose a tag...</option>
                    <option value="1">First</option>
                </select>
                <div class="invalid-feedback">Please select a valid tag.</div>
            </div>
        </fieldset>
    </div>
</div>
`;

class SearchSidebar extends HTMLElement {
    constructor() {
        super();
    }

    connectedCallback() {
        const shadow = this.attachShadow({ mode: "open" })
    }
}

window.customElements.define("search-sidebar", SearchSidebar);