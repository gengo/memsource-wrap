==========
Change Log
==========
All notable changes to this project will be documented in this file. Dates are in UTC.

Unreleased
==========
[0.5.5] - 2020-06-29
====================

Added
-----
- Added a new Bilingual class for Memsource REST transition.

[0.5.4] - 2020-06-24
====================

Added
-----
- Added a new Job class for Memsource REST transition.

[0.5.3] - 2020-06-23
====================

Added
-----
- Added a new Project class for Memsource REST transition.

[0.5.2] - 2020-06-22
====================

Added
-----
- Added a new Domain class for Memsource REST transition.
- Added a new Language class for Memsource REST transition.
- Added a new TermBase class for Memsource REST transition.

[0.5.1] - 2020-06-19
====================

Added
-----
- Added a new Auth class for Memsource REST transition.
- Added a new Client class for Memsource REST transition.

[0.5.0] - 2020-06-17
====================

Added
-----
- Added a new Base class for Memsource REST transition.

[0.4.11] - 2020-05-22
====================

Add page parameter in `listByProject`
-----
- Added `page` parameter for fetching job list in `listByProject`.

[0.4.10] - 2019-11-28
====================

Fix bug
-----
- Fix bug in getting token in Memsource Auth class.

[0.4.9] - 2019-08-23
====================

Refactored
-----
- Refactored `headers` parameter on initiating the Memsource class.
- Removed `inflection` package.

[0.4.8] - 2019-08-21
====================

Added
-----
- Added `headers` parameter on initiating the Memsource class. This will be used for authentication.

[0.4.7] - 2019-08-19
====================

Upgraded
-----
- Upgraded python version from python3.4 to python3.5.

[0.4.6] - 2018-11-08
====================

Added
-----
- Extra project_id parameter to term base download method.

[0.4.5] - 2018-10-29
====================

Fix
-----
- Fix file format parameter constant in term base download method.

[0.4.4] - 2018-10-25
====================

Added
-----
- Support get term base list of a project.
- Support download term base.

[0.4.3] - 2018-10-02
====================

Added
-----
- Support delete all job translations.

[0.4.2] - 2018-03-16
====================

Added
-----
- Support get analysis by project.
- Support download anaylsis.
- Support set status of project.
- Support set status of job.

[0.4.1] - 2018-01-09
====================

Added
-----
- Support parameter filters on project list.

[0.4.0] - 2017-06-13
====================

Added
-----
- Support search endpoint of translation memory api.
