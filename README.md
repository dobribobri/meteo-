# meteo-
Processing of microwave radiometric measurements of atmospheric radio emission (18-27 GHz)

! run firstly<br>
$ python3 c_setup.py build_ext --inplace
<br>
for building cython-extensions (c++ modules)

Example:<br>
$ python3 main.py -Y 2019 -M 08 -D 23 --hh 18 --mm 30 --range --sameday --H1 20 --m1 00 --saveplots --sfreport --wreport --erase


<pre>
usage: main.py [-h] [--meteo METEO [METEO ...]] [--update_meteo]
               [--update_calibr] [-Y YEAR] [-M MONTH] [-D DAY] [-H HH] [-m MM]
               [-s SS] [--range] [--sameday] [--Y1 Y1] [--M1 M1] [--D1 D1]
               [--H1 H1] [--m1 M1] [--s1 S1] [--erase] [--eraserar]
               [--erasedat] [--erasetxt] [--nosf] [--noweather] [--noqw]
               [--closeplots] [--noplots] [--saveplots] [--plotroot PLOTROOT]
               [--savereports] [--tbreport] [--sfreport] [--wreport]
               [--qwreport] [--qwsfreport] [--reportroot REPORTROOT]
               [--txtparsermode TXTPARSERMODE] [--rangespec RANGESPEC]
               [--recycle RECYCLE]

optional arguments:
  -h, --help            show this help message and exit
  --meteo METEO [METEO ...]
                        Choose CSV-files of weather data. Using: [--meteo
                        filepath_1 filepath_2 ... filepath_N ]. Obtain
                        meteodata: http://orash.ire.rssi.ru/meteo/index.php
  --update_meteo        Update weather data with --meteo csv-files. If --meteo
                        is missing (by default), following files are used:
                        &apos;./meteo_1_2017-01-01_2019-09-01.csv&apos;,
                        &apos;./meteo_2_2017-01-01_2019-09-01.csv&apos;
  --update_calibr       Download files used for primary calibration of
                        measurements.
  -Y YEAR, --year YEAR  Year in YYYY format (2017 by default).
  -M MONTH, --month MONTH
                        Month in MM format (08 by default).
  -D DAY, --day DAY     Day in DD format (01 by default).
  -H HH, --hh HH        Hour in hh format (05 by default).
  -m MM, --mm MM        Minute in mm format (09 by default).
  -s SS, --ss SS        Second in ss format (34 by default).
  --range               Set interval of measurements. If necessary, several
                        consecutive measurement sessions are combined into
                        one. For specifying the interval beginning, the values
                        under keys -Y, -M, -D, -H, -m, -s are used. For
                        specifying the end, please, use keys --Y1, --M1, --D1,
                        --H1, --m1, --s1 (listed below).
  --sameday             The keys --Y1, --M1, --D1 will be set equal to -Y, -M,
                        -D.
  --Y1 Y1               Year in YYYY format (2017 by default). Use with
                        --range
  --M1 M1               Month in MM format (08 by default). Use with --range
  --D1 D1               Day in DD format (01 by default). Use with --range
  --H1 H1               Hour in hh format(07 by default). Use with --range
  --m1 M1               Minute in mm format (00 by default). Use with --range
  --s1 S1               Second in ss format (00 by default). Use with --range
  --erase               Add keys --eraserar, --erasedat and --erasetxt.
  --eraserar            Delete RAR-files.
  --erasedat            Delete DAT-files.
  --erasetxt            Delete TXT-files.
  --nosf                Do not calculate structural functions.
  --noweather           Do not load weather data.
  --noqw                No moisture content analysis.
  --closeplots          Show and close plots immediately.
  --noplots             Do not process plots.
  --saveplots           Save plots to --plotroot directory.
  --plotroot PLOTROOT   Where to store images? By default: ./pic/
  --savereports         Save all reports to --reportroot directory.
  --tbreport            Save report on brightness temperatures.
  --sfreport            Save report on structural functions.
  --wreport             Save weather report.
  --qwreport            Save report on moisture content parameters.
  --qwsfreport          Save report on structural functions of moisture
                        content parameters.
  --reportroot REPORTROOT
                        Where to store reports? By default: ./reports/
  --txtparsermode TXTPARSERMODE
                        Set TXT-parser special mode.
  --rangespec RANGESPEC
                        Specify interval of measurements with string of &apos;YYYY-
                        MM-DD : hh:mm - hh:mm&apos; format.
  --recycle RECYCLE     Specify how many times brightness temperature series
                        are repeated.
</pre>