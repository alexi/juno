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
    if (cell.element.find('.juno-button-container').length) {
        return cell
    }
    let row = $('<div>', {class: 'juno-button-container'});
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
    let row = cell.element.find('.juno-button-container');
    if(row.length){
        row.remove();
    }
}

function addAcceptButton(cell) {
    let buttonDiv = $('<div>', {class: 'accept'});
    let existing_button = cell.element.find('.accept-container');
    if (!existing_button.length) {
        buttonDiv.html(
            '<div class="accept-container">' +
            '  <button type="button" style="margin-left: 94px;" onclick="window.JunoEditZones.accept(&#39;' + cell.cell_id + '&#39;)">Accept</button>' +
            '</div>');
        buttonDiv.find('button').prop('disabled', true);
        cell.element.append(buttonDiv);
    }
    return cell;
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

function removeAcceptButton(cell) {
    if(cell == null) {
        return;
    }
    let existing_button = cell.element.find('.accept-container');
    if(existing_button.length){
        existing_button.remove();
    }
}

function addCancelButton(cell) {
    let buttonDiv = $('<div>', {class: 'cancel'});
    let existing_button = cell.element.find('.cancel-container');
    if (!existing_button.length) {
        buttonDiv.html(
            '<div class="cancel-container">' +
            '  <button type="button" style="margin-left: 94px;" onclick="window.JunoEditZones.cancel(&#39;' + cell.cell_id + '&#39;)">Cancel</button>' +
            '</div>');
        cell.element.append(buttonDiv);
    }
    return cell;
}

function removeCancelButton(cell) {
    if(cell == null) {
        return;
    }
    let existing_button = cell.element.find('.cancel-container');
    if(existing_button.length){
        existing_button.remove();
    }
}

function openEditor(cellId) {
    console.log("opening editor for cell " + cellId)
    console.log("edit zones:", window.JunoEditZones)
    let cell = Jupyter.notebook.get_cells().find(cell => cell.cell_id == cellId);
    window.JunoEditZones.createZone(cell);
}

function addFixButton(cell, i) {
    let buttonDiv = $('<div>', {class: 'debug'});
    let existing_button = cell.element.find('.fix-container');
    if (!existing_button.length) {
        buttonDiv.html(
            '<div class="fix-container">' +
            '  <button type="button" style="margin-left: 94px;" onclick="window.writeExplanation(' + i + ')">Debug</button>' +
            '<div id="explanation-' + i + '" class="explanation" style="margin-left: 94px; margin-top: 10px;"></div>' +
            '</div>');
        cell.element.append(buttonDiv);
    }
    return cell;
}

function removeFixButton(cell) {
    let button = cell.element.find('.fix-container');
    if (button.length) {
        button.remove();
    }
}

function addUpdateCodeButton(cellIndex) {
  let cell = Jupyter.notebook.get_cell(cellIndex);
  let buttonDiv = $('<div>', {class: 'subdiv'});
  let existing_button = cell.element.find('.sub-container');
  if (!existing_button.length) {
    buttonDiv.html(
        '<div class="sub-container">' +
        '  <button type="button" style="margin-left: 94px;" onclick="window.fixCode' + cellIndex + '()">Apply Fix</button>' +
          '</div>');
      cell.element.append(buttonDiv);
  }
  return cell;
}

function removeUpdateCodeButton(cell) {
    let button = cell.element.find('.sub-container');
    if (button.length) {
        button.remove();
    }
}

function cellHasErrorOutput(cell) {
    let hasError = false;
    cell.output_area.outputs.forEach(output => {
        if (output.output_type === 'error') {
            hasError = true;
        }
    });
    return hasError;
}

function addRemoveButtons(addOnly) {
    let cells = Jupyter.notebook.get_cells();
    for (let i = 0; i < cells.length; i++) {
        let cell = cells[i];
        let cellHasError = cell.output_area.outputs.length > 0 && cellHasErrorOutput(cell);
        if (cellHasError) {
            addFixButton(cell, i);
        }
        else if (!addOnly && !cellHasError) {
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
    constructor(cell) {
        this.cell = cell;
        this.editCells = [];
        this.accepted = false;
        this._init();
    }
    
    _init() {
        console.log("initializing edit zone for cell " + this.cell)
        removeEditButton(this.cell);
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
        newCell.set_text("%edit ");
        this.editCells.push(newCell);
        setTimeout(() => {
            console.log("selecting cell " + cellIndex + 1)
            Jupyter.notebook.select(cellIndex + 1);
            newCell.focus_editor()
            newCell.code_mirror.setCursor({line:0, ch: 6})
        }, 200);
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
    
    createZone(cell) {
        if (this.editZones[cell.cell_id]) {
            return;
        }
        console.log("new edit zone")
        this.editZones[cell.cell_id] = new EditZone(cell);
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

EXPLANATION_FUNCTION = """

    {get_answer_function}

    {get_context_function}
    
    {get_error_function}
    
    function removeFirstLine(s) {{
      let index = s.indexOf("\\n");
      if (index !== -1) {{
        return s.slice(index + 1);
      }}
      return s;
    }}
    
    function performSubstitutions(substitutions, inputString) {{
      const lines = substitutions.split("\\n");
      for (const line of lines) {{
        const [search, replace] = line.split(" -> ");
        if (search) {{
            inputString = inputString.replace(search, replace);
        }}
      }}
      return inputString;
    }}


    window.writeExplanation = async function(cellIndex) {{
        let cell = Jupyter.notebook.get_cell(cellIndex);
        let prompt = `{prompt}`;
        let context = getContext({contextSize});
        prompt = prompt.replace("[PREV_CELL_CONTEXT]", context);
        
        if ({addError}) {{
            prompt = prompt.replace("[ERROR_CONTENT]", getErrorOutput(cell));
        }}
        console.log(prompt);
        let parsingSubs = false;
        let subsText = "";
        let text = "";
        let explanationElement = document.getElementById("explanation-" + cellIndex);
        let currentParagraph = document.createElement('p');
        currentParagraph.classList.add('explanation-paragraph');
        explanationElement.appendChild(currentParagraph);
        await getCompletion((answer) => {{
          let newText = answer.choices[0]["delta"]["content"];
          // if newText has a new line, create a new paragraph
          if (!parsingSubs && newText.includes('\\n')) {{
              let splitText = newText.split('\\n');
              currentParagraph.innerHTML += splitText[0];
              for (let i = 1; i < splitText.length; i++) {{
                  currentParagraph = document.createElement('p');
                  currentParagraph.classList.add('explanation-paragraph');
                  explanationElement.appendChild(currentParagraph);
                  text = splitText[i];
                  currentParagraph.innerHTML = text;
              }}
          }}
          // the explanation is over and we are interpreting the substitutions
          else if (newText.includes('—')) {{
            let dashSeparated = newText.split('—');
            text += dashSeparated[0];
            subsText += newText.slice(newText.indexOf("—") + 1);
            parsingSubs = true;
          }}
          else if (parsingSubs) {{
            subsText += newText;
          }}
          else {{
            text += newText;
            currentParagraph.innerHTML = text;
          }}
        }}, prompt)
        const substitutionsString = removeFirstLine(subsText);
        
        console.log("substitutionsString", substitutionsString);
        window["fixCode" + cellIndex] = function () {{
            console.log("fixing code");
            for (let i = cellIndex; i >= Math.max(0, cellIndex - {contextSize}); i--) {{
                let cellToFix = Jupyter.notebook.get_cell(i);
                let cellToFixText = cellToFix.get_text();
                cellToFix.set_text(performSubstitutions(substitutionsString, cellToFixText));
            }}
            removeUpdateCodeButton(cell);
        }}
        addUpdateCodeButton(cellIndex);

    }}
        """.format(prompt='', addContext="true", addError="true", contextSize=1,
                   get_answer_function=GET_ANSWER_CODE, get_context_function=GET_CONTEXT, get_error_function=GET_ERROR)

LISTENER_JS = """
if(!window.JunoEditZones){
    window.JunoEditZones = new EditZoneManager();
}
if(!window.juno_initialized){
    window.openEditor = openEditor;
    Jupyter.notebook.events.off('output_appended.OutputArea');
    Jupyter.notebook.events.off('execute.CodeCell');
    Jupyter.notebook.events.on('output_appended.OutputArea', () => setTimeout( () => addRemoveButtons(true), 200));
    Jupyter.notebook.events.on('execute.CodeCell', () => setTimeout(() => addRemoveButtons(false), 50));
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