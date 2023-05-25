# -*- coding: utf-8 -*-
"""
****************************************************
*            Common Physical Data Model
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import copy
from typing import Union, Any, List
from ..bronze import dictionary_utility
from ..bronze.comparison_utility import COMPARISON_METHOD_DICTIONARY as CMD


def check_for_wrapped_parameter(root: Any, param_list: List[str]) -> bool:
    """
    Internal method for validating existence of wrapped parameter.
    :param root: Root object.
    :param param_list: Parameter list.
    :return: Boolean, declaring whether wrapped parameter exists.
    """
    index = 0
    while len(param_list) != index:
        if hasattr(root, param_list[index]):
            root = getattr(root, param_list[index])
            index += 1
        else:
            return False
    return True


def unwrap_parameter(root: Any, param_list: List[str]) -> Any:
    """
    Internal method for unwrapping parameter.
    :param root: Root object.
    :param param_list: Parameter list.
    :return: Wrapped parameter.
    """
    index = 0
    while len(param_list) != index:
        root = getattr(root, param_list[index])
        index += 1
    return root


class FilterMaskOperatorException(Exception):
    """
    FilterMaskOperatorException class.
    """

    def __init__(self, expressions: list, comparison_dict: dict,
                 message: str = "exception occurred while configuring filter mask") -> None:
        """
        Initiation method for the exception.
        :param expressions: Filter Mask expressions.
        :param comparison_dict: Comparison dictionary.
        :param message: Message to include in exception.
        """
        self.expressions = expressions
        self.comparison_dict = comparison_dict
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        """
        Method for encoding exception as string.
        :return: Exception string.
        """
        return f"{self.message} : {self.comparison_dict} with {self.expressions}"


class FilterMask(object):
    """
    Class, representing Filter Mask objects.
    Filter Mask objects contain a list of constraint expressions.
    An expression is a list of the form ["key", "operator", "value"].
    Note that the default Filter Masks expect "flat" data in form of a dictionary of an object.
    "Deep" Filter Masks expect a list of "key"-values instead of a single "key"-value and can be used with nested
    dictionaries / recursive objects and will try to unwrap the target values / attributes.
    When checking an object or data against a Filter Mask, all expressions be correct in order for the object or data
    to be validated.
    "OR"-Logic can be implemented, by creating different filter masks and wrapping their checks into an any()-function.
    """

    def __init__(self, expressions: List[list], operator_dictionary: dict = CMD, deep: bool = False,
                 relative: bool = False) -> None:
        """
        Initiation method for Filter Mask objects.
        :param expressions: List of expressions.
        :param operator_dictionary: Operator dictionary to initiate filter mask with.
        :param deep: Flag, declaring whether filters are deep. Defaults to False. Examples:
            - Flat filter expression = ["key", "operator", "value"]
            - Deep filter expression = [["key", "nested key"], "operator", "value"]
        :param relative: Flag, declaring whether filters are relative Defaults to False.
            Relative Filter Masks expect a target key or list of keys (depending on "flat" or "deep" flag) as "value"
            and reference data as additional parameter for checks. The target key(s) are used to unwrap the reference
            data values for comparison.
        """
        self.expressions = []
        self.operators = set()
        self.operator_dictionary = {}

        self.deep = deep
        self.relative = relative
        self.add_filter_expressions(expressions)
        self.set_operator_dictionary(operator_dictionary)

    def add_filter_expressions(self, expressions: list) -> None:
        """
        Method for adding filter mask.
        :param expressions: Filter expressions.
        """
        self.expressions.extend(copy.deepcopy(expressions))
        new_ops = {exp[1] for exp in expressions}
        if not all(op in self.operator_dictionary for op in new_ops):
            raise FilterMaskOperatorException(self.expressions, self.operator_dictionary)
        self.operators |= new_ops

    def set_operator_dictionary(self, operator_dictionary: dict) -> None:
        """
        Method for setting operator dictionary.
        :param operator_dictionary: Operator dictionary.
        """
        if all(op in operator_dictionary for op in self.operators):
            self.operator_dictionary = operator_dictionary if operator_dictionary is not None else CMD
        else:
            raise FilterMaskOperatorException(self.expressions, operator_dictionary)

    def get_expressions(self, data: Union[dict, Any], reference_data: Union[dict, Any] = None) -> List[Any]:
        """
        Method for getting expressions.
        :param data: Data or object to build expressions.
        :param reference_data: Reference data in case of relative Filter Masks.
        :return: List of expressions.
        """
        if isinstance(data, dict):
            if self.deep:
                return self.operator_dictionary["and"](self.operator_dictionary[exp[1]](
                    dictionary_utility.extract_nested_value(data, exp[0])
                    , exp[2] if not self.relative else dictionary_utility.extract_nested_value(reference_data, exp[2]))
                                                       for
                                                       exp in self.expressions)
            else:
                return self.operator_dictionary["and"](
                    self.operator_dictionary[exp[1]](data[exp[0]],
                                                     exp[2] if not self.relative else reference_data[exp[2]])
                    for exp in self.expressions)
        else:
            if self.deep:
                return self.operator_dictionary["and"](self.operator_dictionary[exp[1]](
                    unwrap_parameter(data, exp[0])
                    , exp[2] if not self.relative else unwrap_parameter(reference_data, exp[2])) for exp in
                                                       self.expressions)
            else:
                return self.operator_dictionary["and"](self.operator_dictionary[exp[1]](
                    self.operator_dictionary[exp[1]](getattr(data, exp[0]),
                                                     exp[2] if not self.relative else getattr(reference_data, exp[2]))
                    , exp[2]) for exp in self.expressions)

    def check(self, data: Union[dict, Any], reference_data: Union[dict, Any] = None) -> bool:
        """
        Method for checking filter mask on data.
        :param data: Data or object to validate.
        :param reference_data: Reference data in case of relative Filter Masks.
        :return: True, if data matches filters, else False.
        """
        if self.deep:
            return self._check_deep(data, reference_data)
        else:
            return self._check_flat(data, reference_data)

    def _check_flat(self, data: Union[dict, Any], reference_data: Union[dict, Any] = None) -> bool:
        """
        Internal method for checking flat filter masks on data.
        :param data: Data or object to validate.
        :param reference_data: Reference data in case of relative Filter Masks.
        :return: True, if data matches filters, else False.
        """
        if isinstance(data, dict):
            return all(self.operator_dictionary[exp[1]](data[exp[0]], exp[2] if not self.relative else reference_data[
                exp[2]]) if self._check_flat_dictionary_key_existence(data, exp[0], reference_data, exp[2]) else False
                       for exp in self.expressions)
        else:
            return all(
                self.operator_dictionary[exp[1]](getattr(data, exp[0]),
                                                 exp[2] if not self.relative else getattr(reference_data, exp[
                                                     2])) if self._check_flat_object_attribute_existence(data, exp[0],
                                                                                                         reference_data,
                                                                                                         exp[
                                                                                                             2]) else False
                for exp in self.expressions)

    def _check_deep(self, data: Union[dict, Any], reference_data: Union[dict, Any] = None) -> bool:
        """
        Internal method for checking deep filter masks on data.
        :param data: Data or object to validate.
        :param reference_data: Reference data in case of relative Filter Masks.
        :return: True, if data matches filters, else False.
        """
        if isinstance(data, dict):
            return all(self.operator_dictionary[exp[1]](dictionary_utility.extract_nested_value(data, exp[0]), exp[
                2] if not self.relative else dictionary_utility.extract_nested_value(reference_data, exp[2]))
                       if self._check_deep_dictionary_key_existence(data, exp[0], reference_data, exp[2]) else False for
                       exp in self.expressions)
        else:
            return all(
                self.operator_dictionary[exp[1]](
                    unwrap_parameter(data, exp[0]),
                    exp[2] if not self.relative else unwrap_parameter(reference_data, exp[2]))
                if self._check_deep_object_attribute_existence(data, exp[0], reference_data, exp[2]) else False for exp
                in self.expressions)

    def _check_flat_object_attribute_existence(self, data: Any, attribute: Union[str, list],
                                               reference_data: Any = None,
                                               reference_attribute: Union[str, list] = None) -> bool:
        """
        Internal Method for checking flat attribute existence.
        :param data: Object to validate.
        :param attribute: Attribute list of the target attribute.
        :param reference_data: Reference object to validate in case of relative Filter Masks.
        :param reference_attribute: Reference attribute or list of attributes the reference attribute in case of
            relative Filter Masks.
        :return: True, if all necessary attributes exist, else False.
        """
        return hasattr(data, attribute) and (not self.relative or hasattr(reference_data, reference_attribute))

    def _check_deep_object_attribute_existence(self, data: Any, attribute: Union[str, list],
                                               reference_data: Any = None,
                                               reference_attribute: Union[str, list] = None) -> bool:
        """
        Internal Method for checking deep attribute existence.
        :param data: Object to validate.
        :param attribute: Attribute list of the target attribute.
        :param reference_data: Reference object to validate in case of relative Filter Masks.
        :param reference_attribute: Reference attribute or list of attributes the reference attribute in case of
            relative Filter Masks.
        :return: True, if all necessary attributes exist, else False.
        """
        return check_for_wrapped_parameter(data, attribute) and (not self.relative or check_for_wrapped_parameter(
            reference_data, reference_attribute))

    def _check_flat_dictionary_key_existence(self, data: dict, attribute: Union[str, list],
                                             reference_data: dict = None,
                                             reference_attribute: Union[str, list] = None) -> bool:
        """
        Internal Method for checking flat key existence.
        :param data: Data to validate.
        :param attribute: Key or key list of the target value.
        :param reference_data: Reference data to validate in case of relative Filter Masks.
        :param reference_attribute: Reference key or key list of the reference value in case of relative
            Filter Masks.
        :return: True, if all necessary attributes exist, else False.
        """
        return attribute in data and (not self.relative or reference_attribute in reference_data)

    def _check_deep_dictionary_key_existence(self, data: dict, attribute: Union[str, list],
                                             reference_data: dict = None,
                                             reference_attribute: Union[str, list] = None) -> bool:
        """
        Internal Method for checking deep key existence.
        :param data: Data to validate.
        :param attribute: Key or key list of the target value.
        :param reference_data: Reference data to validate in case of relative Filter Masks.
        :param reference_attribute: Reference key or key list of the reference value in case of relative
            Filter Masks.
        :return: True, if all necessary attributes exist, else False.
        """
        return dictionary_utility.exists(data, attribute) and (
                not self.relative or dictionary_utility.exists(reference_data,
                                                               reference_attribute))