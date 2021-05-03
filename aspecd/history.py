"""History: Classes collecting information on what has been done to a dataset.

Reproducibility is an essential aspect of good scientific practice. In the
context of data processing and analysis, this means that each processing
step performed on data (of a dataset) should be stored in an reproducible
way and preferably in a consistent format.

To be of actual use, an entry of the history needs to contain all
information necessary to reproduce the processing step in its original form.
This includes as a minimum the name of the processing routine used,
the complete list of necessary parameters for that routine, and a unique
version information of the routine. Additional useful aspects contain
information about the operating system used, the name of the operator,
and the date the processing step has been performed.

"""

from datetime import datetime

import aspecd
import aspecd.exceptions
import aspecd.system
import aspecd.utils


class HistoryRecord(aspecd.utils.ToDictMixin):
    """Generic base class for all kinds of history records.

    For all classes operating on datasets, such as
    :class:`aspecd.processing.SingleProcessingStep`,
    :class:`aspecd.analysis.SingleAnalysisStep` and others, there exist at
    least two "representations": (i) the generic one not (necessarily) tied
    to any concrete dataset, thus portable, and (ii) a concrete one having
    operated on a dataset and thus being accompanied with information about
    who has done what when how to what dataset.

    For this second type, a history class derived from
    :class:`aspecd.dataset.HistoryRecord` gets used, and it is this second type
    that is stored inside the Dataset object.

    Attributes
    ----------
    date : :obj:`datetime.datetime`
        datetime object with date current at HistoryRecord instantiation
    sysinfo : :obj:`aspecd.system.SystemInfo`
        key--value store with crucial system parameters, including user
        login name

    Parameters
    ----------
    package : :class:`str`
        Name of package the history record gets recorded for

        Prerequisite for reproducibility, gets stored in the
        :attr:`sysinfo` attribute. Will usually be provided automatically by
        the dataset.

    """

    def __init__(self, package=''):
        self.date = datetime.today()
        self.sysinfo = aspecd.system.SystemInfo(package=package)
        super().__init__()

    def from_dict(self, dict_=None):
        """
        Set properties from dictionary.

        Only parameters in the dictionary that are valid properties of the
        class are set accordingly.

        Datetime objects are set correctly from the string.

        If the corresponding attribute is an object having a ``from_dict``
        method itself, this method will be called accordingly, making
        cascading calls possible.

        Parameters
        ----------
        dict_ : :class:`dict`
            Dictionary containing properties to set

        """
        for key, value in dict_.items():
            if hasattr(self, key):
                attribute = getattr(self, key)
                if key == "date":
                    if hasattr(datetime, 'fromisoformat'):
                        self.date = datetime.fromisoformat(value)
                    else:
                        self.date = datetime.strptime(value,
                                                      '%Y-%m-%d %H:%M:%S.%f')
                elif hasattr(attribute, 'from_dict'):
                    attribute.from_dict(value)
                else:
                    setattr(self, key, value)


