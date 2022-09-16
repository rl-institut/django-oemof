"""Module holds models to store and restore oemof results in/from DB"""

import pandas
from django.contrib.postgres.fields import ArrayField
from django.db import models
from oemof.solph.processing import convert_keys_to_strings


class OemofDataset(models.Model):
    "Holds inputs and results of an oemof solph optimization"
    input = models.ForeignKey("OemofData", on_delete=models.CASCADE, related_name="data_input")  # noqa: A003
    result = models.ForeignKey("OemofData", on_delete=models.CASCADE, related_name="data_result")

    # pylint: disable=R0914
    @classmethod
    def store_results(cls, input_data, result_data):
        """
        Stores inputs and results from oemof into DB

        For each in entry in scalars and sequences of both input- and result-data
        an OemofScalar or OemofSequence is build and connected to an OemofData
        object representing either input or result data. At last, both OemofData
        objects are connected to OemofInputResult object and resulting index is
        returned.

        Parameters
        ----------
        input_data: dict
            Output of oemof.outputlib.processing.param_results with nodes as str
            (use oemof.outputlib.processing.convert_keys_to_str if necessary)
        result_data: dict
            Output of oemof.outputlib.processing.param_results with nodes as str
            (use oemof.outputlib.processing.convert_keys_to_str if necessary)

        Returns
        -------
        int: Index of created OemofDataset
        """
        # Check if nodes are strings:
        if not isinstance(next(iter(input_data)), str):
            input_data = convert_keys_to_strings(input_data)
        if not isinstance(next(iter(result_data)), str):
            result_data = convert_keys_to_strings(result_data)

        oemof_dataset = OemofDataset()
        for input_result_attr, data in (("input", input_data), ("result", result_data)):
            scalars = []
            sequences = []
            for (from_node, to_node), sc_sq_dict in data.items():
                for key, value in sc_sq_dict["scalars"].items():
                    scalar = OemofScalar(
                        from_node=from_node,
                        to_node=to_node,
                        attribute=key,
                        value=value,
                        type=type(value).__name__,
                    )
                    scalar.save()
                    scalars.append(scalar)

                for key, series in sc_sq_dict["sequences"].items():
                    list_type = "list"
                    if isinstance(series, pandas.Series):
                        series = series.values.tolist()
                        list_type = "series"
                    sequence = OemofSequence(
                        from_node=from_node,
                        to_node=to_node,
                        attribute=key,
                        value=series,
                        type=list_type,
                    )
                    sequence.save()
                    sequences.append(sequence)
            oemof_data = OemofData()
            oemof_data.save()
            oemof_data.scalars.set(scalars)
            oemof_data.sequences.set(sequences)
            setattr(oemof_dataset, input_result_attr, oemof_data)
        oemof_dataset.save()
        result_id = oemof_dataset.id
        return result_id

    def restore_results(self):
        """
        Restores input and result data from OemofDataset

        Returns
        -------
        (dict, dict):
            Restored input- and result-data
        """

        def type_conversion(value_str, value_type):
            if value_type == "str":
                return value_str
            if value_type == "float":
                return float(value_str)
            if value_type == "int":
                return int(value_str)
            if value_type == "bool":
                return bool(value_str)
            raise TypeError('Unknown conversion type "' + value_type + '"')

        input_data = {}
        result_data = {}
        for input_result_attr, data in (("input", input_data), ("result", result_data)):
            ir_attr = getattr(self, input_result_attr)
            for scalar in ir_attr.scalars.all():
                nodes = (scalar.from_node, scalar.to_node)
                if nodes not in data:
                    data[nodes] = {"scalars": {}, "sequences": {}}
                data[nodes]["scalars"][scalar.attribute] = type_conversion(scalar.value, scalar.type)
            for sequence in ir_attr.sequences.all():
                nodes = (sequence.from_node, sequence.to_node)
                if nodes not in data:
                    data[nodes] = {"scalars": {}, "sequences": {}}
                if sequence.type == "series":
                    series = pandas.Series(sequence.value)
                else:
                    series = sequence.value
                data[nodes]["sequences"][sequence.attribute] = series
        return input_data, result_data


class OemofData(models.Model):
    """Model to hold input or results data from oemof"""

    scalars = models.ManyToManyField("OemofScalar")
    sequences = models.ManyToManyField("OemofSequence")


class OemofScalar(models.Model):
    """Represents a scalar from oemof results"""

    from_node = models.CharField(max_length=255)
    to_node = models.CharField(max_length=255)
    attribute = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    type = models.CharField(max_length=255)  # noqa: A003


class OemofSequence(models.Model):
    """Represents a sequence from oemof results"""

    from_node = models.CharField(max_length=255)
    to_node = models.CharField(max_length=255, null=True)
    attribute = models.CharField(max_length=255)
    value = ArrayField(base_field=models.FloatField())
    type = models.CharField(max_length=255)  # noqa: A003
