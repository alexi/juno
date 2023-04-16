import types
import traitlets

import pandas as pd


def describe_dataframe(df, max_cols=20) -> str:
    description = []
    for column in df.columns[:max_cols]:
        is_index = column == df.index.name
        dtype = df[column].dtype
        first_three_values = [truncate_value(v) for v in df[column].head(3).tolist()]
        description.append(f"{column}, index: {is_index}, dtype: {dtype}. First three values: {first_three_values}")
    full_description = "\n".join(description)
    shape_description = f"Shape: {df.shape}"
    return shape_description + '\nColumns:\n' + full_description


def truncate_value(value, max_length=50):
    value_str = ""

    if isinstance(value, (list, tuple, set)):
        truncated_list = list(value)[:3]
        list_repr = ', '.join(truncate_value(x, max_length - 3) for x in truncated_list)
        value_str = f"[{list_repr}{'...' if len(value) > 3 else ''}] (length: {len(value)})"
    elif isinstance(value, dict):
        truncated_dict = {k: v for i, (k, v) in enumerate(value.items()) if i < 3}
        dict_repr = ', '.join(f"{k}: {truncate_value(v, max_length - 5)}" for k, v in truncated_dict.items())
        value_str = f"{{{dict_repr}{'...' if len(value) > 3 else ''}}} (length: {len(value)})"
    elif isinstance(value, pd.DataFrame):
        value_str = describe_dataframe(value)
    else:
        value_str = str(value)
        if len(value_str) > max_length:
            value_str = value_str[:max_length] + "..."

    return value_str


def variable_description(local_ns, max_value_length=50):
    exclude_names = {'In', 'Out', 'get_ipython', 'exit', 'quit'}

    def is_user_defined(value):
        return not (
                isinstance(value, types.ModuleType) or
                isinstance(value, types.FunctionType) or
                isinstance(value, types.BuiltinFunctionType) or
                isinstance(value, types.MethodType) or
                isinstance(value, traitlets.traitlets.MetaHasTraits)
        )

    variables = {}
    for name, value in local_ns.items():
        if (
                not name.startswith('_') and
                name not in exclude_names and
                is_user_defined(value)
        ):
            truncated_value = truncate_value(value, max_value_length)
            variables[name] = {"type": type(value).__name__, "value": truncated_value }
    return variables
