from time import time

GET_CONTEXT = """
function getContext(contextSize, offsetCells) {{
    let prevCellContents = [];
    const cells = Jupyter.notebook.get_cells();
    const currentCellIndex = Jupyter.notebook.get_selected_index();
    for (let i = currentCellIndex - 1 - offsetCells; i >= Math.max(0, currentCellIndex - 1 - contextSize); i--) {{
        let cell = cells[i];
        let cellContents = cell.get_text()
        // Don't include the prompt in the context
        if (!cellContents.trimStart().startsWith("%juno")) {{
            prevCellContents.unshift(cellContents)
        }}
    }}
    return prevCellContents.join("\\n###\\n");
}}

function replaceLastOccurrence(str, search, replacement) {{
    let lastIndex = str.lastIndexOf(search);
    if (lastIndex !== -1) {{
        return str.slice(0, lastIndex) + replacement + str.slice(lastIndex + search.length);
    }}
    return str;
}}

""".format()  # Formatting because of the double brackets included.

GET_ERROR = """
function getErrorOutput(cell) {
    let errorOutputs = cell.output_area.outputs.filter( output => output.output_type === 'error')
    if (errorOutputs.length > 0) {
        let error = errorOutputs[0];
        return `${error.ename}: ${error.evalue}`;
    }
    return "";
}
"""

GET_ANSWER_CODE = """
async function getCompletion(callback, endpoint, payload, doneCallback) {{
    console.log("doneCallback", doneCallback)

    payload["visitor_id"] = localStorage.getItem("visitor_id")
    payload["user_id"] = localStorage.getItem("user_id")

    await fetchSSE("https://api.struct.network/" + endpoint, {{
        method: "POST",
        headers: {{
            "Content-Type": "application/json"
        }},
        body: JSON.stringify(payload),
        onMessage(message) {{
            message.split("data: ").forEach((dataString) => {{
                dataString = dataString.trim();
                if (dataString.length === 0) {{
                    return;
                }}
                else if (dataString === "[DONE]") {{
                    console.log("COMPLETED receiving response ");
                    if (doneCallback !== undefined) {{
                        doneCallback();
                    }}
                    return;
                }}
                try {{
                    const data = JSON.parse(dataString);
                    callback(data);
                }} catch (e) {{
                    console.log("Error parsing data", dataString, e);
                }}
            }});
        }},
        onDone() {{
            if (doneCallback !== undefined) {{
                doneCallback();
            }}
        }}
    }});
}}

async function* streamAsyncIterable(stream) {{
  const reader = stream.getReader();
  try {{
    while (true) {{
      const {{ done, value }} = await reader.read();
      if (done) {{
        return;
      }}
      yield value;
    }}
  }} finally {{
    reader.releaseLock();
  }}
}}

async function fetchSSE(resource, options) {{
  const {{ onMessage, ...fetchOptions }} = options;
  // fetchOptions.credentials = "include";
  const resp = await fetch(resource, fetchOptions);
  for await (const chunk of streamAsyncIterable(resp.body)) {{
    const message = new TextDecoder().decode(chunk);
    onMessage(message);
  }}
  if(fetchOptions.onDone !== undefined) {{
    fetchOptions.onDone();
  }}
}}

""".format()

def write_completion_stream(command, notebook_state, add_context=False, context_size=5):
    js = """

{get_answer_function}

{get_context_function}

// Back up one cell from the current selection to get the one with the command
let startCell = Jupyter.notebook.get_selected_index() - 1;
let cell = Jupyter.notebook.get_cell(startCell);
async function main() {{
    let context, errorContent;

    let payload = {{
        "command" : `{command}`,
        "data_info": `{ns}`,
    }}
    if ({addContext}) {{
        payload["prev_transcript"] = getContext({contextSize}, 0);
    }}
    let startingCellText = cell.get_text()
    let text = replaceLastOccurrence(startingCellText, "%juno", "# %juno") + "\\n"
    let newText = "";
    // Select the cell with the command
    Jupyter.notebook.select(startCell);
    let cell_id = cell.cell_id;
    var done = () => {{
        window.JunoEditZones.handleDoneStreaming('chat', cell_id)
    }}
    await getCompletion((answer) => {{
      newText = answer;
      if (newText !== undefined) {{
        text += newText;
        let trimmedText = text.replace(/`+$/, "").replace(/\\s+$/, ''); // Remove trailing backticks that denote end of markdown code block.
        cell.set_text(trimmedText);
      }}
    }}, "query", payload, done);
}}
if ((Date.now() / 1000) - {current_time} < 2) {{
    main();
}}
    """.format(command=command, ns=notebook_state, addContext="true" if add_context else "false", contextSize=context_size,
               get_answer_function=GET_ANSWER_CODE, get_context_function=GET_CONTEXT, current_time=round(time()))
    return js


