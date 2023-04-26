import types
import traitlets
import validators
import pandas as pd
import re

VALUES_ENABLED = True

phone_pattern = r"(\+\d{1,2}\s?)?1?\-?\.?\s?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}"
physical_address_pattern = r"\b(\d{1,6}\s([a-zA-z\.\s\-]+\s){0,3}([a-zA-z0-9\s]+[a-zA-Z\.])([\,\s]{0,2})?(road|street|avenue|boulevard|lane|drive|way|court|plaza|terrace|colony|close)[\,\s]{1,2}((Apt|Apartment|Floor|Suite|House)[\s\:]{1,2}\d{0,6}[\,\s]{1,2})?(([a-zA-Z]+[\s\-]?){1,4})?([\,\s]{0,2})?([A-Za-z]{2}|[a-zA-Z]+[\s\-])?([\,\s]{0,2}([0-9\-]{1,10})|[A-Z0-9]{3}\s[A-Z0-9]{3})?)\b"

def set_values_enabled(enabled):
    global VALUES_ENABLED
    VALUES_ENABLED = enabled
    
def filter_dataframe_pii(df, column) -> list:
    first_three_values = [truncate_value(v) for v in df[column].head(3).tolist()]
    for i, value in enumerate(first_three_values):
        if isinstance(value, str):
            if validators.uuid(value) and ('id' in column or 'user' in column):
                    first_three_values[i] = '(uuid)'
            elif validators.email(value):
                first_three_values[i] = '(email)'
            elif validators.ip_address.ipv4(value) or validators.ip_address.ipv6(value):
                first_three_values[i] = '(ip_address)'
            elif validators.card.card_number(value):
                first_three_values[i] = '(card_number)'
            elif re.match(phone_pattern, value):
                first_three_values[i] = '(phone)'
            elif re.match(physical_address_pattern, value):
                first_three_values[i] = '(address)'
    return first_three_values
    
def describe_dataframe(df, max_cols=20) -> str:
    description = []
    for column in df.columns[:max_cols]:
        is_index = column == df.index.name
        dtype = df[column].dtype
        if VALUES_ENABLED:
            first_three_values = filter_dataframe_pii(df, column)
            description.append(f"{column}, index: {is_index}, dtype: {dtype}. First three values: {first_three_values}")
        else:
            description.append(f"{column}, index: {is_index}, dtype: {dtype}.")
    full_description = "\n".join(description)
    shape_description = f"Shape: {df.shape}"
    return shape_description + '\nColumns:\n' + full_description

def describe_list(lst, max_length=50) -> str:
    if VALUES_ENABLED:
        truncated_list = list(lst)[:3]
        list_repr = ', '.join(truncate_value(x, max_length - 3) for x in truncated_list)
        return f"[{list_repr}{'...' if len(lst) > 3 else ''}] (length: {len(lst)})"
    else:
        return f"(length: {len(lst)})"

def describe_dict(dct, max_length=50) -> str:
    if VALUES_ENABLED:
        truncated_dict = {k: v for i, (k, v) in enumerate(dct.items()) if i < 3}
        dict_repr = ', '.join(f"{k}: {truncate_value(v, max_length - 5)}" for k, v in truncated_dict.items())
        return f"{{{dict_repr}{'...' if len(dct) > 3 else ''}}} (length: {len(dct)})"
    else:
        value_types = set()
        for value in dct.values():
            value_types.add(type(value))
        truncated_value_types = value_types[:3]
        value_types_str = ', '.join(str(truncate_value(t, max_length - 3)) for t in truncated_value_types)
        return f"(value-types: {value_types_str}{'...' if len(value_types) > 3 else ''} length: {len(dct)})"

def truncate_value(value, max_length=50):
    value_str = ""
    if isinstance(value, (list, tuple, set)):
        value_str = describe_list(value, max_length)
    elif isinstance(value, dict):
        value_str = describe_dict(value, max_length)
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