class ProcessingStepRecord(aspecd.utils.ToDictMixin):
    """Base class for processing step records stored in the dataset history.

    The history of a :class:`aspecd.dataset.Dataset` should *not* contain
    references to :class:`aspecd.processing.SingleProcessingStep` objects, but rather
    records that contain all necessary information to create the respective
    objects inherited from :class:`aspecd.processing.SingleProcessingStep`. One
    reason for this is simply that we want to import datasets containing
    processing steps in their history for which no corresponding processing
    class exists in the current installation of the application.

    .. note::
        Each history entry in a dataset stores the processing as a
        :class:`aspecd.processing.ProcessingStepRecord`, even in applications
        inheriting from the ASpecD framework. Hence, subclassing of this class
        should normally not be necessary.

    Attributes
    ----------
    undoable : :class:`bool`
        Can this processing step be reverted?
    description : :class:`str`
        Short description, to be set in class definition
    parameters : :class:`dict`
        Parameters required for performing the processing step

        All parameters, implicit and explicit.
    comment : :class:`str`
        User-supplied comment describing intent, purpose, reason, ...
    class_name : :class:`str`
        Fully qualified name of the class of the corresponding processing step

    Parameters
    ----------
    processing_step : :class:`aspecd.processing.SingleProcessingStep`
        Processing step the record should be created for.

    Raises
    ------
    aspecd.processing.MissingProcessingStepError
        Raised when no processing step exists to act on

    """

    def __init__(self, processing_step=None):
        super().__init__()
        self.undoable = False
        self.description = ''
        self.parameters = dict()
        self.comment = ''
        self.class_name = ''
        self._attributes_to_copy = ['description', 'parameters', 'undoable',
                                    'comment']
        if processing_step:
            self.from_processing_step(processing_step)

    def from_processing_step(self, processing_step):
        """Obtain information from processing step.

        Parameters
        ----------
        processing_step : :obj:`aspecd.processing.SingleProcessingStep`
            Object to obtain information from

        """
        for attribute in self._attributes_to_copy:
            setattr(self, attribute, getattr(processing_step, attribute))
        self.class_name = processing_step.name

    def create_processing_step(self):
        """Create a processing step object from the parameters stored.

        Returns
        -------
        processing_step : :class:`aspecd.processing.SingleProcessingStep`
            actual processing step object that can be used for processing,
            e.g., in context of undo/redo

        """
        processing_step = aspecd.utils.object_from_class_name(self.class_name)
        for attribute in self._attributes_to_copy:
            setattr(processing_step, attribute, getattr(self, attribute))
        return processing_step

    def from_dict(self, dict_=None):
        """
        Set properties from dictionary.

        Only parameters in the dictionary that are valid properties of the
        class are set accordingly.

        Parameters
        ----------
        dict_ : :class:`dict`
            Dictionary containing properties to set

        """
        for key, value in dict_.items():
            if hasattr(self, key):
                setattr(self, key, value)


class ProcessingHistoryRecord(HistoryRecord):
    """History record for processing steps on datasets.

    Attributes
    ----------
    processing : `aspecd.history.ProcessingStepRecord`
        record of the processing step

    Parameters
    ----------
    processing_step : :class:`aspecd.processing.SingleProcessingStep`
        processing step the history is saved for

    package : :class:`str`
        Name of package the history record gets recorded for

        Prerequisite for reproducibility, gets stored in the
        :attr:`aspecd.dataset.HistoryRecord.sysinfo` attribute.
        Will usually be provided automatically by the dataset.

    """

    def __init__(self, processing_step=None, package=''):
        super().__init__(package=package)
        self.processing = ProcessingStepRecord(processing_step)

    @property
    def undoable(self):
        """Can this processing step be reverted?"""
        return self.processing.undoable

    def replay(self, dataset):
        """Replay the processing step saved in the history record.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset the processing step should be replayed to

        """
        processing_step = self.processing.create_processing_step()
        processing_step.process(dataset=dataset)


