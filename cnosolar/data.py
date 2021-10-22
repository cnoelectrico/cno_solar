import pvlib
import pandas as pd

def psm3_to_df(file_name, prefix, start_year, end_year, tz, sort_index=False):
    '''
    Docstring
    '''
    frames = []
    for i in range(start_year, end_year):
        frames.append(pvlib.iotools.read_psm3(filename=f'./data/{file_name}/{prefix}_{i}.csv')[0])

    df = pd.concat(frames)
    df = df.fillna(0)
    df = df.tz_convert(tz)
    
    if sort_index == True:
        df = df.sort_index()

    return df

def test_load_csv(file_name, tz):
    '''
    Docstring
    '''
    df = pd.read_csv(filepath_or_buffer=f'./data/{file_name}.csv', 
                     sep=',',
                     decimal='.',
                     header='infer',
                     index_col='Unnamed: 0')

    df.index = pd.DatetimeIndex(data=df.index)
    df = df.tz_convert(tz)
    df = df.fillna(0)

    return df

def load_csv(file_name, tz):
    '''
    Docstring
    '''
    df = pd.read_csv(filepath_or_buffer=file_name, 
                     sep=',',
                     decimal='.',
                     header='infer',
                     index_col='Unnamed: 0')

    df.index = pd.DatetimeIndex(data=df.index)
    df = df.tz_convert(tz)
    df = df.fillna(0)

    return df