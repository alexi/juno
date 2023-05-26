const utils = require('./utils.js');

class Agent {
    constructor(starting_cell) {
        this.starting_cell = starting_cell;
        this.cells = [this.starting_cell]
        this.session_id = utils.generateId();
        this.cell_states = {}
    }
    
    get_cell_state(cell) {
        return this.cell_states[cell.cell_id]
    }
    
    set_cell_state(cell, state) {
        this.cell_states[cell.cell_id] = state
    }
}

class AgentManager {
    constructor() {
        this.agent = null;
    }
    
    start(cell, prompt, nb_context) {
        this.agent = new Agent(cell);
        // add spinner below the cell
        let junoInfo = document.createElement("div");
        junoInfo.id = "juno-agent-spinner";
        junoInfo.style = "display: flex; align-items: center; margin-left:114px; margin-top: 10px; margin-bottom: 10px; padding: 10px; border: 1px solid #e6e6e6; border-radius: 3px; background-color: #f9f9f9; font-size: 12px; color: #666;";
        // list the commands juno can run with explanations
        junoInfo.innerHTML = "<div class='juno-spinner'></div><span style='padding-left:1px;'>planning...</span>"
        setTimeout(() => {
            let outputArea = cell.output_area;
            console.log("starting cell output area:", outputArea)
            
            outputArea.element.append(junoInfo);
        }, 400);
        utils.call(
            'agent_start', 
            {
                "agent_id": this.agent.session_id,
                "data_info": nb_context,
                "command": prompt,
                "prev_transcript": utils.getContext(5)
            },
            (response) => {
                // remove spinner
                junoInfo.remove();
                this.handle_agent_start_response(response);
            }
        )
    }
    
    done() {
        // unset agent, print agent done message
        this.agent = null
    }
    
    handle_agent_start_response(response) {
        console.log("handle_agent_start_response response:", response)
        let startCell = this.agent.cells[this.agent.cells.length - 1]
        let startingCellText = startCell.get_text()
        let text = utils.replaceLastOccurrence(startingCellText, "%agent", "# %agent")
        startCell.set_text(text)
        setTimeout(() => {
            let cellIndex = Jupyter.notebook.find_cell_index(startCell)
            Jupyter.notebook.select(cellIndex + 1);
            let _cell = Jupyter.notebook.get_cell(cellIndex + 1);
            _cell.focus_editor()
        }, 200);
        this.get_next();
    }
    
    handle_output_appended() {
        // console.log("handle_output_appended")
        // let cell = this.agent.cells[this.agent.cells.length - 1]
        // if (cellHasOutput(cell)) {
        //     this.handle_cell_executed()
        // }
    }
    
    handle_cell_executed(cell) {
        console.log("handle_cell_executed id:", cell.cell_id, "index:", Jupyter.notebook.find_cell_index(cell))
        // ignore on the initial agent cell
        if(!this.agent) { return }
        if (this.agent.cells.length == 1){
            return
        }
        let _cell = this.agent.cells[this.agent.cells.length - 1]
        console.log("last-cell-id:", _cell.cell_id)
        if(cell.cell_id != _cell.cell_id) {
            return
        }
        let state = this.agent.get_cell_state(cell)
        if(!state){
            console.log("initially query handle_cell_executed id:", cell.cell_id)
            this.agent.set_cell_state(cell, "querying")
            return
        } else if (state == "querying") {
            this.agent.set_cell_state(cell, "executed")
        } else if (state == "executed") {
            console.log("already handled handle_cell_executed id:", cell.cell_id)
            return
        }
        console.log("continuing handle_cell_executed id:", cell.cell_id, "index:", Jupyter.notebook.find_cell_index(cell))
        let cellIndex = Jupyter.notebook.find_cell_index(cell)
        
        if (utils.cellHasErrorOutput(cell)) {
            console.log("cell has error output")
            // todo: handle error auto debug
        }
        setTimeout(() => {
            Jupyter.notebook.select(cellIndex + 1);
            let _cell = Jupyter.notebook.get_cell(cellIndex + 1);
            _cell.focus_editor()
        }, 20);
        
        setTimeout(() => {
            this.get_next()
        }, 20);
    }
    
    get_next() {
        let payload = {
            "agent_id": this.agent.session_id
        }
        call(
            'agent_next', 
            payload,
            (response) => {
                this.handle_agent_next_response(response);
            }
        )
    }
    
    handle_agent_next_response(response) {
        console.log("handle_agent_next_response response:", response)
        
        if (response["action"] === "next") {
            let i = Jupyter.notebook.find_cell_index(this.agent.cells[this.agent.cells.length - 1])
            let nextCell = Jupyter.notebook.get_cell(i+1)
            if(nextCell === null) {
                nextCell = Jupyter.notebook.insert_cell_below("code")
            }
            nextCell.set_text(response["message"])
            this.agent.cells.push(nextCell)
            console.log("executing cell:", nextCell.cell_id, "index:", Jupyter.notebook.find_cell_index(nextCell), "i+1:", i+1)
            nextCell.execute()
        } else if (response["action"] === "done") {
            this.done();
        }
    }
    
    async stream_action(command, ns, addContext, contextSize) {
        if(!this.agent){
            return
        }
        // let cellIndex = Jupyter.notebook.get_selected_index() - 1;
        // let cell = Jupyter.notebook.get_cell(cellIndex);
        let cell = this.agent.cells[this.agent.cells.length - 1]
        let cellIndex = Jupyter.notebook.find_cell_index(cell)
        let payload = {
            "command" : command,
            "data_info": ns,
            "agent_id": this.agent.session_id,
        }
        if (addContext) {
            payload["prev_transcript"] = utils.getContext(contextSize, 0);
        }
        let startingCellText = cell.get_text()
        let text = utils.replaceLastOccurrence(startingCellText, "%action", "# %action") + "\n"

        // Select the cell with the command
        Jupyter.notebook.select(cellIndex);
        var done = () => {
            cell.execute()
        }
        await utils.stream("query", payload, (answer) => {
            if (answer !== undefined) {
                text += answer;
                let trimmedText = text.replace(/`+$/, "").replace(/\\s+$/, ''); // Remove trailing backticks that denote end of markdown code block.
                cell.set_text(trimmedText);
            }
        }, done);
    }
}

module.exports = AgentManager