class AnalysisStepRecord(aspecd.utils.ToDictMixin):
    """Base class for analysis step records.

    The analysis of a :class:`aspecd.dataset.Dataset` should *not* contain
    references to :class:`aspecd.analysis.AnalysisStep` objects, but rather
    records that contain all necessary information to create the respective
    objects inherited from :class:`aspecd.analysis.AnalysisStep`. One
    reason for this is simply that we want to import datasets containing
    analysis steps in their analyses for which no corresponding analysis
    class exists in the current installation of the application. Another is
    to not have an infinite recursion of datasets, as the dataset is stored
    in an :obj:`aspecd.analysis.AnalysisStep` object.

    Attributes
    ----------
    description : :class:`str`
        Short description, to be set in class definition
    parameters : :class:`dict`
        Parameters required for performing the analysis step

        All parameters, implicit and explicit.
    result
        Results of the analysis step

        Can be either a :class:`aspecd.dataset.Dataset` or some other
        class, *e.g.*, :class:`aspecd.metadata.PhysicalQuantity`.

        In case of a dataset, it is a calculated dataset
        (:class:`aspecd.dataset.CalculatedDataset`)
    comment : :class:`str`
        User-supplied comment describing intent, purpose, reason, ...
    class_name : :class:`str`
        Fully qualified name of the class of the corresponding analysis step

    Parameters
    ----------
    analysis_step : :class:`aspecd.analysis.SingleAnalysisStep`
        Analysis step the record should be created for.

    Raises
    ------
    aspecd.analysis.MissingAnalysisStepError
        Raised when no analysis step exists to act on

    """

    def __init__(self, analysis_step=None):
        super().__init__()
        self.description = ''
        self.parameters = dict()
        self.comment = ''
        self.class_name = ''
        self.result = None
        self._attributes_to_copy = ['description', 'parameters', 'comment',
                                    'result']
        if analysis_step:
            self.from_analysis_step(analysis_step)

    def from_analysis_step(self, analysis_step):
        """Obtain information from analysis step.

        Parameters
        ----------
        analysis_step : :obj:`aspecd.analysis.AnalysisStep`
            Object to obtain information from

        """
        for attribute in self._attributes_to_copy:
            setattr(self, attribute, getattr(analysis_step, attribute))
        self.class_name = analysis_step.name

    def create_analysis_step(self):
        """Create an analysis step object from the parameters stored.

        Returns
        -------
        analysis_step : :class:`aspecd.analysis.SingleAnalysisStep`
            actual analysis step object that can be used for analysis

        """
        analysis_step = aspecd.utils.object_from_class_name(self.class_name)
        analysis_step.comment = self.comment
        analysis_step.parameters = self.parameters
        analysis_step.description = self.description
        return analysis_step

    def from_dict(self, dict_=None):
        """
        Set properties from dictionary.

        Only parameters in the dictionary that are valid properties of the
        class are set accordingly.

        Parameters
        ----------
        dict_ : :class:`dict`
            Dictionary containing properties to set

        """
        for key, value in dict_.items():
            if hasattr(self, key):
                setattr(self, key, value)


class SingleAnalysisStepRecord(AnalysisStepRecord):
    """Base class for analysis step records stored in the dataset analyses.

    The analysis of a :class:`aspecd.dataset.Dataset` should *not* contain
    references to :class:`aspecd.analysis.AnalysisStep` objects, but rather
    records that contain all necessary information to create the respective
    objects inherited from :class:`aspecd.analysis.AnalysisStep`. One
    reason for this is simply that we want to import datasets containing
    analysis steps in their analyses for which no corresponding analysis
    class exists in the current installation of the application. Another is
    to not have an infinite recursion of datasets, as the dataset is stored
    in an :obj:`aspecd.analysis.AnalysisStep` object.

    .. note::
        Each analyses entry in a dataset stores the analysis step as a
        :class:`aspecd.analysis.SingleAnalysisStepRecord`, even in applications
        inheriting from the ASpecD framework. Hence, subclassing of this class
        should normally not be necessary.

    Attributes
    ----------
    preprocessing : :class:`list`
        List of processing steps

        The actual processing steps are objects of the class
        :class:`aspecd.processing.ProcessingStepRecord`.

    Parameters
    ----------
    analysis_step : :class:`aspecd.analysis.SingleAnalysisStep`
        Analysis step the record should be created for.

    """

    def __init__(self, analysis_step=None):
        super().__init__(analysis_step=analysis_step)
        self.preprocessing = []

    def from_analysis_step(self, analysis_step):
        """Obtain information from analysis step.

        Parameters
        ----------
        analysis_step : :obj:`aspecd.analysis.AnalysisStep`
            Object to obtain information from

        """
        super().from_analysis_step(analysis_step)
        self.preprocessing = analysis_step.preprocessing


class AnalysisHistoryRecord(HistoryRecord):
    """History record for analysis steps on datasets.

    Attributes
    ----------
    analysis : :class:`aspecd.analysis.SingleAnalysisStep`
        Analysis step the history is saved for

    package : :class:`str`
        Name of package the history record gets recorded for

        Prerequisite for reproducibility, gets stored in the
        :attr:`aspecd.dataset.HistoryRecord.sysinfo` attribute.
        Will usually be provided automatically by the dataset.

    Parameters
    ----------
    analysis_step : :class:`aspecd.analysis.SingleAnalysisStep`
        Analysis step the history is saved for

    package : :class:`str`
        Name of package the history record gets recorded for

    """

    def __init__(self, analysis_step=None, package=''):
        super().__init__(package=package)
        self.analysis = SingleAnalysisStepRecord(analysis_step)

    def replay(self, dataset):
        """Replay the analysis step saved in the history record.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset the analysis step should be replayed to

        """
        analysis_step = self.analysis.create_analysis_step()
        dataset.analyse(analysis_step=analysis_step)


