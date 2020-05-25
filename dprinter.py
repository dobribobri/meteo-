# -*- coding: utf-8 -*-
#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#


def printDATA(DATA, columns=8, shortened=False, rows=4):
    for freq in DATA.keys():
        print('freq: {}'.format(freq))
        k = 0
        for i, item in enumerate(DATA[freq]):
            time, val = item
            print("{:.4f} {:.2f};\t".format(time, val), end='', flush=True)
            if (i+1) % columns == 0:
                print('')
                k += 1
                if shortened and (k + 1 == rows):
                    print('...')
                    try:
                        e_data = DATA[freq][len(DATA[freq]) - columns: len(DATA[freq])]
                    except IndexError:
                        break
                    for time, val in e_data:
                        print("{:.4f} {:.2f};\t".format(time, val), end='', flush=True)
                    print('')
                    break
        print('')
    print('')
    return


def printDATA2File(DATA, File, columns=8, shortened=False, rows=4):
    for freq in DATA.keys():
        File.write('freq: {}\n'.format(freq))
        k = 0
        for i, item in enumerate(DATA[freq]):
            time, val = item
            File.write("{:.4f} {:.2f};\t".format(time, val))
            if (i+1) % columns == 0:
                File.write('\n')
                k += 1
                if shortened and (k + 1 == rows):
                    File.write('...\n')
                    try:
                        e_data = DATA[freq][len(DATA[freq]) - columns: len(DATA[freq])]
                    except IndexError:
                        break
                    for time, val in e_data:
                        File.write("{:.4f} {:.2f};\t".format(time, val))
                    File.write('\n')
                    break
        File.write('\n')
    File.write('\n')
    return


def printList(data, columns=8, shortened=False, rows=4):
    k = 0
    for i, item in enumerate(data):
        time, val = item
        print("{:.4f} {:.2f};\t".format(time, val), end='', flush=True)
        if (i + 1) % columns == 0:
            print('')
            k += 1
            if shortened and (k + 1 == rows):
                print('...')
                try:
                    e_data = data[len(data) - columns : len(data)]
                except IndexError:
                    break
                for time, val in e_data:
                    print("{:.4f} {:.2f};\t".format(time, val), end='', flush=True)
                print('')
                break
    print('')
    return
