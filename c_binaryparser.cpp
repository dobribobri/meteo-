////
//// Mikhail T. Smirnov, Dobroslav P. Egorov
//// Kotel'nikov Institute of Radio-engineering and Electronics of RAS
//// 2019
//


//---------------------------------------------------------------------------

#include <iostream>
#include <stdio.h>
#include <string>
#include <math.h>
#include <time.h>
#include <string.h>
#include <clocale>

void ReadCalibr(std::string fn, double *CalibrTemp, double *CalibrFreqs,
        double ***CalibrVal, double *Kqi, double *Kiq, double *Nulls);

std::string double2datetime(double TDateTimeVal);


void c_parse(std::string fPath, std::string cPath, std::string outPath) {
    setlocale(LC_ALL, "en_US.UTF-8");

    FILE *fd, *fc, *fo;
    int TempSet[2];
    int static num, nw;
    float static Time, fadc[2], freq, freqp;
    int i, j;

    double CalibrFreqs[32];

    double OutIhot, OutQhot, OutIcold, OutQcold;
    double Ihot, Qhot, Icold, Qcold;

    static double val[2];
    int nt, nf, ns;
    static double ai[32], aq[32], bi[32], bq[32];

    double* CTime = new double[1001*32];
    double* cpa = new double[1001*32];
    double** tbi = new double *[1001];
    double** tbq = new double *[1001];
    double** ui = new double *[1001];
    double** uq = new double *[1001];
    for(i = 0; i < 1001; i++) {
        tbi[i] = new double[32];
        tbq[i] = new double[32];
        ui[i] = new double[32];
        uq[i] = new double[32];
    }

    int* freqg = new int[32];
    for(i = 0; i < 31; i++) freqg[i] = 9800 + 100*i;

    std::string fn_in = fPath;
    fd=fopen(fn_in.c_str(), "rb");

    fread(TempSet, 4, 2, fd);

    freqp = 9800;
    val[0] = 0.;
    val[1] = 0.;
    nt = 0;
    nf = 0;
    ns = 0;
    double CTime_c = 0.;
    double CTa = 0.;
    float cpa_c = 0.;
    CTime[31*ns+nf] = 0.;
    cpa[31*ns+nf] = 0;

    std::cout << "Чтение данных..." << std::endl;

    while(fread(&num, 4, 1, fd)) {
        fread(&nw, 4, 1, fd);
        fread(&Time, 4, 1, fd);
        fread(&CTime_c, 8, 1, fd);
        fread(fadc, 4, 2, fd);
        fread(&freq, 4, 1, fd);
        if(freq == freqp) {
            val[0] += fadc[0];
            val[1] += fadc[1];
            CTa += CTime_c;
            cpa_c += Time;
            nt++;
        } else {
            nf = (int)(freqp - 9800)/100;
            ui[ns][nf] = val[0] / nt;
            uq[ns][nf] = val[1] / nt;
            cpa[31*ns + nf] = cpa_c / nt;
            CTime[31*ns + nf] = CTa / nt;
            if(freqp > freq) ns++;
            nt = 0;
            val[0] = 0.;
            val[1] = 0.;
            freqp = freq;
            cpa_c = 0.;
            CTa = 0.;
        }
    }

    fclose(fd);



    nf = 3;
    std::string fn_cal = cPath;
    double*** CalibrVal = new double**[nf];
    for(i = 0; i < nf; i++) {
        CalibrVal[i] = new double*[32];
        for (j = 0; j < 31; j++)
            CalibrVal[i][j] = new double[3];
    }

    double* CalibrTemp = new double[2];
    double* Kqi = new double[32];
    double* Kiq = new double[32];
    double* Nulls = new double[2];

    // ReadCalibr(fn_cal, CalibrTemp, CalibrFreqs, CalibrVal, Kqi, Kiq, Nulls);
    
    int Calibr_N_Freq, Calibr_N_Temp;
    char str[1000];

    std::cout << "Чтение файла калибровки..." << std::endl;

    fc = fopen(fn_cal.c_str(), "rt");

    int fStep = 0;
    Calibr_N_Temp = 0;
    if(fc != NULL) do {
        if(fscanf(fc, "%s\n", str)!=1) break;
        if(fStep == 0) {
            if     (strstr(str, "N_Freq")) fStep=10;
            else if(strstr(str, "CalibrTable")) fStep=40;
            else if(strstr(str, "IsolationCorrectTable")) fStep=50;
            else if(strstr(str, "Nulls")) fStep=60;
        } else {
        if     (fStep == 10) sscanf(str, "%u", &Calibr_N_Freq);
        else if(fStep == 40) {
            fscanf(fc, "%lf", &CalibrTemp[Calibr_N_Temp]);

            for(int i = 0; i < Calibr_N_Freq; i++) {
              fscanf(fc, "%lf %lf %lf", &CalibrFreqs[i], &CalibrVal[0][i][Calibr_N_Temp],
                                                         &CalibrVal[1][i][Calibr_N_Temp]);
            }
            Calibr_N_Temp++;
        }
        else if(fStep == 50) {
            for(int i = 0; i < Calibr_N_Freq; i++) {
              fscanf(fc, "%lf", &Kqi[i]);
              fscanf(fc, "%lf", &Kiq[i]);
            }
        }
        else if(fStep == 60) {
            fscanf(fc, "%lf %lf", &Nulls[0], &Nulls[1]);
        }
        fStep = 0;
        }
    } while(1);
    fclose(fc);



    std::cout << "Вычисление калибровочных коэффициентов..." << std::endl;

    for(i = 0; i < 31; i++) {
        OutIhot =(CalibrVal[0][i][0]-Nulls[0]);
        OutQhot=(CalibrVal[1][i][0]-Nulls[1]);
        OutIcold=(CalibrVal[0][i][1]-Nulls[0]);
        OutQcold=(CalibrVal[1][i][1]-Nulls[1]);

        Ihot=(OutIhot-Kqi[i]*OutQhot)/(1-Kqi[i]*Kiq[i]);
        Qhot=(OutQhot-Kiq[i]*OutIhot)/(1-Kqi[i]*Kiq[i]);
        Icold=(OutIcold-Kqi[i]*OutQcold)/(1-Kqi[i]*Kiq[i]);
        Qcold=(OutQcold-Kiq[i]*OutIcold)/(1-Kqi[i]*Kiq[i]);
        bi[i]=(CalibrTemp[0]-CalibrTemp[1])/
                        (Ihot-Icold);
        bq[i]=(CalibrTemp[0]-CalibrTemp[1])/
                        (Qhot-Qcold);
        ai[i]=CalibrTemp[1]-bi[i]*Icold;
        aq[i]=CalibrTemp[1]-bq[i]*Qcold;
    }



    std::cout << "Выполнение калибровки..." << std::endl;

    for(i = 0; i < ns; i++)
        for(j = 0; j < 31; j++) {
            double I = (ui[i][j]-Nulls[0]-Kqi[j]*(uq[i][j]-Nulls[1]))/(1-Kqi[j]*Kiq[j]);
            double Q = (uq[i][j]-Nulls[1]-Kiq[j]*(ui[i][j]-Nulls[0]))/(1-Kqi[j]*Kiq[j]);
            tbi[i][j] = ai[j] + bi[j]*I;
            tbq[i][j] = aq[j] + bq[j]*Q;
    }

    std::string fn_out = outPath;

    std::cout << "Сохранение файлов..." << std::endl;
                
    fo=fopen(fn_out.c_str(), "w");

    std::string strb="Date\tTime\tmsec\tTime_P\tFreqg\tFreq1\tTbI\tFreq2\tTbQ";

    fprintf(fo, "%s\n", strb.c_str());
    int nsb = 0;
    int nse = 1000;

    for(i = nsb; i < nse; i++)
        for(j = 0; j < 31; j++) {
            fprintf(fo, "%s\t%f\t%d\t%d\t%10.3f\t%d\t%10.3f\n",
                        double2datetime(CTime[i*31 + j]).c_str(),
                        cpa[31*i + j], freqg[j],
                        freqg[j]*2+1600, tbi[i][j], freqg[j]*2-1600, tbq[i][j]);
    }

    fclose(fo);
    
}

