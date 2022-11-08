import xarray as xr
from xhistogram.xarray import histogram
import numpy as np

def calc_histogram(tracer,volume,tracer_bins=None,normalize=True):
    '''
    Derive volumetric histogram for 'tracer' in 'tracer_bins'.
    Returned histogram is normalized by bin width unless normalize=False.
    
    PARAMETERS
        tracer xr.DataArray
        volume xr.DataArray
        tracer_bins None or np.array
        normalize bool
    
    RETURN
        hs xr.DataArray
    '''
    # Get name of tracer
    tracername=tracer.name
    # Derive bins if not specified
    if tracer_bins is None:
        tracer_bins = np.linspace(tracer.min().values,tracer.min().values,50)
    # Get dimensions to sum over (all dimensions and remove 'time')
    histdims = list(tracer.dims)
    histdims.remove('time')
    # Histogram
    hs = histogram(tracer,bins=[tracer_bins],weights=volume,dim=histdims)
    # Assign upper bound as coordinate
    hs = hs.assign_coords({tracername+'_bin':tracer_bins[1:]})
    
    if normalize:
        # Normalize each bin by bin width
        dtracervals = np.diff(tracer_bins)
        dtracer = xr.DataArray(dtracervals,
                               dims=tracername+'_bin',
                               coords={tracername+'_bin':hs[tracername+'_bin']})
        hs = hs/dtracer
    return hs

def invert_and_interpolate_1Dhistogram(hs,percentiles=None):
    '''
    Take cumulative sum of volumetric histogram for a tracer and invert
    to give tracer value as a function of volume percentile.
    
    PARAMETERS
        hs xr.DataArray
        percentiles None or np.array
        
    RETURNS
        tp xr.DataArray
        
    '''
    # Define percentiles if not specified
    if percentiles is None:
        percentiles = np.linspace(1,100,100)
    # Get name of tracer bins
    dim = hs.dims[0]
    # Invert histogram
    inverted = xr.DataArray(hs[dim],dims='percentile',coords={'percentile':hs.values})
    # Find points where percentile coordinate is not monotonically increasing
    diffvals=inverted['percentile'].diff('percentile').values
    diffvals=np.append(1,diffvals) # Append value to start to align difference with latter bin
    diff = xr.DataArray(diffvals,dims=['percentile'],coords={'percentile':inverted['percentile']})
    # Drop points in original histogram where percentile not monotonically increasing
    # (necessary to interpolate onto uniform grid)
    inverted_dropped = inverted.where(diff>0,drop=True)
    # Interpolate onto uniform percentiles
    tp = inverted_dropped.interp({'percentile':percentiles})
    return tp


def calc_tracerpercentile(tracer,volume,tracer_bins=None,percentiles=None,ascending=True):
    '''
    Calculate 'tracer' as a function of volume percentile. This involves binning volume
    in tracer space, deriving the cumulative sum over tracer values, then inverting.
    
    PARAMETERS
        tracer xr.DataArray
        volume xr.DataArray
        tracer_bins None or np.array
        percentiles None or np.array
        ascending bool
            In cumulative volumetric sum, arrange tracer in ascending order.
        
    RETURN
        tp xr.DataArray
    '''
    # Get name of tracer
    tracername=tracer.name
    # Derive histogram
    hs = calc_histogram(tracer,volume,tracer_bins=tracer_bins,normalize=True)
    # Sort to ascending or descending
    hs = hs.sortby(tracername+'_bin',ascending=ascending)
    # Cumulative volumetric sum
    VT = hs.sum(tracername+'_bin')
    hs_frac = 100*hs.cumsum(tracername+'_bin')/VT
    print("Loading volumetric histogram.")
    hs_frac.compute()
    # Loop through time, get tracer percentile at each time
    tp = xr.DataArray(dims=['percentile','time'],
                      coords={'percentile':percentiles,'time':hs_frac['time']})
    print("Inverting for tracer percentile at each time.")
    for t in range(len(hs_frac['time'])):
        hsnow = hs_frac.isel(time=t)
        tpnow = invert_and_interpolate_1Dhistogram(hsnow)
        tp[:,t] = tpnow
        
    return tp,VT

def calc_extensive(tp,VT,prefactor=1):
    '''
    Calculate the extensive tracer quantity based on the tracer percentile.
    For example, if tracer=temperature, calc_extensive can be used to return 
    heat content as a function of tracer percentile.
    
    PARAMETERS
        tp xr.DataArray
        VT float
        prefactor int, float
            Any prefactor for integration, e.g. density or heat capacity
    
    RETURN
        Tp xr.DataArray
    '''
    
    return 0.01*VT*(tp*prefactor).cumsum('percentile')