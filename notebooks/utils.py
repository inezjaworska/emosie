import os
import re
import random
from itertools import product

import numpy as np
import pandas as pd


def round2step(vals, step=0.001):
	return np.round(vals / step) * step


def trim(val, vmin, vmax):
	return max([min([val, vmax]), vmin])


def to_percent(val):
	# currently assumes val is 0 - 1
	s = str(val * 100)
	return s.split('.')[0] + '%'


def trim_df(df, colname='time', value=0.):
	# find last trial
	fin = np.where(df[colname] == value)[0]
	if np.any(fin):
		df = df[0:fin[0]]
	return df


def group(vec):
	in_grp = False
	group_lims = list()
	for ii, el in enumerate(vec):
		if in_grp and not el:
			in_grp = False
			group_lims.append([start_ind, ii-1])
		elif not in_grp and el:
			in_grp = True
			start_ind = ii
	return np.array(group_lims)


# TODO - maybe add shuffle=False
def grow_sample(smp, num):
	"""take `num` elements from sample `smp` similar to
	random.sample but even if `num` > len(`smp`).

	Example:
	--------
	> grow_sample([0.2, 0.4], 5)
	array([0.2, 0.4, 0.2, 0.4, 0.4])
	"""
	smp = np.asarray(smp)
	smp_len = len(smp)
	if smp_len > num:
		return np.array(random.sample(list(smp), num))

	div = int(np.floor(num / smp_len))
	rem = num - div * smp_len
	rem_el = np.array(random.sample(list(smp), rem))
	base_el = np.tile(smp, div)
	return np.concatenate((base_el, rem_el))


def fillz(val, num, addpos='front'):
    '''
    fillz(val, num)
    adds zero to the beginning of val so that length of
    val is equal to num. val can be string, int or float
    '''

    # if not string - turn to a string
    if not isinstance(val, basestring):
        val = str(val)

    # add zeros
    ln = len(val)
    if ln < num:
        addz = '0' * (num - ln)
        if addpos == 'front':
            return addz + val
        elif addpos == 'end':
            return val + addz
    else:
        return val


def reformat_params(params):
    if isinstance(params, list):
        n_params = len(params)
        params = np.array(list(product(*params)))
    elif isinstance(params, np.ndarray):
        assert params.ndim == 1
        params = params[:, np.newaxis]
    return params


def continue_dataframe(pth, fl):
	# test if file exists:
	flfl = os.path.join(pth, fl)
	ifex = os.path.isfile(flfl)

	if not ifex:
		return ifex
	else:
		# load with pandas and take first column
		try:
			df = pd.read_excel(flfl)
		except TypeError:
			# old version of pandas (0.13 and below):
			xl = pd.ExcelFile(flfl)
			sht_nm = xl.sheet_names[0]  # see all sheet names
			df = xl.parse(sht_nm, convert_float=False)
		# some columns have to be converted to float now
		colnames = ['fixTime', 'targetTime', 'SMI', 'maskTime',
			'orientation', 'ifcorrect']
		df.loc[:, colnames] = df.loc[:, colnames].astype('Int32')

		col = df.columns
		col = df[col[0]]

		# test first col for nonempty
		isempt, = np.nonzero(np.isnan(col))
		if isempt.any():
			# return dataframe and first trial to resume from:
			return df, isempt[0] + 1
		else:
			# here it should return something special
			# not to overwrite the file (because file
			# absent and file presnt but finished re-
			# sponses are identical)
			return False


def free_filename(pth, subj, givenew = True):
	# list files within the dir
	fls = os.listdir(pth)
	n_undsc_in_subj = 0
	ind = -1
	while True:
		try:
			ind = subj['symb'][ind+1:-1].index('_')
			n_undsc_in_subj += 1
		except (IndexError, ValueError):
			break

	# predefined file pattern
	subject_pattern = subj['symb'] + '_' + r'[0-9]+'

	# check files for pattern
	reg = re.compile(subject_pattern)
	used_files = [reg.match(itm).group() for ind, itm in enumerate(fls) \
		if not (reg.match(itm) == None)]
	used_files_int = [int(f.split('_')[1 + n_undsc_in_subj][0:2])
					  for f in used_files]

	if givenew:
		if len(used_files) == 0:
			# if there are no such files - return prefix + S01
			return 1, subj['symb'] + '_01'
		else:
			# check max used number:
			mx = 1
			for temp in used_files_int:
				if temp > mx:
					mx = temp

			return mx + 1, subj['symb'] + '_' + fillz(mx + 1, 2)
	else:
		return not subj['ind'] in used_files_int


def check_color(color):
	if isinstance(color, str):
		if color.startswith('seaborn_'):
			col_dict = dict()
			col_dict['green'] = (0.3333333333333333, 0.6588235294117647,
							   0.40784313725490196)
			col_dict['red'] = (0.7686274509803922, 0.3058823529411765,
								 0.3215686274509804)
			for k in col_dict.keys():
				if color.endswith(k):
					return col_dict[k]
			raise ValueError("Could not find seaborn color for {}."\
							 .format(color))
	return color


def time_shuffle(start=1.5, end=5.0, every=0.05, times=6, shuffle=True):
	'''time_shuffle is used to keep track of all fixation times
	that should be used in the experiment 2.

	parameters
	----------
	start - float; start value
	end   - float; end value
	every - float; step value
	times - int; number of times each value should be used

	example
	-------
	>>> times = time_shuffle(start=1.5, end=3., every=0.5,
			times=2, shuffle=False)
	[ 1.5  2.   2.5  3.   1.5  2.   2.5  3. ]
	'''
	times = np.tile(np.arange(start, end + 0.000001, every), times)
	if shuffle:
		np.random.shuffle(times)
	return times
