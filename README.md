# meteo-
Processing of microwave radiometric measurements of atmospheric radio emission (18-27 GHz)

! run firstly<br>
$ python3 c_setup.py build_ext --inplace
<br>
for building cython-extensions (c++ modules)
---
Example:<br>
$ python3 main.py -Y 2019 -M 08 -D 23 --hh 18 --mm 30 --range --sameday --H1 20 --m1 00 --noqw --nocturb --saveplots --savereports
---

<pre>usage: main.py [-h] [--meteo METEO [METEO ...]] [--update_meteo]
               [--update_calibr] [-Y YEAR] [-M MONTH] [-D DAY] [-H HH] [-m MM]
               [-s SS] [--range] [--sameday] [--Y1 Y1] [--M1 M1] [--D1 D1]
               [--H1 H1] [--m1 M1] [--s1 S1] [--erase] [--nosf] [--noweather]
               [--noqw] [--continuous] [--noplots] [--saveplots]
               [--plotroot PLOTROOT] [--savereports] [--reportroot REPORTROOT]
               [--txtparsermode TXTPARSERMODE] [--noconnection]

optional arguments:
  -h, --help            show this help message and exit
  --meteo METEO [METEO ...]
                        Выбор файлов метеорологической базы данных (CSV).
                        Использование: [--meteo путь_к_файлу_CSV_1
                        путь_к_файлу_CSV_2 ... путь_к_файлу_CSV_N ].
                        Метеоданные в формате CSV можно получить по адресу
                        URL: http://orash.ire.rssi.ru/meteo/index.php
  --update_meteo        Обновить метеорологическую базу данных. В процессе
                        обновления будут использованы CSV файлы, указанные под
                        флагом --meteo. Если флаг --meteo отсутствует (по
                        умолчанию), то используются следующие файлы:
                        &apos;./meteo_1_2017-01-01_2019-09-01.csv&apos;,
                        &apos;./meteo_2_2017-01-01_2019-09-01.csv&apos;
  --update_calibr       Обновить базу файлов (первичной) калибровки (загрузка
                        с сервера).
  -Y YEAR, --year YEAR  Год в формате YYYY (2017 по умолчанию).
  -M MONTH, --month MONTH
                        Месяц в формате MM (08 по умолчанию).
  -D DAY, --day DAY     День в формате DD (01 по умолчанию).
  -H HH, --hh HH        Час в формате hh (05 по умолчанию).
  -m MM, --mm MM        Минута в формате mm (09 по умолчанию).
  -s SS, --ss SS        Секунда в формате ss (34 по умолчанию).
  --range               Задать временной интервал измерений. При
                        необходимости, несколько последовательных
                        измерительных сеансов будут объеденены в один. За дату
                        и время начала диапазона (временного интервала)
                        принимаются значения под ключами -Y, -M, -D, -H, -m,
                        -s. Для указания даты и времени окончания диапазона
                        используйте --Y1, --M1, --D1, --H1, --m1, --s1
                        (приведены ниже).
  --sameday             Ключи --Y1, --M1, --D1 устанавливаются равными -Y, -M,
                        -D.
  --Y1 Y1               Год в формате YYYY (2017 по умолчанию). Не
                        используется без --range
  --M1 M1               Месяц в формате MM (08 по умолчанию). Не используется
                        без --range
  --D1 D1               День в формате DD (01 по умолчанию). Не используется
                        без --range
  --H1 H1               Час в формате hh (07 по умолчанию). Не используется
                        без --range
  --m1 M1               Минута в формате mm (57 по умолчанию). Не используется
                        без --range
  --s1 S1               Секунда в формате ss (00 по умолчанию). Не
                        используется без --range
  --erase               Удалить файлы данных измерительного сеанса по
                        окончанию работы программы.
  --nosf                Не вычислять значения структурных функций.
  --noweather           Не подгружать данные погоды (--noqw будет устновлен
                        автоматически).
  --noqw                Не вычислять значения интегральных параметров
                        влагосодержания атмосферы.
  --continuous          Закрыть графики сразу же после отрисовки.
  --noplots             Вообще не рисовать графики.
  --saveplots           Сохранять отрисованные графики в директорию --plotroot
  --plotroot PLOTROOT   Куда сохранять изображения? По умолчанию: ./pic/
  --savereports         Сохранять обобщённые данные графиков в текстовом виде
                        (сохранять отчёты). Директория для сохранения:
                        --reportroot
  --reportroot REPORTROOT
                        Куда сохранять отчёты? По умолчанию: ./reports/
  --txtparsermode TXTPARSERMODE
                        Режим парсера текстовых файлов.
  --noconnection        Не подключаться к серверу.
</pre>
