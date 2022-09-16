
from django.db import models
from django.contrib.postgres.fields import ArrayField


class OemofDataset(models.Model):
    input = models.ForeignKey("OemofData", on_delete=models.CASCADE, related_name="data_input")
    result = models.ForeignKey("OemofData", on_delete=models.CASCADE, related_name="data_result")

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
                scalars.extend(
                    OemofScalar(
                        from_node=from_node,
                        to_node=to_node,
                        attribute=key,
                        value=value,
                        type=type(value).__name__,
                    )
                    for key, value in sc_sq_dict["scalars"].items()
                )

                for key, series in sc_sq_dict["sequences"].items():
                    list_type = "list"
                    if isinstance(series, pandas.Series):
                        series = series.values.tolist()
                        list_type = "series"
                    sequences.append(
                        OemofSequence(
                            from_node=from_node,
                            to_node=to_node,
                            attribute=key,
                            value=series,
                            type=list_type,
                        )
                    )
            oemof_data = OemofData()
            oemof_data.scalars = scalars
            oemof_data.sequences = sequences
            setattr(input_result, input_result_attr, oemof_data)
        oemof_dataset.save()
        result_id = oemof_dataset.id
        return result_id


class OemofData(models.Model):
    scalars = models.ManyToManyField("OemofScalar")
    sequences = models.ManyToManyField("OemofSequence")


class OemofScalar(models.Model):
    from_node = models.CharField(max_length=255)
    to_node = models.CharField(max_length=255)
    attribute = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    type = models.CharField(max_length=255)


class OemofSequence(models.Model):
    from_node = models.CharField(max_length=255)
    to_node = models.CharField(max_length=255, null=True)
    attribute = models.CharField(max_length=255)
    value = ArrayField(base_field=models.FloatField())
    type = models.CharField(max_length=255)