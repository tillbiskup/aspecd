============
Introduction
============

The idea behind the ASpecD framework.


Reproducible data analysis
==========================

Reproducibility of data acquisition and processing is at the heart of proper science. To achieve this goal, documenting all parameters (of an experiment) is one necessary prerequisite. In large companies working in the field of chemistry, pharmacy and medicine, a strict quality management has led to developing large-scale, commercial, and highly integrated systems taking a maximum effort to ensure a gap-less record and documentation of each processing step. In fundamental research in academia, though, those systems are rare at best, if not simply not existing. In contrast, documenting the research directly correlates with the motivation of the individual scientist to cope with aspects of reproducibility as well as with her or his discipline to follow appropriate rules and workflows. In reality, experiments performed are usually insufficiently documented, let alone the following processing of the acquired data, even though missing information can often be inferred retrospectively thanks to experience and "informed guessing" of those directly involved in data acquisition.


Personal freedom vs. reproducible science
=========================================

At the same time, individuality, independence and personal responsibility of scientists are emphasised in the academic context for good reason. Generally, scientists should not be limited by too many and unnecessary rules. Even more, developing an individual concept for documenting experimental parameters necessary for a sensible and adequate analysis (and reproducibility) of the acquired data is often seen as an integral part of scientific education in universities.

Particularly in spectroscopy, home-built setups and lab-written, individual acquisition software are widespread. Therefore, it is of outstanding importance in this given context to document all experimental parameters, especially given that the acquisition software will usually *not* take care of this by itself. As this means extra effort for the experimenter, this documentation should be as easy and comfortable as possible. Ideally, it will be written in a format easily processable by computers, thus being accessible by software for data processing and analysis.


Scientists are not software engineers
=====================================

Another important aspect: Usually, programs for data processing and analysis get written by the indivudual scientist who is using them. However, scientists normally are not familiar with nor know about central aspects of software engineering developed over the last decades that are essential to create robust and reliable software of the necessary complexity that can be used by others as well and is sufficiently future-proof.

There are good reasons why developing and taking care of (more) complex software is usually in the realm of professional software engineers that can focus solely on this task. However, for most research groups in the academic context, it is not possible to hire professionals for this purpose. Besides that, the individual scientists should not use "black boxes" whose inner workings they neither know about nor understand. One strategy to overcome this problems may be to make scientists familiar with both, proven rules ("best practices") for programming as well as general concepts for data handling that have been developed by scientists and have been proven useful in day-to-day work. This would free scientists to focus on their actual science and would be beneficial in the long run.


Long-term storage and availability
==================================

Usually, most data nowadays are acquired and processed digitally using computers. This raises questions about long-term storage and availability. Whereas an increasing number of funding agencies in science require applicants to provide concepts for these aspects, developing appropriate solutions and actually implementing them in a working manner is far from easy. Given that often not only raw data are of interest, but detailed analyses as well, this becomes even more problematic.


The goal: concepts for reproducibility
======================================

All the aspects mentioned above have led to the development of the ASpecD framework (and its predecessors). The goal of the ASpecD framework is not to solve once and for all the problems mentioned. Rather, the idea is to provide concepts and show ways to tackle many of the individual aspects. The ultimate goal remains to have a system for data processing and analysis ensuring complete reproducibility (and replicability whereever possible) starting from the raw data and ending with final representations (figures, tables).

The different components and underlying principles of the ASpecD framework are the result of more than a decade of practical day-to-day work in experimental sciences (mostly spectroscopy), combined with reflecting about the requirements for its appropriate documentation. It started out with a set of individual short routines for analysing time-resolved EPR data. Nowadays, the concepts developed are but much more general and can be most certainly applied beyond spectroscopy as well.
