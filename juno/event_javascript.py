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

function addAcceptButton(cell) {
    let buttonDiv = $('<div>', {class: 'accept'});
    let existing_button = cell.element.find('.accept-container');
    if (!existing_button.length) {
        buttonDiv.html(
            '<div class="accept-container">' +
            '  <button type="button" style="margin-left: 94px;" onclick="window.EDIT_ZONES.accept(&#39;' + cell.cell_id + '&#39;)">Accept</button>' +
            '</div>');
        cell.element.append(buttonDiv);
    }
    return cell;
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

function openEditor(cellId) {
    console.log("opening editor for cell " + cellId)
    console.log("edit zones:", window.EDIT_ZONES)
    let cell = Jupyter.notebook.get_cells().find(cell => cell.cell_id == cellId);
    window.EDIT_ZONES.createZone(cell);
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
    console.log("adding edit buttons")
    let cells = Jupyter.notebook.get_cells();
    for (let i = 0; i < cells.length; i++) {
        let cell = cells[i];
        if (cell.cell_type === 'code' && !window.EDIT_ZONES.isEditCell(cell)) {
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
        this.addEditCell();
        this.showButtons();
    }
    
    addEditCell() {
        let cellIndex = this.editCells.length === 0 ? Jupyter.notebook.find_cell_index(this.cell) : Jupyter.notebook.find_cell_index(this.editCells[this.editCells.length - 1]);
        let newCell = Jupyter.notebook.insert_cell_below('code', cellIndex)
        newCell.set_text("%edit ");
        this.editCells.push(newCell);
        setTimeout(() => {
            console.log("selecting cell " + cellIndex + 1)
            Jupyter.notebook.select(cellIndex + 1);
            newCell.focus_editor()
        }, 200);
    }
    
    close() {
        for (let i = 0; i < this.editCells.length; i++) {
            // get cell index from cell id
            let cellId = this.editCells[i].cell_id;
            let cellIndex = Jupyter.notebook.get_cells().findIndex(cell => cell.cell_id == cellId);            
            Jupyter.notebook.delete_cell(cellIndex);
        }
        this.removeButtons();
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
        addAcceptButton(this.editCells[this.editCells.length - 1]); 
    }
    
    enableButtons() {
        
    }
    
    containsCell(cell) {
        if (this.cell.cell_id === cell.cell_id){
            return true
        }
        // return true if any editCells have cell_id === cell.cell_id
        return this.editCells.some(editCell => editCell.cell_id === cell.cell_id)
    }
        
    removeButtons() {
        removeAcceptButton(this.editCells[this.editCells.length - 1]);
    }
    
    accept(cell_id) {
        this.cell.set_text(this.editCells[this.editCells.length - 1].get_text());
        this.accepted = true;
        this.close();
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
    
    getZone(cell_id) {
        return this.editZones[cell_id];
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
    
    accept(cell_id) {
        for(const [key, zone] of Object.entries(this.editZones)) {
            if (zone.cell.cell_id === cell_id) {
                zone.accept();
                delete this.editZones[key];
                return;
            }
            for (const editCell of zone.editCells) {
                if (editCell.cell_id === cell_id) {
                    zone.accept();
                    delete this.editZones[key];
                    return;
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
if(!window.EDIT_ZONES){
    window.EDIT_ZONES = new EditZoneManager();
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
    // when cell is deleted call EDIT_ZONES.handleDeleteCell
    Jupyter.notebook.events.on('delete.Cell', (event, data) => EDIT_ZONES.handleDeleteCell(data.cell));
    addEditButtons();
    setTimeout(() => addEditButtons(), 600);
    console.log("loaded listener js");
    window.juno_initialized = true;
}

"""