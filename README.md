# meteo-

See also https://github.com/dobribobri/atmrad - cloudfield modeling.

Processing of microwave radiometric measurements of atmospheric radio emission (18-27 GHz)

! run firstly<br>
$ python3 c_setup.py build_ext --inplace
<br>
for building cython-extensions (c++ modules)

Example:<br>
$ python main.py -Y 2019 -M 08 -D 23 --hh 18 --mm 30 --range --sameday --H1 20 --m1 00 --saveplots --sfreport --wreport --erase


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
                        './meteo_1.csv', './meteo_2.csv'
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

<hr/><br/>

"P22M" dataset preparation:

1. Prepare local meteo data - meteo_1.csv & meteo_2.csv. Use <b><font color='cyan'>prepare_local_meteo.ipynb</font></b>
2. Update meteo-. Run <pre><font color='cyan'>python main.py --update_meteo</font></pre>
3. Collect, calibrate and preprocess all existing files from server. Run <pre><font color='cyan'>python collect.py</font></pre>
Wait! If script finishes before all the files are processed, just restart it. (Note, you'll need more than 250Gb of free disk space)
4. Delete all files in <b>./bf</b> and <b>./tf</b> subfolders to save disk space (optional).
5. Parse radiosonde data stored in HTML-format at ./Dolgoprudnyj subfolder. Run <pre><font color='cyan'>python Dolgoprudnyj_parse.py</font></pre>
6. Bring all the altitude profiles measured via radiosonde to a single altitude grid. 
Run <pre><font color='cyan'>python Dolgoprudnyj_prepare.py</font></pre>
7. Generate dumps. Run <pre><font color='cyan'>python prepare_multi.py</font></pre>
8. Clone atmrad repo<br/><pre>.../meteo-$ cd ..
.../$ git clone https://github.com/dobribobri/atmrad </pre>
9. Compute true TWV values from radiosonde profiles and update dumps. 
Use <b><font color='cyan'>prepare_q_real.ipynb</font></b> (optional)
10. Select the time intervals you are interested in (seasons, individual days, time of day e t.c.). Specify <b>path_to_dump_dir</b>.
Use <b><font color='cyan'>select.ipynb</font></b>
11. Solve the inverse problem to retrieve TWV and LWC values from the selected microwave radiometry data.
Run <pre><font color='cyan'>python prepare_qw_dualfreq.py -P '%path_to_dump_dir%'</font></pre>
or <pre><font color='cyan'>python prepare_qw_multifreq.py -R 17.25 --lm --ms --path_to_dump_dir '%path_to_dump_dir%'</font></pre>
For more information type <pre><font color='cyan'>python prepare_qw_multifreq.py --help</font></pre>
Also consider setting environment variable <pre>.../meteo-$ export TF_GPU_ALLOCATOR=cuda_malloc_async</pre>
