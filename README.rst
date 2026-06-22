========
Pickling
========

``make_battery_pickle.py`` reads in .wpilog file(s) from the roboRIO, and generates a pickle file of an array of
``BatteryDataSample`` (defined in ``utilities.py``).
``analyze.py`` can read the pickle files a *lot* faster than it can read .wpilog files.

================
Analysis of data
================

``analyze.py`` reads in either pickle files of ``BatteryDataSample`` or raw wpilog files from the battery tester, and
generates summary files of the tests.
For each test, you get 2 summary files named ``#nnn_yyyymmdd-hhmmss.json`` and ``#nnn_yyyymmdd-hhmmss.json``,
where ``nnn`` is the battery number,
and ``hhmmdd-hhmmss`` is the timestamp of when the test was started, **expressed in the local timezone**.
This will not match the timestamp from the ``FRC_yyyymmdd_hhmmss.wpilog`` input file,
because that timestamp is expressed in relation to UTC (4 or 5 hours advanced from Eastern time),
and the ``FRC*`` timestamp is when the driver station connected to the battery tester, not when the test started.

The json file is similar to::

    {
     "battery_id": 113,
     "capacity_estimate": 463995.12169967016,
     "cutoff_criteria": "mean of last 10 idle batteryVoltage < 12.3125",
     "rint_reverse_end": 0.023843281297826667,
     "rint_reverse_start": 0.01985737035241987,
     "start_time": "20260407-195040"
    }

The data items may vary as the battery tester and ``analyze.py`` evolve.

======
Rollup
======

``rollup.py`` reads all the `#nnn_yyyymmdd-hhmmss.json` files, and produced a CSV file
with a summary.