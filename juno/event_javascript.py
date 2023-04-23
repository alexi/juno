from .prompting_javascript import GET_ANSWER_CODE, GET_ERROR, GET_CONTEXT

BUTTON_HANDLERS = """

function addStyle(styleString) {
    const style = document.createElement('style');
    style.textContent = styleString;
    document.head.append(style);
}

addStyle(`
    .edit-btn {
        transition: color 0.3s ease;
        color: grey;
    }
    .edit-btn:hover {
        color: blue;
    }
    .edit-box-top {
        border-bottom: none!important;
        border-width: 2px!important;
        border-color: rgb(194, 194, 194)!important;
        margin-top: 4px!important;
        padding:11px!important;
    }
    .edit-box {
        background-color: rgb(245, 245, 245);
    }
    .edit-box-bottom {
        border-top: none!important;
        border-width: 2px!important;
        border-color: rgb(194, 194, 194)!important;
        margin-bottom: 4px!important;
        padding:11px!important;
    }
    div.cell.selected.edit-box:before, div.cell.selected.edit-box.jupyter-soft-selected:before {
        top: 3px;
        left: 3px;
        width: 5px;
        height: calc(100% -  6px);
    }
    
    .juno-button-container {
        display: flex;
        justify-content: space-between;
        width: fit-content;
        margin-top: 10px;
    }
    .juno-button-container.debug-container {
        margin-bottom: 10px;
    }

    .juno-button,
    .cancel-button {
        display: inline-block;
        font-size: 13px;
        font-weight: 600;
        text-align: center;
        text-decoration: none;
        padding: 7px 16px;
        border-radius: 2px;
        color: #ffffff;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);
    }

    .juno-button {
        background-color: #0d257e;
        color: #ffffff;
    }

    .cancel-button {
        background-color: #f8f8f8;
        color: #070707;
    }

    .juno-button:hover,
    .cancel-button:hover {
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
        transform: translateY(-1px);
    }

    .juno-button:active,
    .cancel-button:active {
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        transform: translateY(1px);
    }
    
    .juno-button:disabled,
    .cancel-button:disabled {
        background-color: #cccccc;
        color: #999999;
        cursor: not-allowed;
        box-shadow: none;
        opacity:0.75;
    }

    .juno-button:disabled:hover,
    .cancel-button:disabled:hover {
        transform: none;
    }
`);


function addEditButton(cell) {
    let buttonDiv = $('<div style="display:inline">', {class: 'edit'});
    let input_below_div = cell.element.find('.input_prompt');
    if(!input_below_div) {
        return;
    }
    input_below_div.css('display', 'inline-flex');
    input_below_div.css('align-items', 'center')
    input_below_div.css('height', '30px')
    let existing_button = cell.element.find('.edit-btn');
    if (!existing_button.length) {
        buttonDiv.html(
            '<button class="edit-btn" type="button" style="height:19px;width:26px;margin-right:5px;font-size:25px;margin-top:1px;border-width:0px;background-color:white;overflow:visible" onclick="window.openEditor(&#39;' + cell.cell_id + '&#39;)">✎</button>'
            );
        input_below_div.prepend(buttonDiv);
    }
    return cell;
}

function removeEditButton(cell) {
    console.log("removing edit button from cell " + cell)
    let existing_button = cell.element.find('.edit-btn');
    console.log("existing_button:", existing_button)
    if(existing_button.length){
        existing_button.remove();
    }
}

function addAcceptCancel(cell) {
    if (cell.element.find('.accept-cancel-container').length) {
        return cell
    }
    let row = $('<div>', {class: 'juno-button-container accept-cancel-container'});
    row.html(
            '<button type="button" class="juno-button accept-button" style="margin-left: 89px;" onclick="window.JunoEditZones.accept(&#39;' + cell.cell_id + '&#39;)">Accept</button>' +
            '<button type="button" class="cancel-button" style="margin-left: 5px;" onclick="window.JunoEditZones.cancel(&#39;' + cell.cell_id + '&#39;)">Cancel</button>'
    );    
    row.find('.accept-button').prop('disabled', true);
    cell.element.append(row);
    return cell;
}

function removeAcceptCancel(cell) {
    if(cell == null) {
        return;
    }
    let row = cell.element.find('.accept-cancel-container');
    if(row.length){
        row.remove();
    }
}

function enableAcceptButton(cell) {
    let existing_button = cell.element.find('.accept-button');
    if (!existing_button.length) {
        addEditButtons(cell);
    }
    existing_button = cell.element.find('.accept-button');
    if (!existing_button.length) { return }
    existing_button.prop('disabled', false);
}

function openEditor(cellId, debugging=false) {
    console.log("opening editor for cell " + cellId)
    console.log("edit zones:", window.JunoEditZones)
    let cell = Jupyter.notebook.get_cells().find(cell => cell.cell_id == cellId);
    window.JunoEditZones.createZone(cell, debugging);
}

function addFixButton(cell, i) {
    if (cell.element.find('.debug-container').length) {
        return cell
    }
    let row = $('<div>', {class: 'juno-button-container debug-container'});
    row.html(
            '<button type="button" class="juno-button debug-button" style="margin-left: 93px;" onclick="window.openEditor(&#39;' + cell.cell_id + '&#39;, true)">Debug</button>'
    );    
    cell.element.append(row);
    return cell;
}

function removeFixButton(cell) {
    if(cell == null) {
        return;
    }
    let row = cell.element.find('.debug-container');
    if(row.length){
        row.remove();
    }
}

function cellHasErrorOutput(cell) {
    console.log("checking cell:", cell.cell_id)
    if (!cell.output_area || ! cell.output_area.outputs) {
        console.log("cell-id:", cell.cell_id, "no outputs")
        return false;
    }
    // if any output has output_type === 'error', then the cell has an error
    for (const output of cell.output_area.outputs) {
        if (output.output_type === 'error') {
            return true;
        }
    }
    return false;
}

function cleanDebugButtons(addOnly) {    
    let cells = Jupyter.notebook.get_cells();
    for (let i = 0; i < cells.length; i++) {
        let cell = cells[i];
        console.log("cell:", cell)
        let shouldShowDebugButton = cellHasErrorOutput(cell) && !window.JunoEditZones.isEditCell(cell);
        if (shouldShowDebugButton ) {
            addFixButton(cell, i);
        }
        else if (!addOnly && !shouldShowDebugButton) {
            removeFixButton(cell);
        }
    }
}

function addEditButtons() {
    let cells = Jupyter.notebook.get_cells();
    for (let i = 0; i < cells.length; i++) {
        let cell = cells[i];
        if (cell.cell_type === 'code' && !window.JunoEditZones.isEditCell(cell)) {
            addEditButton(cell, i);
        }
    }
}

window.addEditButtons = addEditButtons;

class EditZone {
    constructor(cell, debugging) {
        this.cell = cell;
        this.editCells = [];
        this.accepted = false;
        this.debugging = debugging;
        this._init();
    }
    
    _init() {
        console.log("initializing edit zone for cell " + this.cell)
        removeEditButton(this.cell);
        if(this.debugging) {
            removeFixButton(this.cell);
        }
        this.cell.element.addClass('edit-box-top');
        this.cell.element.addClass('edit-box');
        this.addEditCell();
        this.showButtons();
    }
    
    addEditCell() {
        let cellIndex = this.editCells.length === 0 ? Jupyter.notebook.find_cell_index(this.cell) : Jupyter.notebook.find_cell_index(this.editCells[this.editCells.length - 1]);
        let newCell = Jupyter.notebook.insert_cell_below('code', cellIndex)
        newCell.element.addClass('edit-box-bottom');
        newCell.element.addClass('edit-box');
        this.editCells.push(newCell);
        if (!this.debugging) {
            newCell.set_text("%edit ");
            setTimeout(() => {
                console.log("selecting cell " + cellIndex + 1)
                Jupyter.notebook.select(cellIndex + 1);
                newCell.focus_editor()
                newCell.code_mirror.setCursor({line:0, ch: 6})
            }, 200);
        }
        else {
            newCell.set_text("%debug ");
            setTimeout(() => {
                let newCellIndex = Jupyter.notebook.find_cell_index(newCell);
                Jupyter.notebook.execute_cells([newCellIndex]);
            }, 10);
        }
    }
    
    close(accepted) {
        this.removeButtons();
        for (let i = 0; i < this.editCells.length; i++) {
            // get cell index from cell id
            let cellId = this.editCells[i].cell_id;
            let editCellIndex = Jupyter.notebook.get_cells().findIndex(cell => cell.cell_id == cellId);
            let originalCellIndex = editCellIndex - 1;

            if (accepted) { // if edit is accepted, delete original and replace with the edit cell
                Jupyter.notebook.delete_cell(originalCellIndex);
                this.cell = Jupyter.notebook.get_cell(originalCellIndex);
            }
            else {
                Jupyter.notebook.delete_cell(editCellIndex);
            }
        }

        this.cell.element.removeClass('edit-box-bottom');
        this.cell.element.removeClass('edit-box-top');
        this.cell.element.removeClass('edit-box');
        addEditButton(this.cell);
        if(!accepted && this.debugging) {
            if (cellHasErrorOutput(this.cell)) {
                addFixButton(this.cell);
            }
        }
    }
    
    handleDeleteCell(cell) {
        if (this.accepted) {
            return;
        }
        console.log("handling delete cell", cell)
        if (this.cell.cell_id === cell.cell_id) {
            this.cell = this.editCells[this.editCells.length - 1];
            this.editCells.splice(this.editCells.length - 1, 1);
            this.close()
            return true;
        }
        if (this.editCells.some(editCell => editCell.cell_id === cell.cell_id)) {
            console.log("edit cells includes cell")
            this.editCells.splice(this.editCells.indexOf(cell), 1);
            if (this.editCells.length === 0) {
                this.close()
                return true;
            }
        }
        return false;
    }
    
    showButtons() {
        addAcceptCancel(this.editCells[this.editCells.length - 1]);
    }
    
    enableButtons() {
        enableAcceptButton(this.editCells[this.editCells.length - 1]);
    }
        
    removeButtons() {
        removeAcceptCancel(this.editCells[this.editCells.length - 1]);
    }
    
    containsCell(cell) {
        // if cell is str, set sellId to cell. else set to cell.cell_id
        let cellId = typeof cell === 'string' ? cell : cell.cell_id;
        if (this.cell.cell_id === cellId){
            return true
        }
        // return true if any editCells have cell_id === cellId
        return this.editCells.some(editCell => editCell.cell_id === cellId)
    }
    
    accept(cell_id) {
        this.accepted = true;
        this.close(true);
    }
    
    cancel() {
        this.close(false);
    }
}

// generate random id
function generateId() {
    return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

class EditZoneManager {
    constructor() {
        this.editZones = {};
    }
    
    getZone(cellId) {
        return this.editZones[cellId];
    }
    
    isEditCell(cell){
        for(const zone of Object.values(this.editZones)) {
            if(zone.containsCell(cell)) {
                return true;
            }
        }
    }
    
    createZone(cell, debugging) {
        if (this.editZones[cell.cell_id]) {
            return;
        }
        console.log("new edit zone")
        this.editZones[cell.cell_id] = new EditZone(cell, debugging);
    }
    
    handleDeleteCell(cell) {
        for(const [key, zone] of Object.entries(this.editZones)) {
            if(zone.containsCell(cell)) {
                console.log("zone:", zone, "contains cell:", cell)
                let isClosed = zone.handleDeleteCell(cell);
                if(isClosed) {
                    console.log("zone", key, "closed")
                    delete this.editZones[key];
                }
            }
        }
    }
    
    accept(cellId) {
        for(const [key, zone] of Object.entries(this.editZones)) {
            if (zone.cell.cell_id === cellId) {
                zone.accept();
                delete this.editZones[key];
                return;
            }
            for (const editCell of zone.editCells) {
                if (editCell.cell_id === cellId) {
                    zone.accept();
                    delete this.editZones[key];
                    return;
                }
            }
        }
    }
    
    cancel(cellId) {
        for(const [key, zone] of Object.entries(this.editZones)) {
            if(zone.containsCell(cellId)) {
                zone.cancel();
                delete this.editZones[key];
            }
        }
    }
    
    handleDoneStreaming(streamType, cellId) {
        if (streamType === "edit") {
            let cell = Jupyter.notebook.get_cells().find(cell => cell.cell_id == cellId);
            if (cell) {
                for (const [key, zone] of Object.entries(this.editZones)) {
                    if (zone.containsCell(cell)) {
                        zone.enableButtons();
                        cell.execute()
                    }
                }
            }
        }
    }
}
"""