class AnnotationRecord(aspecd.utils.ToDictMixin):
    """Base class for annotation records stored in the dataset annotations.

    The annotation of a :class:`aspecd.dataset.Dataset` should *not* contain
    references to :class:`aspecd.annotation.Annotation` objects, but rather
    records that contain all necessary information to create the respective
    objects inherited from :class:`aspecd.annotation.Annotation`. One
    reason for this is simply that we want to import datasets containing
    annotations in their analyses for which no corresponding annotation
    class exists in the current installation of the application. Another is
    to not have an infinite recursion of datasets, as the dataset is stored
    in an :obj:`aspecd.analysis.SingleAnalysisStep` object.

    .. note::
        Each annotation entry in a dataset stores the annotation as a
        :class:`aspecd.annotation.AnnotationRecord`, even in applications
        inheriting from the ASpecD framework. Hence, subclassing of this class
        should normally not be necessary.

    Attributes
    ----------
    content : :class:`dict`
        Actual content of the annotation

        Generic place for more information
    class_name : :class:`str`
        Fully qualified name of the class of the corresponding annotation

    Parameters
    ----------
    annotation : :class:`aspecd.annotation.Annotation`
        Annotation the record should be created for.

    Raises
    ------
    aspecd.annotation.MissingAnnotationError
        Raised when no annotation exists to act on

    """

    def __init__(self, annotation=None):
        super().__init__()
        self.content = dict()
        self.class_name = ''
        self._attributes_to_copy = ['content']
        if annotation:
            self.from_annotation(annotation)

    def from_annotation(self, annotation):
        """Obtain information from annotation.

        Parameters
        ----------
        annotation : :obj:`aspecd.annotation.Annotation`
            Object to obtain information from

        """
        for attribute in self._attributes_to_copy:
            setattr(self, attribute, getattr(annotation, attribute))
        self.class_name = aspecd.utils.full_class_name(annotation)

    def create_annotation(self):
        """Create an analysis step object from the parameters stored.

        Returns
        -------
        analysis_step : :class:`aspecd.analysis.SingleAnalysisStep`
            actual analysis step object that can be used for analysis

        """
        annotation = aspecd.utils.object_from_class_name(self.class_name)
        annotation.content = self.content
        return annotation

    def from_dict(self, dict_=None):
        """
        Set properties from dictionary.

        Only parameters in the dictionary that are valid properties of the
        class are set accordingly.

        Parameters
        ----------
        dict_ : :class:`dict`
            Dictionary containing properties to set

        """
        for key, value in dict_.items():
            if hasattr(self, key):
                setattr(self, key, value)


class AnnotationHistoryRecord(HistoryRecord):
    """History record for annotations of datasets.

    Attributes
    ----------
    annotation : :class:`aspecd.analysis.Annotation`
        Annotation the history is saved for

    package : :class:`str`
        Name of package the history record gets recorded for

        Prerequisite for reproducibility, gets stored in the
        :attr:`aspecd.dataset.HistoryRecord.sysinfo` attribute.
        Will usually be provided automatically by the dataset.

    Parameters
    ----------
    annotation : :class:`aspecd.annotation.AnnotationRecord`
        Annotation the history is saved for

    package : :class:`str`
        Name of package the history record gets recorded for

    """

    def __init__(self, annotation=None, package=''):
        super().__init__(package=package)
        self.annotation = AnnotationRecord(annotation)


