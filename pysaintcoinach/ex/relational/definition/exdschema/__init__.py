from typing import List
from copy import deepcopy


def add_field(field_list, field: dict, parent_chain) -> None:
    if field.get("type") == "array":
        if field.get("fields", None) is None:
            # if you get an array without a field list, just repeat scalars
            for i in range(int(field.get("count", 1))):
                field_list.append(
                    SchemaField.create_field(field, True, i, parent_chain)
                )
        else:
            for i in range(int(field.get("count", 1))):
                fname = field.get("name")
                for nested_def in field.get("fields", []):
                    new_parent_chain = deepcopy(parent_chain)
                    new_parent_chain.append(f"{fname}[{i}]")
                    add_field(field_list, nested_def, new_parent_chain)
    else:
        field_list.append(SchemaField.create_field(field, False, 0, parent_chain))


class SchemaSheet:

    @property
    def name(self):
        return self.__name

    @property
    def display_field(self):
        return self.__display_field

    @display_field.setter
    def display_field(self, value):
        self.__display_field = value

    @property
    def fields(self) -> List:
        return self.__fields

    @property
    def relations(self) -> List:
        return self.__relations

    def process_yaml_fields(self, flist: List[dict]):
        fields = []
        for field in flist:
            add_field(fields, field, [])
        self.__fields = fields
        # Now that all the array fields are expanded into scalars, assign an index
        for i in range(len(self.__fields)):
            self.__fields[i].index = i

    def __init__(
        self,
        name: str,
        display_field: str,
        fields: List[dict] | None,
        relations: List | None,
    ) -> None:
        self.__name = name
        self.__display_field = display_field
        self.__fields = fields if fields is not None else []
        self.__relations = relations if relations is not None else []

        self.process_yaml_fields(self.__fields)


class SchemaField:
    @property
    def index(self):
        return self.__index

    @index.setter
    def index(self, value):
        self.__index = value

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def type(self):
        return self.__field_type

    @type.setter
    def type(self, value):
        self.__field_type = value

    @property
    def fields(self):
        return self.__fields

    @fields.setter
    def fields(self, value):
        self.__fields = value

    @property
    def condition(self) -> "Condition":
        return self.__condition

    @condition.setter
    def condition(self, value):
        self.__condition = value

    @property
    def targets(self):
        return self.__targets

    @targets.setter
    def targets(self, value: List):
        self.__targets = value

    @property
    def comment(self) -> str:
        return self.__comment

    def __init__(
        self, name, count, field_type, comment, fields, condition, targets
    ) -> None:
        self.__name = name
        self.__count = count
        self.__field_type = field_type
        self.__comment = comment
        self.__fields = fields
        self.__condition = (
            Condition.from_yaml(condition) if condition is not None else None
        )
        self.__targets = targets
        self.__index = 0

    def __repr__(self) -> str:
        return "%s(Name=%s,FieldType=%s,Index=%s)" % (
            self.__class__.__name__,
            self.__name,
            self.__field_type,
            self.__index,
        )

    @staticmethod
    def create_field(
        base_field: dict, is_array: bool, array_index: int, parent_chain: List[str]
    ):
        retv = SchemaField(
            "",
            0,
            (
                "scalar"
                if base_field.get("type") == "array"
                else base_field.get("type", "scalar")
            ),
            base_field.get("comment", ""),
            base_field.get("fields", []),
            base_field.get("condition"),
            base_field.get("targets"),
        )
        name = base_field.get("name", None)
        if is_array:
            name = f"{name}[{array_index}]"
        if len(parent_chain) > 0:
            parent_node_name = ".".join(parent_chain)
            if name is not None:
                name = f"{parent_node_name}.{name}"
            else:
                name = parent_node_name
        retv.name = name
        return retv


class Condition:

    @property
    def switch_field(self) -> str:
        return self.__switch_field

    @property
    def case_values(self) -> dict:
        return self.__case_values

    def __init__(self, switch_field: str, case_values: dict) -> None:
        self.__switch_field = switch_field
        self.__case_values = case_values

    @staticmethod
    def from_yaml(obj: dict) -> "Condition":
        return Condition(obj.get("switch", ""), obj.get("cases", {}))
