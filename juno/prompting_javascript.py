from time import time

def set_api_key(api_key):
    return """
localStorage.setItem("api_key", "{api_key}");
""".format(api_key=api_key)

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
   let errorOutputs = cell.output_area.outputs.filter(output => output.output_type === 'error');
    if (errorOutputs.length > 0) {
        let error = errorOutputs[0];
       let traceback = error.traceback.join('\\n');
       return `${error.ename}: ${error.evalue}\\n${traceback}`;
    }
    return "";
}
"""

def submit_feedback(feedback):
    return """

// Back up one cell from the current selection to get the one with the command
let startCell = Jupyter.notebook.get_selected_index() - 1;
let cell = Jupyter.notebook.get_cell(startCell);
async function sendFeedback() {{
    let context, errorContent;
    let startingCellText = cell.get_text()
    let text = startingCellText.replace("%feedback ", "")
    // Select the cell with the command
    let cell_id = cell.cell_id;
    
    const payload = {{
        "message": `{feedback}`,
        "visitor_id": localStorage.getItem("visitor_id"),
        "api_key": localStorage.getItem("api_key"),
        "timestamp": Date.now(),
    }};
    await fetch(window.juno.api_endpoint + "feedback", {{
        method: "POST",
        headers: {{
            "Content-Type": "application/json"
        }},
        body: JSON.stringify(payload),
        onMessage(message) {{
        }}
    }})
    // add thank you message below cell
    let outputArea = cell.output_area;
    let junoInfo = document.createElement("div");
    junoInfo.id = "juno-info";
    junoInfo.style = "margin-top: 10px; margin-bottom: 10px; padding: 10px; border: 1px solid #e6e6e6; border-radius: 3px; background-color: #f9f9f9; font-size: 12px; color: #666;";
    // list the commands juno can run with explanations
    junoInfo.innerHTML = "Thank you for your feedback!"
    outputArea.element.append(junoInfo);
}}
if ((Date.now() / 1000) - {current_time} < 2) {{
    sendFeedback();
}}
    """.format(feedback=feedback, current_time=round(time()))

GET_ANSWER_CODE_SSE = """

const createURLWithParams = (url, params) => {{
  const urlObj = new URL(url);
  Object.keys(params).forEach((key) => urlObj.searchParams.append(key, params[key]));
  return urlObj.toString();
}};

async function getCompletion(callback, endpoint, payload, doneCallback) {{

    payload["visitor_id"] = localStorage.getItem("visitor_id")
    payload["api_key"] = localStorage.getItem("api_key")
    if (localStorage.getItem("agent") !== null) {{
        payload["agent"] = localStorage.getItem("agent")
    }}
    
    const url = createURLWithParams(window.juno.api_endpoint + endpoint, payload);
    const source = new EventSource(url);
    
    source.onmessage = (event) => {{
      message.split("data: ").forEach((dataString) => {{
          dataString = dataString.trim();
          if (dataString === "[DONE]") {{
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
    }}
    
    source.onerror = (e) => {{
      console.log("handling error fetching", e);
      if(e.status == 402) {{
          console.log("opening signup page")
          setTimeout(() => {{
              window.open(window.juno_url + 'signup', '_blank');
          }}, 10);
          // get selected cell
          let cell = Jupyter.notebook.get_selected_cell();
          // print login prompt below cell
          let outputArea = cell.output_area;
          let junoInfo = document.createElement("div");
          junoInfo.id = "juno-info";
          junoInfo.style = "margin-left: 114px; margin-top: 10px; margin-bottom: 10px; padding: 10px; border: 1px solid #e6e6e6; border-radius: 3px; background-color: #f9f9f9; font-size: 12px; color: #666;";
          // list the commands juno can run with explanations
          junoInfo.innerHTML = "Please <a href='" + window.juno_url + "signup' target='_blank'>signup</a> or <a href='" + window.juno_url + "login' target='_blank'>login</a> to continue using Juno"
          outputArea.element.append(junoInfo);
      }}
    }}
    
    if (doneCallback !== undefined) {{
        doneCallback();
    }}
}}

""".format()

GET_ANSWER_CODE = """

async function getCompletion(callback, endpoint, payload, doneCallback) {{

    payload["visitor_id"] = localStorage.getItem("visitor_id")
    payload["api_key"] = localStorage.getItem("api_key")
    if (localStorage.getItem("agent") !== null) {{
        payload["agent"] = localStorage.getItem("agent")
    }}
    
    await fetchSSE(window.juno.api_endpoint + endpoint, {{
        method: "POST",
        headers: {{
            "Content-Type": "application/json"
        }},
        body: JSON.stringify(payload),
        onMessage(message) {{
            message.split("data: ").forEach((dataString) => {{
                dataString = dataString.trim();
                if (dataString === "[DONE]") {{
                    if (doneCallback !== undefined) {{
                        doneCallback();
                    }}
                    return;
                }}
                if(dataString !== "") {{
                    try {{
                        const data = JSON.parse(dataString);
                        callback(data);
                    }} catch (e) {{
                        console.log("Error parsing data", dataString, e);
                    }}
                }}
            }});
        }},
        onDone() {{
            if (doneCallback !== undefined) {{
                doneCallback();
            }}
        }},
        onError(e) {{
            console.log("handling error fetching", e);
            if(e.status == 402) {{
                console.log("opening signup page")
                setTimeout(() => {{
                    window.open(window.juno_url + 'signup', '_blank');
                }}, 10);
                // get selected cell
                let cell = Jupyter.notebook.get_selected_cell();
                // print login prompt below cell
                let outputArea = cell.output_area;
                let junoInfo = document.createElement("div");
                junoInfo.id = "juno-login-info";
                junoInfo.style = "margin-left: 114px; margin-top: 10px; margin-bottom: 10px; padding: 10px; border: 1px solid #e6e6e6; border-radius: 3px; background-color: #f9f9f9; font-size: 12px; color: #666;";
                junoInfo.innerHTML = "Please <a href='" + window.juno_url + "signup' target='_blank'>signup</a> or <a href='" + window.juno_url + "login' target='_blank'>login</a> to continue using Juno"
                // add text input form for user to enter api key and call localStorage.setItem("api_key", api_key) on submit
                outputArea.element.append(junoInfo);
            }}
        }}
    }});
}}

async function fetchSSE(resource, options) {{
  const {{ onMessage, ...fetchOptions }} = options;
  // fetchOptions.credentials = "include";
  try {{
    const resp = await fetch(resource, fetchOptions);
    if(!resp.ok) {{
        if (options.onError !== undefined) {{
            options.onError(resp);
        }}
        return;
    }}
    const decoder = new TextDecoder();
    const reader = resp.body.getReader();

    while (true) {{
      const {{ done, value }} = await reader.read();
      if (done) {{
        break;
      }}
      const message = decoder.decode(value);
      onMessage(message);
    }}
    if(fetchOptions.onDone !== undefined) {{
        fetchOptions.onDone();
    }}
  }} catch (e) {{
    console.log("Error fetching", e);
    if (options.onError !== undefined) {{
        options.onError(e);
    }}
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
        window.juno.edit_zones.handleDoneStreaming('chat', cell_id)
    }}
    await getCompletion((answer) => {{
      // console.log("got answer chunk:", answer, "timestamp:", Date.now() / 1000)
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
        window.juno.edit_zones.handleDoneStreaming('edit', cell_id)
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