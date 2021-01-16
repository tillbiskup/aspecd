import aspecd.dataset
import aspecd.exceptions


class Model:
    """
    Base class for numerical models.

    Models are defined by (constant) parameters and values the model is
    evaluated for.

    As a simple example, consider a polynomial defined by its (constant)
    coefficients. The model will evaluate the polynomial for the values,
    and the result will be a :obj:`aspecd.dataset.CalculatedDataset` object
    containing the evaluated model in its data.

    Models can be seen as abstraction to simulations in some regard. In this
    respect, they will play a central role in conjunction with fitting
    models to data by adjusting their respective parameters, a quite general
    approach in science and particularly in spectroscopy.

    Attributes
    ----------
    parameters : :class:`dict`
        constant parameters characterising the model

    values : :class:`numpy.ndarray`
       values to evaluate the model for

    """

    def __init__(self):
        self.parameters = None
        self.values = None
        self._dataset = aspecd.dataset.CalculatedDataset()

    def create(self):
        """
        Create dataset containing the evaluated model as data

        The actual model creation should be implemented within the non-public
        method :meth:`_perform_task`. Furthermore, you should make sure your
        model will be evaluated for the values given in
        :attr:`aspecd.model.Model.values` and the resulting dataset having set
        the axes appropriately.

        Returns
        -------
        dataset : :class:`aspecd.dataset.CalculatedDataset`
            Calculated dataset containing the evaluated model as data

        Raises
        ------
        aspecd.exceptions.MissingParameterError
            Raised if either parameters or values are not set

        """
        self._check_prerequisites()
        self._perform_task()
        self._dataset.data.axes[0].values = self.values
        return self._dataset

    def from_dataset(self, dataset=None):
        """
        Obtain crucial information from an existing dataset.

        Often, models should be calculated for the same values as an
        existing dataset. Therefore, you can set the
        :attr:`aspecd.model.Model.values` property from a given dataset.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            Dataset to obtain crucial information for building the model from

        Raises
        ------
        aspecd.exceptions.MissingDatasetError
            Raised if no dataset is provided

        """
        if not dataset:
            raise aspecd.exceptions.MissingDatasetError
        self.values = dataset.data.axes[0].values

    def _check_prerequisites(self):
        if not self.parameters:
            raise aspecd.exceptions.MissingParameterError(
                'No parameters provided')
        if self.values is None:
            raise aspecd.exceptions.MissingParameterError(
                'No values provided')

    def _perform_task(self):
        """Create the actual model and evaluate it for the given values.

        The implementation of the actual model goes in here in all
        classes inheriting from Model. This method is automatically
        called by :meth:`self.create` after some background checks.

        """