def write_edit_stream(command, notebook_state, add_context=False, context_size=5, add_error=False):
    """Write a javascript function that will stream completions from OpenAI's API. using a Python prompt"""

    js = """

{get_answer_function}

{get_context_function}

{get_error_function}

// Cell with the command
// if we are adding an error message we are using the debug flow.
// In that case the execution is automatic so the notebook doesn't jump to the next cell.
let startCell = Jupyter.notebook.get_selected_index() -  ({addError} ? 0 : 1);
// Cell with code to be edited
let prevCell = Jupyter.notebook.get_cell(startCell - 1)
let cell = Jupyter.notebook.get_cell(startCell);
async function main() {{
    let context, errorContent;
    let payload = {{
        "command" : `{command}`,
        "data_info": `{ns}`,
    }}
    if ({addContext}) {{
        payload["prev_transcript"] = getContext({contextSize}, 2);
    }}
    if ({addError}) {{
        payload["prev_error"] = getErrorOutput(prevCell);
    }}
    let startingCellText = cell.get_text()
    payload["code_to_edit"] = prevCell.get_text()
    let noDebugText = replaceLastOccurrence(startingCellText, "%debug ", "")
    let text = replaceLastOccurrence(noDebugText, "%edit", "# %edit") + "\\n"
    let newText = "";
    Jupyter.notebook.select(startCell);
    let cell_id = cell.cell_id;
    var done = () => {{
        window.JunoEditZones.handleDoneStreaming('edit', cell_id)
    }}
    let endpoint = {addError} ? "debug" : "edit";
    await getCompletion((answer) => {{
      newText = answer;
      if (newText !== undefined) {{
        text += newText;
        // Remove trailing backticks that denote end of markdown code block.
        let trimmedText = text.replace(/`+$/, "").replace(/\\s+$/, "").replace(/^\\n+/, ""); 
        cell.set_text(trimmedText);
      }}
    }}, endpoint, payload, done);
    Jupyter.notebook.select(startCell);
}}
if ((Date.now() / 1000) - {current_time} < 2) {{
    main();
}}
    """.format(command=command, ns=notebook_state, addContext="true" if add_context else "false",
               contextSize=context_size, addError="true" if add_error else "false",
               get_answer_function=GET_ANSWER_CODE, get_context_function=GET_CONTEXT, get_error_function=GET_ERROR, current_time=round(time()))
    return js


def write_explanation_stream(command, ns, context_size=5):
    """Write a javascript function that will stream explanations from OpenAI's API. using a Python prompt"""
    js = """

    {get_answer_function}

    {get_context_function}
    
    {get_error_function}

    async function writeExplanation(cellIndex) {{
        let cell = Jupyter.notebook.get_cell(cellIndex);
        let context, errorContent;
        if ({addContext}) {{
            context = getContext({contextSize});
        }}
        if ({addError}) {{
            errorContent = getErrorOutput(cell);
        }}
        console.log(prompt);
        let text = "";
        let explanationElement = document.getElementById("explanation-" + cellIndex);
        await getCompletion((answer) => {{
          text += answer.choices[0]["delta"]["content"];
          explanationElement.innerHTML = text;
        }}, "query", `{command}`, `{ns}`, context, errorContent);
    }}
        """.format(command=command, ns=ns, addContext="true", addError="true", contextSize=context_size,
                   get_answer_function=GET_ANSWER_CODE, get_context_function=GET_CONTEXT, get_error_function=GET_ERROR)
    return js