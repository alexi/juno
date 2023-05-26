// src/juno.js
const AgentManager = require('./agent.js');
const utils = require('./utils.js');
const { 
    EditZoneManager,
    addEditButtons,
    addStyles,
    addFixButton,
    removeFixButton
} = require('./handlers.js')

class Juno {
    // singleton
    constructor() {
        this.initialized = false;
        this.initialize()
    }
    
    initialize() {
        if (this.initialized) {
            return
        }
        this.juno_url = 'https://getjuno.ai/'
        this.api_endpoint = 'http://127.0.0.1:8000/'
        addStyles()
        this.agent_manager = new AgentManager()
        this.edit_zones = new EditZoneManager()
        this._listen()
        
        this.initialized = true
    }
    
    cleanDebugButtons(addOnly) {
        let cells = Jupyter.notebook.get_cells();
        for (const [i, cell] of cells.entries()) {
            let shouldShowDebugButton = utils.cellHasErrorOutput(cell) && !this.edit_zones.isEditCell(cell);
            if (shouldShowDebugButton ) {
                addFixButton(cell, i);
            }
            else if (!addOnly && !shouldShowDebugButton) {
                removeFixButton(cell);
            }
        }
    }
    
    _listen() {
        Jupyter.notebook.events.off('output_appended.OutputArea');
        Jupyter.notebook.events.off('execute.CodeCell');
        let handleOutput = (debut_update) => {
            this.cleanDebugButtons(debut_update)
            this.agent_manager.handle_output_appended()
        }
        Jupyter.notebook.events.on('output_appended.OutputArea', ( data) => {
                setTimeout(() => handleOutput(true), 400)
                setTimeout(() => handleOutput(false), 800)
                setTimeout(() => handleOutput(false), 2000)
            }
        );
        Jupyter.notebook.events.on('execute.CodeCell', ( event, data ) => {
                setTimeout(() => handleOutput(false), 400)
                setTimeout(() => this.agent_manager.handle_cell_executed(data.cell), 400)
                
                setTimeout(() => {
                    // if cell content starats with juno_api_key, delete cell
                    let cellText = data.cell.get_text()
                    if (cellText.startsWith("juno_api_key =")) {
                        data.cell.clear_output();
                        data.cell.set_text(cellText + " ✅")
                        setTimeout(() => {
                            let cellIndex = Jupyter.notebook.find_cell_index(data.cell);
                            Jupyter.notebook.delete_cell(cellIndex);
                        }, 1000)
                    }
                }, 400)
            }
        );
        // when cell is created, add edit button
        Jupyter.notebook.events.on('create.Cell', () => {
            setTimeout(() => addEditButtons(this.edit_zones), 150)
            setTimeout(() => addEditButtons(this.edit_zones), 400)
        });
        setInterval(() => addEditButtons(this.edit_zones), 3000);
        setInterval(() => this.cleanDebugButtons(true), 3000);
        // when cell is deleted call this.edit_zones.handleDeleteCell
        Jupyter.notebook.events.on('delete.Cell', (event, data) => this.edit_zones.handleDeleteCell(data.cell));
        addEditButtons(this.edit_zones);
        setTimeout(() => addEditButtons(this.edit_zones), 600);
    }
    
    openEditor(cellId, debugging=false) {
        let cell = Jupyter.notebook.get_cells().find(cell => cell.cell_id == cellId);
        this.edit_zones.createZone(cell, debugging);
    }
}

(function(global) {
    if (global.juno) {
        if(!global.juno.initialized) {
            global.juno.initialize()
        }
        return;
    }

    // assign to global object
    global.juno = new Juno();
    
    global.juno_url = 'https://getjuno.ai/'
    global.juno_api_endpoint = 'https://api.getjuno.ai/'
    // global.juno_api_endpoint = 'http://127.0.0.1:8000/'

})(window);