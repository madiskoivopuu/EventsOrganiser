const template = document.createElement("template");
template.innerHTML = `
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>

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
                    <option value="2">Second</option>
                </select>
                <div class="invalid-feedback">Please select a valid tag.</div>
            </div>
        </fieldset>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
<script src="https://unpkg.com/gijgo@1.9.14/js/gijgo.min.js" type="text/javascript"></script>
<script type="module">
    import Tags from "https://cdn.jsdelivr.net/gh/lekoala/bootstrap5-tags@master/tags.js";
    Tags.init("#tagsField");
</script>
<script defer>
    $('#startDate').datepicker({
        uiLibrary: 'bootstrap5'
    });

    $('#endDate').datepicker({
        uiLibrary: 'bootstrap5'
    });
</script>
`;

const scripts = [

]

class SearchSidebar extends HTMLElement {
    constructor() {
        super();

        const shadow = this.attachShadow({ mode: "open" });
        shadow.appendChild(document.importNode(template.content, true)); //template.content.cloneNode(true));
    }

    get #scripts() {
        return this.shadowRoot.querySelectorAll('script');
    }
      
    #scopedEval = (script) => 
        Function(script).bind(this.shadowRoot)();
      
    #processScripts() {
        this.#scripts.forEach(
            s => this.#scopedEval(s.innerHTML)
        );
    }

    connectedCallback() {
        this.shadowRoot.getElementById("enableAdvancedSearch").addEventListener('change', enableAdvancedSearchChanged);
        this.#processScripts();
    }
}

function enableAdvancedSearchChanged() {
    const searchFields = this.shadowRoot.getElementById("searchExtraOpts");
    if(this.checked)
        searchFields.removeAttr("disabled");
    else
        searchFields.setAttribute("disabled", "");
}

window.customElements.define("search-sidebar", SearchSidebar);