/*
void ReadCalibr(std::string fn, double *CalibrTemp, double *CalibrFreqs,
        double ***CalibrVal, double *Kqi, double *Kiq, double *Nulls) {
    // ReadCalibr(fn_cal, CalibrTemp, CalibrFreqs, CalibrVal, Kqi, Kiq, Nulls);
}
*/

/*
def Double2TDateTime(double):
    fractionalPart, integerPart = math.modf(double)

    DATE = date_0 + timedelta(days=integerPart)
    hh = fractionalPart // (1 / 24)
    fractionalPart -= hh / 24
    mm = fractionalPart // (1 / (24 * 60))
    fractionalPart -= mm / (24 * 60)
    ss = fractionalPart // (1 / (24 * 60 * 60))
    fractionalPart -= ss / (24 * 60 * 60)
    ms = np.round(fractionalPart / (1 / (24 * 60 * 60 * 1000)))
    if ms == 1000:
        ms = 999
    return TDateTime(DATE.day, DATE.month, DATE.year, hh, mm, ss, ms)
*/

std::string double2datetime(double TDateTimeVal) {
    double fractionalPart, integerPart;
    fractionalPart = modf(TDateTimeVal, &integerPart);
    struct tm t { 0 };
    // t.tm_mday = 0;
    // t.tm_mon = 0;
    // t.tm_year = 0;
    // 1 Jan, 1900 = 30 Dec, 1899 + 2 days
    t.tm_mday += integerPart - 1; //WHY

    // std::cout << "I " << integerPart << std::endl;
    // std::cout << "f " << fractionalPart << std::endl;

    int hh = (int)(fractionalPart / (1. / 24.));
    fractionalPart -= double(hh) / 24.;
    int mm = (int)(fractionalPart / (1. / (24. * 60.)));
    fractionalPart -= double(mm) / (24. * 60.);
    int ss = (int)(fractionalPart / (1. / (24. * 60. * 60.)));
    fractionalPart -= double(ss) / (24. * 60. * 60.);
    int ms = (int)round(fractionalPart / (1. / (24. * 60. * 60. * 1000.)));
    if (ms == 1000) ms = 999;    

    t.tm_hour = hh;
    t.tm_min = mm;
    t.tm_sec = ss;
    mktime(&t);

    char _datetime[20];
    strftime(_datetime, 20, "%Y.%m.%d %H:%M:%S", &t);

    std::string result = std::string(_datetime) + std::string(" ") + std::to_string(ms);

    return result;
}

//---------------------------------------------------------------------------

