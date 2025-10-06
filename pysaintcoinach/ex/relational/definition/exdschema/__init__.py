from typing import List
from copy import deepcopy


def add_field(field_list: List, field: dict, parent_chain: List) -> None:
    """Add an exdschema field to the array of parsed fields

    Args:
        field_list (List): The final returned field list
        field (dict): The field being parsed
        parent_chain (List): The current chain of parent fields for the given field
    """
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
    """An EXDSchema sheet in class form"""

    @property
    def name(self) -> str:
        """
        The name of the sheet as specified in the EXDSchema
        """
        return self.__name

    @property
    def display_field(self):
        """
        If given, the primary column used to display this sheet's rows when accessed
        """
        return self.__display_field

    @display_field.setter
    def display_field(self, value: str) -> None:
        self.__display_field = value

    @property
    def fields(self) -> List:
        """The valid fields contained within this sheet"""
        return self.__fields

    @property
    def relations(self) -> List:
        """
        The list of relation objects contained within this sheet.
        A relation is considered a grouping of items with some related purpose,
        i.e. the ReceiveItems and ItemCost relations in SpecialShop.yml"""
        return self.__relations

    def process_yaml_fields(self, flist: List[dict]):
        """
        Take a given set of fields and process them into a field List suitable for use in the library

        Args:
            flist (List[dict]): the list of field objects from the yaml decoder
        """
        fields = []
        for field in flist:
            add_field(fields, field, [])

        # Now that all the array fields are expanded into scalars, assign an index
        for i, field in enumerate(fields):
            field.index = i

        self.__fields = fields

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
    """An OO representation of a Field within an EXDSchema Sheet"""

    @property
    def index(self):
        """The numeric index position of a field within its sheet"""
        return self.__index

    @index.setter
    def index(self, value):
        self.__index = value

    @property
    def name(self):
        """The name of this field, used in display and column headers"""
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def type(self):
        """The schematic type of the field, not to be confused with an underlying data type."""
        # TODO: Consider an enum, maybe?
        return self.__field_type

    @type.setter
    def type(self, value):
        self.__field_type = value

    @property
    def fields(self):
        """The list of subfields that are owned by this particular field. An Array type field may have its own child fields"""
        return self.__fields

    @fields.setter
    def fields(self, value):
        self.__fields = value

    @property
    def condition(self) -> "Condition":
        """The condition object that disambiguates the value in this column, if available"""
        return self.__condition

    @condition.setter
    def condition(self, value):
        self.__condition = value

    @property
    def targets(self):
        """The list of target sheets that this field should resolve to, in order"""
        return self.__targets

    @targets.setter
    def targets(self, value: List):
        self.__targets = value

    @property
    def comment(self) -> str:
        """A helpful, human readable commentary on the field, if provided"""
        return self.__comment

    @property
    def converter(self) -> str:
        """The specified override converter for a field, if provided"""
        return self.__converter

    @converter.setter
    def converter(self, value):
        self.__converter = value

    def __init__(
        self, name, count, field_type, comment, fields, condition, targets, converter
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
        self.__converter = converter

    def __repr__(self) -> str:
        return (
            f"{{self.__class__.__name__}}(Name={self.__name}, FieldType={self.__field_type}, "
            f"Index={self.__index}, Converter={self.__converter})"
        )

    @staticmethod
    def create_field(
        base_field: dict, is_array: bool, array_index: int, parent_chain: List[str]
    ):
        """
        Create a Field object to pass back into a field List for a given schema

        Args:
            base_field (dict): The object containing the Field's properties, as given in the YAML object
            is_array (bool): Whether the current field is part of a parent array
            array_index (int): The numerical array index of this item, if is_array is true
            parent_chain (List[str]): The parent heirachy chain for this Field within the Schema

        Returns:
            Field: The OO Field representation, suitable for manipulation or sending to ARealmReversed class
        """
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
            base_field.get("converter"),
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
    """
    A switch/case statement equivalent, used in disamiguating columns
    which point toward different Sheets depending on a given value for some
    other Column within the Sheet
    For example, in Achievement.yml, the Key column links to different sheets
    based on the numeric value of the Type column in that row of the sheeet
    """

    @property
    def switch_field(self) -> str:
        """The field to examine to determine which related Sheet to link to"""
        return self.__switch_field

    @property
    def case_values(self) -> dict:
        """The case/target values for this condition"""
        return self.__case_values

    def __init__(self, switch_field: str, case_values: dict) -> None:
        self.__switch_field = switch_field
        self.__case_values = case_values

    @staticmethod
    def from_yaml(obj: dict) -> "Condition":
        """Process a YAML object into a Condition object"""
        return Condition(obj.get("switch", ""), obj.get("cases", {}))
