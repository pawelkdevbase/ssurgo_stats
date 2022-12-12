import os
import pandas as pd
import geopandas as gpd
import numpy as np
from zipfile import ZipFile
import shutil

from dcts import states, dct
from config import DOWNLOAD_FOLDER



DFO = pd.DataFrame(
    {
        'state': [],
        'table': [],
        'col': [],
        'type': [],
        'empty': [],
        'rows': [],
        'val_cnt': [],
        'minv': [],
        'maxv': [],
        'unique_vals': [],
        'duplicates': [],
        'type_ok': [],
    }
)

DFU = pd.DataFrame(
    {
        'state': [],
        'table': [],
        'col': [],
        'type': [],
        'vals': [],
    }
)


def state_stats(st):
    df = DFO.copy()
    dfuu = DFU.copy()
    ind = 0
    for itab in dct.keys():
        cc = gpd.read_file(
            f'gSSURGO_{st}.gdb', layer=itab, ignore_geometry=True
        )
        for col, tp in dct[itab].items():
            #print(itab, col,tp)
            #print(np.unique(cc[col].fillna(''), return_counts=True))
            #print(cc[col].describe())
            #print('Non zero: ', np.count_nonzero(cc[col]))

            fillval = -9999 if tp in ['int', 'float'] else ''
            cnts = np.unique(cc[col].fillna(fillval), return_counts=True)
            emp = 'Y' if (cnts[0].shape[0]==1 and cnts[0][0]==fillval) else 'N'
            val_ucnt = 0 if emp == 'Y' else cnts[0].shape[0]
            val_ucnt = max(0, val_ucnt if fillval not in cnts[0] else val_ucnt - 1)
            val_cnt = np.count_nonzero(cc[col])
            if emp == 'N':
                try:
                    minv = None if tp == 'str' else np.delete(cnts[0], np.where(cnts[0]==fillval)).min()
                    maxv = None if tp == 'str' else np.delete(cnts[0], np.where(cnts[0]==fillval)).max()
                except ValueError:
                    minv = None
                    maxv = None
            type_comp = 'Y'
            try:
                cc[col].fillna(fillval).astype(tp)
            except:
                type_comp = 'F'
                print(itab, col, '----f----')

            iidct = {
                'state': st,
                'table': itab,
                'col': col,
                'type': tp,
                'empty': emp,
                'rows': cc.shape[0],
                'val_cnt': val_cnt,
                'minv': minv,
                'maxv': maxv,
                'unique_vals': val_ucnt,
                'duplicates': 'Y' if True in (cnts[1] > 1) else 'N',
                'type_ok': type_comp,

            }
            df = pd.concat([df, pd.DataFrame(iidct, index=[ind])], axis=0)

            if val_ucnt > 0:
                unq = np.delete(cnts[0], np.where(cnts[0]==fillval))
                if tp != 'str':
                    unq = map(lambda xx: round(xx, 4), unq)
                undct = {
                    'state': st,
                    'table': itab,
                    'col': col,
                    'type': tp,
                    'vals': ','.join(map(str, unq))
                }
                dfuu = pd.concat([df, pd.DataFrame(undct, index=[ind])], axis=0)
            ind += 1
    return df, dfuu


if __name__ == '__main__':
    df = DFO.copy()
    dfuu = DFU.copy()
    for st in states:
        pth = os.path.join(DOWNLOAD_FOLDER, f'gSSURGO_{st}.zip')
        if not os.path.isfile(pth):
            continue
        print(st)
        with ZipFile(pth, 'r') as zip:
            zip.extractall("./")
        dfc, dfui = state_stats(st)
        df = pd.concat([df, dfc], ignore_index=True)
        dfuu = pd.concat([dfuu, dfui], ignore_index=True)
        shutil.rmtree(f'gSSURGO_{st}.gdb/')

    df.to_csv('report.csv', index_label='id')
    dfuu.to_csv('report_uv.csv', index_label='id')
