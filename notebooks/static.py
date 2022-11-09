import numpy as np

def tracer_args():
    return {
        'o2':{'bins':np.linspace(0,0.4,400),
                 'units':'molm-3'},
        'o2sat':{'bins':np.linspace(0,0.4,400),
                     'units':'molm-3'}
    }

def direction_name(ascending):
    if ascending:
        direction = 'ascending'
    else:
        direction = 'descending'
    return direction

def path_tp(tracername,dataset,ascending):
    outdir = '../data/tracerpercentiles/'
    filename = '.'.join([tracername,dataset,direction_name(ascending),'nc'])
    return outdir+filename