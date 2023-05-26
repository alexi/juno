const utils = require('./utils.js');

function addStyle(styleString) {
    const style = document.createElement('style');
    style.textContent = styleString;
    document.head.append(style);
}

const addStyles = () => {
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
        
        .juno-spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            animation: spin 2s linear infinite;
            margin-right: 10px;
        }
        
        @keyframes spin {
            0% {
                transform: rotate(0deg);
            }
            100% {
                transform: rotate(360deg);
            }
        }
    `);
}




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
            '<button class="edit-btn" type="button" style="height:19px;width:26px;margin-right:5px;font-size:25px;margin-top:1px;border-width:0px;background-color:white;overflow:visible" onclick="window.juno.openEditor(&#39;' + cell.cell_id + '&#39;)">✎</button>'
            );
        input_below_div.prepend(buttonDiv);
    }
    return cell;
}

function removeEditButton(cell) {
    let existing_button = cell.element.find('.edit-btn');
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
            '<button type="button" class="juno-button accept-button" style="margin-left: 89px;" onclick="window.juno.edit_zones.accept(&#39;' + cell.cell_id + '&#39;)">Accept</button>' +
            '<button type="button" class="cancel-button" style="margin-left: 5px;" onclick="window.juno.edit_zones.cancel(&#39;' + cell.cell_id + '&#39;)">Cancel</button>'
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

function enableAcceptButton(cell, edit_zones) {
    let existing_button = cell.element.find('.accept-button');
    if (!existing_button.length) {
        addEditButton(cell);
    }
    existing_button = cell.element.find('.accept-button');
    if (!existing_button.length) { return }
    existing_button.prop('disabled', false);
}

function addFixButton(cell, i) {
    if (cell.element.find('.debug-container').length) {
        return cell
    }
    let row = $('<div>', {class: 'juno-button-container debug-container'});
    row.html(
            '<button type="button" class="juno-button debug-button" style="margin-left: 93px;" onclick="window.juno.openEditor(&#39;' + cell.cell_id + '&#39;, true)">Debug</button>'
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

function addEditButtons(edit_zones) {
    let cells = Jupyter.notebook.get_cells();
    for (let i = 0; i < cells.length; i++) {
        let cell = cells[i];
        if (cell.cell_type === 'code' && !edit_zones.isEditCell(cell)) {
            addEditButton(cell, i);
        }
    }
}

class EditZone {
    constructor(cell, debugging) {
        this.cell = cell;
        this.editCells = [];
        this.accepted = false;
        this.debugging = debugging;
        this._init();
    }
    
    _init() {
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
                // console.log("selecting cell " + cellIndex + 1)
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
            if (utils.cellHasErrorOutput(this.cell)) {
                addFixButton(this.cell);
            }
        }
    }
    
    handleDeleteCell(cell) {
        if (this.accepted) {
            return;
        }
        // console.log("handling delete cell", cell)
        if (this.cell.cell_id === cell.cell_id) {
            this.cell = this.editCells[this.editCells.length - 1];
            this.editCells.splice(this.editCells.length - 1, 1);
            this.close()
            return true;
        }
        if (this.editCells.some(editCell => editCell.cell_id === cell.cell_id)) {
            // console.log("edit cells includes cell")
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
        this.editZones[cell.cell_id] = new EditZone(cell, debugging);
    }
    
    handleDeleteCell(cell) {
        for(const [key, zone] of Object.entries(this.editZones)) {
            if(zone.containsCell(cell)) {
                let isClosed = zone.handleDeleteCell(cell);
                if(isClosed) {
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

module.exports = {
    EditZoneManager: EditZoneManager,
    addEditButtons: addEditButtons,
    addEditButton: addEditButton,
    removeEditButton: removeEditButton,
    addFixButton: addFixButton,
    removeFixButton: removeFixButton,
    addStyles: addStyles
}