class PlotRecord(aspecd.utils.ToDictMixin):
    """Base class for records storing information about a plot.

    For reproducibility of plots performed on either a single dataset or
    multiple datasets, information for each plot needs to be collected that
    suffices to reproduce the plot. This is what a PlotRecord is good for.

    All information will usually be obtained from a plotter object, either
    by instantiating a PlotRecord object providing a plotter object,
    or by calling :meth:`from_plotter` on a PlotRecord object.

    Subclasses for :obj:`aspecd.plotting.SinglePlotter` and
    :obj:`aspecd.plotting.MultiPlotter` objects are available, namely
    :class:`aspecd.plotting.SinglePlotRecord` and
    :class:`aspecd.plotting.MultiPlotRecord`.

    Attributes
    ----------
    class_name : :class:`str`
        Name of the plotter.

        Defaults to the plotter class name and shall never be set manually.
    description : :class:`str`
        Short description of the plot
    parameters : :class:`dict`
        All parameters necessary for the plot, implicit and explicit
    properties : :class:`aspecd.plotting.PlotProperties`
        Properties of the plot, defining its appearance
    caption : :class:`aspecd.plotting.Caption`
        User-supplied information for the figure.
    filename : :class:`str`
        Name of the file the plot has been/should be saved to


    Parameters
    ----------
    plotter : :obj:`aspecd.plotting.Plotter`
        Plotter object to obtain information from

    Raises
    ------
    aspecd.plotting.MissingPlotterError
        Raised if no plotter is provided.

    """

    def __init__(self, plotter=None):
        super().__init__()
        self.class_name = ''
        self.description = ''
        self.parameters = dict()
        self.properties = None
        self.caption = None
        self.filename = ''
        self._attributes_to_copy = ['description', 'parameters',
                                    'properties', 'caption', 'filename']
        if plotter:
            self.from_plotter(plotter=plotter)

    def from_plotter(self, plotter=None):
        """Obtain information from plotter.

        Parameters
        ----------
        plotter : :obj:`aspecd.plotting.Plotter`
            Plotter object to obtain information from

        Raises
        ------
        aspecd.plotting.MissingPlotterError
            Raised if no plotter is provided.

        """
        if not plotter:
            raise aspecd.exceptions.MissingPlotterError
        for attribute in self._attributes_to_copy:
            setattr(self, attribute, getattr(plotter, attribute))
        self.class_name = plotter.name

    def from_dict(self, dict_=None):
        """
        Set properties from dictionary.

        Only parameters in the dictionary that are valid properties of the
        class are set accordingly.

        Parameters
        ----------
        dict_ : :class:`dict`
            Dictionary containing properties to set

        """
        for key, value in dict_.items():
            if hasattr(self, key):
                setattr(self, key, value)


class SinglePlotRecord(PlotRecord):
    """Record for SinglePlotter objects.

    When plotting data of a single dataset, classes derived from
    :class:`aspecd.plotting.SinglePlotter` will be used. The information
    obtained from these plotters will be stored in a SinglePlotRecord object.

    Attributes
    ----------
    preprocessing : :class:`list`
        List of processing steps

        The actual processing steps are objects of the class
        :class:`aspecd.processing.ProcessingStepRecord`.

    Parameters
    ----------
    plotter : :obj:`aspecd.plotting.Plotter`
        Plotter object to obtain information from

    """

    def __init__(self, plotter=None):
        self.preprocessing = list()
        super().__init__(plotter=plotter)


class MultiPlotRecord(PlotRecord):
    """Record for MultiPlotter objects.

    When plotting data of multiple datasets, classes derived from
    :class:`aspecd.plotting.MultiPlotter` will be used. The information
    obtained from these plotters will be stored in a MultiPlotRecord object.

    Attributes
    ----------
    datasets : :class:`list`
        List of datasets whose data appear in the plot.

    Parameters
    ----------
    plotter : :obj:`aspecd.plotting.Plotter`
        Plotter object to obtain information from

    """

    def __init__(self, plotter=None):
        self.datasets = list()
        super().__init__(plotter=plotter)


class PlotHistoryRecord(HistoryRecord):
    """History record for plots of datasets.

    Attributes
    ----------
    plot : :class:`aspecd.plotting.SinglePlotRecord`
        Plot the history is saved for

    package : :class:`str`
        Name of package the history record gets recorded for

        Prerequisite for reproducibility, gets stored in the
        :attr:`aspecd.dataset.HistoryRecord.sysinfo` attribute.
        Will usually be provided automatically by the dataset.

    """

    def __init__(self, package=''):
        super().__init__(package=package)
        self.plot = SinglePlotRecord()