LISTENER_JS = """
if(!window.JunoEditZones){
    window.JunoEditZones = new EditZoneManager();
}
if(!window.juno_initialized){
    window.openEditor = openEditor;
    Jupyter.notebook.events.off('output_appended.OutputArea');
    Jupyter.notebook.events.off('execute.CodeCell');
    Jupyter.notebook.events.on('output_appended.OutputArea', null, () => {
            console.log("output appended")
            setTimeout(() => cleanDebugButtons(true), 400)
            setTimeout(() => cleanDebugButtons(false), 800)
        }
    );
    Jupyter.notebook.events.on('execute.CodeCell', null, () => setTimeout(() => cleanDebugButtons(false), 400));
    // when cell is created, add edit button
    Jupyter.notebook.events.on('create.Cell', () => {
        setTimeout(() => addEditButtons(), 150)
        setTimeout(() => addEditButtons(), 400)
    });
    setInterval(() => addEditButtons(), 3000);
    // when cell is deleted call JunoEditZones.handleDeleteCell
    Jupyter.notebook.events.on('delete.Cell', (event, data) => JunoEditZones.handleDeleteCell(data.cell));
    addEditButtons();
    setTimeout(() => addEditButtons(), 600);
    console.log("loaded listener js");
    window.juno_initialized = true;
}

"""

DISPLAY_JUNO_INFO = """

function displayJunoInfo(version) {{
    let cell = Jupyter.notebook.get_cells().find(cell => cell.cell_type === "code" && cell.get_text().includes("%load_ext juno"))
    if (!cell) {{
        return;
    }}
    // add juno info below cell output area
    let outputArea = cell.output_area;
    let junoInfo = document.createElement("div");
    junoInfo.id = "juno-info";
    junoInfo.style = "margin-top: 10px; margin-bottom: 10px; padding: 10px; border: 1px solid #e6e6e6; border-radius: 3px; background-color: #f9f9f9; font-size: 12px; color: #666;";
    if(version && version !== ""){{
    }}
    // list the commands juno can run with explanations
    junoInfo.innerHTML = "Juno is your data science co-pilot. Here are some things you can do with Juno:<br><br>" +
        "<b>%juno</b> - prompt juno to write code for you<br>" +
        "<b>✎ edit</b> - prompt juno to edit a cell for you<br>" +
        "<b>🪲 debug</b> - have juno automatically fix your code when it outputs an error<br>"
    outputArea.element.append(junoInfo);
}}
displayJunoInfo({version});

"""

def get_info_injection(version):
    return DISPLAY_JUNO_INFO.format(version=version)