
import numpy as np
import pandas as pd
import glob

def ecdf(data):
    """
    Computes the empirical cumulative distribution function for a collection of provided data.

    Parameters
    ----------
    data : 1d-array, Pandas Series, or list
        One-dimensional collection of data for which the ECDF will
        be computed

    Returns
    -------
    x, y : 1d-arrays
        The sorted x data and the computed ECDF
    """
    return np.sort(data), np.arange(0, len(data)) / len(data)



def compute_statistics(df, varnames=None, logprob_name="logp"):
    r"""
    Computes the mode, hpd_min, and hpd_max from a pandas DataFrame. The value
    of the log posterior must be included in the DataFrame.
    """

    # Get the vars we care about.
    if varnames is None:
        varnames = [v for v in df.keys() if v is not "logp"]

    # Find the max of the log posterior.
    ind = np.argmax(df[logprob_name].values)

    # Instantiate the dataframe for the parameters.
    stat_df = pd.DataFrame(
        [], columns=["parameter", "mean", "median", "mode", "hpd_min", "hpd_max"]
    )
    for v in varnames:
        mode = df.iloc[ind][v]
        median = df[v].median()
        mean = df[v].mean()
        hpd_min, hpd_max = compute_hpd(df[v].values, mass_frac=0.95)
        stat_dict = dict(
            parameter=v,
            median=median,
            mean=mean,
            mode=mode,
            hpd_min=hpd_min,
            hpd_max=hpd_max,
        )
        stat_df = stat_df.append(stat_dict, ignore_index=True)

    return stat_df

def compute_hpd(trace, mass_frac):
    r"""
    Returns highest probability density region given by
    a set of samples.

    Parameters
    ----------
    trace : array
        1D array of MCMC samples for a single variable
    mass_frac : float with 0 < mass_frac <= 1
        The fraction of the probability to be included in
        the HPD.  For hreple, `massfrac` = 0.95 gives a
        95% HPD.

    Returns
    -------
    output : array, shape (2,)
        The bounds of the HPD

    Notes
    -----
    We thank Justin Bois (BBE, Caltech) for developing this function.
    http://bebi103.caltech.edu/2015/tutorials/l06_credible_regions.html
    """
    # Get sorted list
    d = np.sort(np.copy(trace))

    # Number of total samples taken
    n = len(trace)

    # Get number of samples that should be included in HPD
    n_samples = np.floor(mass_frac * n).astype(int)

    # Get width (in units of data) of all intervals with n_samples samples
    int_width = d[n_samples:] - d[: n - n_samples]

    # Pick out minimal interval
    min_int = np.argmin(int_width)

    # Return interval
    return np.array([d[min_int], d[min_int + n_samples]])

def compute_deciles(trace):
    """
    Computes the set of deciles from a given trace.

    Parameters
    ----------
    trace: array 
        1D array of values from which the deciles will be computed.

    Returns
    -------
    deciles: dict 
        A dictionary for each decile with the lower and upper bound values.
    """
    
    intervals = {'90th': [5, 95],
                 '80th': [10, 90],
                 '70th': [15, 85],
                 '60th': [20, 80],
                 '50th': [25, 75],
                 '40th': [30, 70],
                 '30th': [35, 65],
                 '20th': [40, 60],
                 '10th': [45, 55],
                 '1st': [49.5, 50.5]}

    deciles = {'100th': [trace.min(), trace.max()]}

    for k, v in intervals.items():
        deciles[k] = np.percentile(trace, v)
    
    return deciles

    