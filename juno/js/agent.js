// generate random id
function generateId() {
    return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

async function* streamAsyncIterable(stream) {
  const reader = stream.getReader();
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        return;
      }
      yield value;
    }
  } finally {
    reader.releaseLock();
  }
}

async function fetchSSE(resource, options) {
  const { onMessage, ...fetchOptions } = options;
  // fetchOptions.credentials = "include";
  const resp = await fetch(resource, fetchOptions);
  for await (const chunk of streamAsyncIterable(resp.body)) {
    const message = new TextDecoder().decode(chunk);
    onMessage(message);
  }
  if(fetchOptions.onDone !== undefined) {
    fetchOptions.onDone();
  }
}

async function call(endpoint, payload, handleResponse){
    payload["visitor_id"] = localStorage.getItem("visitor_id")
    payload["api_key"] = localStorage.getItem("api_key")
    console.log("calling api endpoint:", endpoint, "with payload", payload)
    let resp = await fetch(window.juno_api_endpoint + endpoint, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload),
    })
    console.log("got response")
    let response = await resp.json()
    console.log("resp:", resp, "json:", response)
    try {
        console.log("handling response:", response)
        handleResponse(response)
        console.log("handled response:", response)
    } catch (e) {
        console.log("Error parsing data", response, e);
    }
}

async function stream(endpoint, payload, handleStreamMessage, doneCallback) {

    payload["visitor_id"] = localStorage.getItem("visitor_id")
    payload["api_key"] = localStorage.getItem("api_key")

    await fetchSSE(window.juno_api_endpoint + endpoint, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload),
        onMessage(message) {
            message.split("data: ").forEach((dataString) => {
                dataString = dataString.trim();
                if (dataString.length === 0) {
                    return;
                }
                else if (dataString === "[DONE]") {
                    console.log("COMPLETED receiving response ");
                    if (doneCallback !== undefined) {
                        doneCallback();
                    }
                    return;
                }
                try {
                    const data = JSON.parse(dataString);
                    handleStreamMessage(data);
                } catch (e) {
                    console.log("Error parsing data", dataString, e);
                }
            });
        },
        onDone() {
            if (doneCallback !== undefined) {
                doneCallback();
            }
        }
    });
}

var PROMPT_KEYS = ["%juno", "%action"]

function getContext(contextSize, offsetCells) {
    let prevCellContents = [];
    const cells = Jupyter.notebook.get_cells();
    const currentCellIndex = Jupyter.notebook.get_selected_index();
    for (let i = currentCellIndex - 1 - offsetCells; i >= Math.max(0, currentCellIndex - 1 - contextSize); i--) {
        let cell = cells[i];
        let cellContents = cell.get_text()
        // Don't include the prompt in the context
        if (!PROMPT_KEYS.some(prefix => cellContents.trimStart().startsWith(prefix))) {
            prevCellContents.unshift(cellContents)
        }
    }
    return prevCellContents.join("\\n###\\n");
}

function replaceLastOccurrence(str, search, replacement) {
    let lastIndex = str.lastIndexOf(search);
    if (lastIndex !== -1) {
        return str.slice(0, lastIndex) + replacement + str.slice(lastIndex + search.length);
    }
    return str;
}

function cellHasErrorOutput(cell) {
    if (!cell.output_area || ! cell.output_area.outputs) {
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

function cellHasOutput(cell) {
    if (!cell.output_area || ! cell.output_area.outputs) {
        return false;
    }
    return cell.output_area.outputs.length > 0;
}

class Agent {
    constructor(starting_cell) {
        this.starting_cell = starting_cell;
        this.cells = [this.starting_cell]
        this.session_id = generateId();
    }
}

class AgentManager {
    constructor() {
        this.agent = null;
    }
    
    start(cell, prompt, nb_context) {
        this.agent = new Agent(cell);
        call(
            'agent_start', 
            {
                "agent_id": this.agent.session_id,
                "data_info": nb_context,
                "command": prompt,
                "prev_transcript": getContext(5)
            },
            (response) => {
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
        setTimeout(() => {
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
        console.log("handle_cell_executed id:", cell.cell_id)
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
        let cellIndex = Jupyter.notebook.find_cell_index(cell)
        
        if (cellHasErrorOutput(cell)) {
            console.log("cell has error output")
            // todo: handle error auto debug
        }
        setTimeout(() => {
            Jupyter.notebook.select(cellIndex + 1);
            let _cell = Jupyter.notebook.get_cell(cellIndex + 1);
            _cell.focus_editor()
        }, 200);
        this.get_next()
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
            nextCell.execute()
        }
        else if (response["action"] === "done") {
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
            payload["prev_transcript"] = getContext(contextSize, 0);
        }
        let startingCellText = cell.get_text()
        let text = replaceLastOccurrence(startingCellText, "%action", "# %action") + "\n"

        // Select the cell with the command
        Jupyter.notebook.select(cellIndex);
        var done = () => {
            cell.execute()
        }
        await stream("query", payload, (answer) => {
            if (answer !== undefined) {
                text += answer;
                let trimmedText = text.replace(/`+$/, "").replace(/\\s+$/, ''); // Remove trailing backticks that denote end of markdown code block.
                cell.set_text(trimmedText);
            }
        }, done);
    }

}