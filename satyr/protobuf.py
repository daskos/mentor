from __future__ import absolute_import, division, print_function

# import base64
from copy import copy
from functools import partial

import six
from google.protobuf.descriptor import FieldDescriptor
from google.protobuf.message import Message

__all__ = ["protobuf_to_dict", "TYPE_CALLABLE_MAP", "dict_to_protobuf",
           "REVERSE_TYPE_CALLABLE_MAP"]


TYPE_CALLABLE_MAP = {
    FieldDescriptor.TYPE_DOUBLE: float,
    FieldDescriptor.TYPE_FLOAT: float,
    FieldDescriptor.TYPE_INT32: int,
    FieldDescriptor.TYPE_INT64: int if six.PY3 else six.integer_types[1],
    FieldDescriptor.TYPE_UINT32: int,
    FieldDescriptor.TYPE_UINT64: int if six.PY3 else six.integer_types[1],
    FieldDescriptor.TYPE_SINT32: int,
    FieldDescriptor.TYPE_SINT64: int if six.PY3 else six.integer_types[1],
    FieldDescriptor.TYPE_FIXED32: int,
    FieldDescriptor.TYPE_FIXED64: int if six.PY3 else six.integer_types[1],
    FieldDescriptor.TYPE_SFIXED32: int,
    FieldDescriptor.TYPE_SFIXED64: int if six.PY3 else six.integer_types[1],
    FieldDescriptor.TYPE_BOOL: bool,
    FieldDescriptor.TYPE_STRING: six.text_type,
    FieldDescriptor.TYPE_BYTES: str,  # base64.b64encode,
    FieldDescriptor.TYPE_ENUM: int
}

REVERSE_TYPE_CALLABLE_MAP = {
    # FieldDescriptor.TYPE_BYTES: base64.b64decode
}

CONTAINER_MAP = []


def enum_to_label(field, value):
    return field.enum_type.values_by_number[int(value)].name


def label_to_enum(field, value):
    enum_dict = field.enum_type.values_by_name
    return enum_dict[value].number


def message_to_container(message, containers):
    for msg, cnt in containers:
        if isinstance(msg, type):  # class definition used
            if isinstance(message, msg):
                return cnt()
        elif isinstance(message, msg.__class__):  # object definition used
            if all([getattr(msg, field.name) == getattr(message, field.name)
                    for field, value in msg.ListFields()]):
                return cnt()
    return dict()  # fallback to plain dictionary


def container_to_message(container, containers):
    for msg, cnt in containers:
        if isinstance(container, cnt):
            if isinstance(msg, type):
                return msg()
            else:
                return copy(msg)


def protobuf_to_dict(pb, containers=CONTAINER_MAP, converters=TYPE_CALLABLE_MAP):
    result = message_to_container(pb, containers)

    # for field, value in pb.ListFields():  # only non-empty fields
    for field in pb.DESCRIPTOR.fields:  # empty fields too
        value = getattr(pb, field.name)
        if (field.message_type and field.message_type.has_options and
                field.message_type.GetOptions().map_entry):
            converter = dict
        elif field.type == FieldDescriptor.TYPE_MESSAGE:
            # recursively encode protobuf sub-message
            converter = partial(protobuf_to_dict, containers=containers,
                                converters=converters)
        elif field.type == FieldDescriptor.TYPE_ENUM:
            converter = partial(enum_to_label, field)
        else:
            converter = converters[field.type]

        if field.label == FieldDescriptor.LABEL_REPEATED:
            converter = partial(map, converter)

        result[field.name] = converter(value)

    return result


def dict_to_protobuf(dct, pb=None, containers=CONTAINER_MAP,
                     converters=REVERSE_TYPE_CALLABLE_MAP, strict=True):
    default = container_to_message(dct, containers)
    if pb:
        if default:
            pb.MergeFrom(default)
    else:
        pb = default
    pb = pb if isinstance(pb, Message) else pb()

    for k, v in dct.items():
        try:
            # TODO silently skip undifened fields
            field = pb.DESCRIPTOR.fields_by_name[k]
        except:
            if not strict:
                continue
            else:
                raise
        pb_value = getattr(pb, k, None)
        if field.label == FieldDescriptor.LABEL_REPEATED:
            for item in v:
                if field.type == FieldDescriptor.TYPE_MESSAGE:
                    dict_to_protobuf(item, pb_value.add(),
                                     containers, converters)
                elif field.type == FieldDescriptor.TYPE_ENUM:
                    pb_value.append(label_to_enum(field, item))
                else:
                    pb_value.append(item)
        elif field.type == FieldDescriptor.TYPE_MESSAGE:
            dict_to_protobuf(v, pb_value, containers, converters)
        else:
            if field.type in converters:
                v = converters[field.type](v)
            elif field.type == FieldDescriptor.TYPE_ENUM:
                v = label_to_enum(field, v)

            setattr(pb, field.name, v)

    return pb

encode = dict_to_protobuf
decode = protobuf_to_dict
