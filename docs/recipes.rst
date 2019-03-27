.. _recipes:

===========================
Recipe-driven data analysis
===========================

Recipes have been briefly introduced already with the concept of :ref:`tasks <tasks>`. However, the idea of recipe-driven data analysis is a bit more complex, and this page will provide more details, although still on a rather abstract level. Those readers interested in actually implementing recipe-driven data analysis are referred to the documentation of the :mod:`aspecd.tasks` module.

Basically, recipe-driven data analysis can be thought of a special type of user interface to the ASpecD framework and derived packages. The normal user of such package has a clear idea how to process and analyse data, but is not necessarily interested in actually programming a lot. Furthermore, reproducible science requires the history of each and every processing and analysis step to be recorded and stored in a way that can be used and understood long after the steps have been carried out (think of decades rather than weeks or months).

From the user's perspective, all that is required is a human-writable file format and a list of datasets followed by a list of tasks to be performed on these datasets. For each task, the user will want to provide all necessary parameters. Eventually, the user is providing the metadata of the data analysis. Introducing the metaphor of recipe and cook prevents multiple meanings of the term "metadata" and the confusion this might cause. A recipe is a list of datasets and tasks to perform on them. Such recipe is processed by a cook. This is the origin of the term "recipe-driven data analysis".


Reproducible and automated
==========================

Processing data consists of lots of different single tasks that can mostly be automated. This is the idea behind *recipe-driven data analysis*: lists of datasets and tasks that can easily be created by a user and processed fully automated. "Tasks" has a broad meaning here, covering basically every automatable aspect of data analysis, including processing and analysis steps, creating representations and annotations, and finally reports.

Storing the (somewhat abstract) recipes rather than scripts consisting of code depending too much on implementation details helps with reproducibility. On the one hand, problems with other versions of the underlying programs should be less frequent, and on the other hand, a human-readable list of datasets and tasks with their respective parameters is much easier to understand than actual code.

Automatisation comes with several advantages. Generally, everything that can be automated can be delegated to computers. That does not mean that the tasks carried out are necessarily correct, but they are usually consistent. And if mistakes in the input are detected, this can be easily fixed, resulting in a consistent (hopefully more correct) result. Additionally, everything that can be automated saves the user from performing boring and error-prone routine tasks and allows her or him to use their brains for good---thinking of ways how to process and analyse the data and to make sense of the results, *i.e.* things computers cannot really do for us. The power of automatisation is nicely reflected in a quote by Whitehead in his "Introduction to Mathematics":

   Civilization advances by extending the number of important operations which we can perform without thinking about them.

   -- Alfred North Whitehead, [Whitehead1911]_

The real important aspect of data analysis in science is to think about the data and the results obtained from automatically processing the (raw) data and to *interpret* these results. Everything else can (and should) be delegated to the computer as much as possible.


Fully unattended
================

Recipe-driven data analysis is carried out fully unattended (*i.e.*, non-interactive). This allows to use it in context of separate hardware and a scheduling system. Situations particularly benefiting from this approach are either many datasets that need to be processed all in the same way, or few datasets requiring expensive processing such as simulation and fitting. The latter is even more true in context of global fitting and/or sampling of different starting parameters, such as Monte-Carlo or Latin-Hypercube sampling approaches.

Furthermore, this approach allows to decouple the place the actual data processing will take place from the input. Think of containerisation (*e.g.*, `docker <https://www.docker.com/>`_) where the actual packages derived from ASpecD are located in a container that is self-contained and could basically even be shared with others [#fn1]_. Particularly in case of the above-mentioned long-running fitting tasks, having the data analysis run not on the personal computer, but on some server somewhere.


History
=======

Processing a recipe will always result in documenting all tasks performed. This includes the complete set of available information necessary to reproduce and replay the tasks, both parameters and version information of the actual routines used. For ease of use, these protocols can be used again as recipes (if necessary after automatic conversion).


Human-writable
==============

The file format of the recipes is an unimportant detail. However, at least in a first implementation, the `YAML file format <https://yaml.org/>`_ will be used. This format has been proven useful in similar settings (*e.g.*, `Ansible <https://www.ansible.com/>`_). Being very easy to write and read by humans due to the minimum of formatting required is perhaps its biggest advantage.

.. rubric:: Footnotes

.. [#fn1] Although an entirely different topic, containerisation would allow to even share a fully working installation of your analysis packages with collaboration partners. In such context, an easy-to-use and somewhat intuitive user interface as provided by *recipe-driven data analysis* will further help.

.. [Whitehead1911] Alfred North Whitehead. An Introduction to Mathematics. original 1911. Mineola: Dover Publications, 2017, S. 34.

