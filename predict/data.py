#!/usr/bin/env python

import os
import os.path as pt
import pandas as pd
import re
import subprocess as sp
import numpy as np

from predict import hdf



def read_pos(path, dataset, chromo):
    group = pt.join(dataset, 'pos', str(chromo))
    pos = pd.read_hdf(path, group)
    return pos.values


def list_chromos(path, dataset):
    group = pt.join(dataset, 'pos')
    return hdf.ls(path, group)


def read_cpg(path, chromos=None, nrows=None):
    d = pd.read_table(path, header=None, usecols=[0, 1, 2], nrows=nrows,
                      dtype={0: np.str, 1: np.int32, 2: np.float32})
    d.columns = ['chromo', 'pos', 'value']
    if chromos is not None:
        d = d.loc[d.chromo.isin(chromos)]
    d['chromo'] = [chromo_to_int(x) for x in d.chromo]
    d['value'] = np.round(d.value)
    assert np.all((d.value == 0) | (d.value == 1)), 'Invalid methylation states'
    d = pd.DataFrame(d, dtype=np.int32)
    return d


def read_annos(filename, *args, **kwargs):
    d = pd.read_table(filename, header=None, usecols=[0, 1, 2])
    d.columns = ['chromo', 'start', 'end']
    d = format_bed(d, *args, **kwargs)
    return d


def format_bed(d, rm_unknown=True, sort=True):
    d['chromo'] = format_chromos(d['chromo'])
    if rm_unknown:
        d = d.loc[d.chromo != 0]
    if sort:
        d = d.sort(['chromo', 'start'])
    return d


def chromo_to_int(chromo):
    if type(chromo) is int:
        return chromo
    chromo = chromo.lower()
    if chromo == 'x':
        return 100
    elif chromo == 'y':
        return 101
    elif chromo in ['mt', 'm']:
        return 102
    elif chromo.isdigit():
        return int(chromo)
    else:
        return 0 # unknown


def format_chromo(chromo, to_int=True):
    if type(chromo) is int:
        return chromo
    chromo = chromo.lower()
    chromo = re.sub('^chr', '', chromo)
    if to_int:
        chromo = chromo_to_int(chromo)
    return chromo


def format_chromos(chromos, *args, **kwargs):
    return [format_chromo(x, *args, **kwargs) for x in chromos]