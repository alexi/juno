import os
from .prompting_javascript import GET_ANSWER_CODE, GET_ERROR, GET_CONTEXT

JUNO_PKG_JS = open(os.path.join(os.path.dirname(__file__), 'js/juno.min.js')).read()

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
    junoInfo.style = "margin-left:114px; margin-top: 10px; margin-bottom: 10px; padding: 10px; border: 1px solid #e6e6e6; border-radius: 3px; background-color: #f9f9f9; font-size: 12px; color: #666;";
    if(version && version !== ""){{
    }}
    // list the commands juno can run with explanations
    junoInfo.innerHTML = "Juno is your data science co-pilot. Here are some things you can do with Juno:<br><br>" +
        "<b>%juno</b> - prompt juno to write code for you<br>" +
        "<b>✎ edit</b> - prompt juno to edit a cell for you<br>" +
        "<b>🪲 debug</b> - have juno automatically fix your code when it outputs an error<br>" +
        // "<b>%agent</b> - give juno a more complex task to plan and execute over multiple steps<br>" +
        "<div style='display: block;width: 100%;height: 1px;background-color: color(srgb 0.765 0.765 0.765);margin-top: 10px;margin-bottom: 10px;'></div>" +
        //"<b>%disable_sketch / enable_sketch</b> - disable/enable shallow, PII-filtered data sketches that <i>dramatically</i> improve juno's performance. (ON BY DEFAULT)<br>" +
        "<b><span style=''>%feedback</span></b> - send us some feedback on the alpha 🙏<br>"
    outputArea.element.append(junoInfo);
}}
displayJunoInfo({version});

"""

def get_info_injection(version):
    return DISPLAY_JUNO_INFO.format(version=version)