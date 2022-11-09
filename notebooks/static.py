import numpy as np

def tracer_args():
    return {
        'o2':{'bins':np.linspace(0,0.4,400),
              'units':'molm-3',
              'gfdl_ppname':'ocean_cobalt_omip_tracers_year_z_1x1deg',
              'linestyle':'-'},
        'o2sat':{'bins':np.linspace(0,0.4,400),
                 'units':'molm-3',
                 'gfdl_ppname':'ocean_cobalt_omip_tracers_year_z_1x1deg',
                 'linestyle':'--'}
    }

def dataset_args():
    return {
        'gobai':{'color':'tab:blue'},
        'esm4':{'color':'tab:orange'}
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