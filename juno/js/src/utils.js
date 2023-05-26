


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
 
// generate random id
function generateId() {
    return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

async function fetchSSE_agent(resource, options) {
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
    let resp = await fetch(window.juno.api_endpoint + endpoint, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload),
    })
    let response = await resp.json()
    try {
        handleResponse(response)
    } catch (e) {
        console.log("Error parsing data", response, e);
    }
}

async function stream(endpoint, payload, handleStreamMessage, doneCallback) {

    payload["visitor_id"] = localStorage.getItem("visitor_id")
    payload["api_key"] = localStorage.getItem("api_key")

    await fetchSSE_agent(window.juno.api_endpoint + endpoint, {
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
                    if (doneCallback !== undefined) {
                        doneCallback();
                    }
                    return;
                }
                if (dataString.length > 0){
                    try {
                        const data = JSON.parse(dataString);
                        handleStreamMessage(data);
                    } catch (e) {
                        console.log("Error parsing data", dataString, e);
                    }
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

module.exports = {
    generateId,
    fetchSSE_agent,
    call,
    stream,
    getContext,
    replaceLastOccurrence,
    cellHasErrorOutput,
    cellHasOutput
}