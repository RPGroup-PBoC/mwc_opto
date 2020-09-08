#%%
import numpy as np
import pandas as pd 
import bokeh.io
import seaborn as sns
from bokeh.models import * 
import bokeh.plotting
import photo.viz
import photo.stats
import bokeh.layouts
import tqdm
colors,  _ = photo.viz.bokeh_theme()
palette = [colors['red'], colors['blue'], colors['green'], colors['purple'],
           colors['light_red'], colors['light_blue'], colors['light_green'],
           colors['pale_red'], colors['pale_blue'], colors['dark_green']]

# Load the datasets 
traces = pd.read_csv('../../data/experiment_3_traces_subtracted.csv')
fits = pd.read_csv('../../data/experiment_3_hpd_fit.csv')
params = pd.read_csv('../../data/experiment_3_kinetic_parameters_summary.csv')
params.rename(columns={'dimension':'point_idx'}, inplace=True)

# For each unique replicate, assign colors
for g, d in tqdm.tqdm(traces.groupby(['power_density_nW'])):

    #Tie parameters to power density
    for i, point in enumerate(d['point_idx'].unique()):
        t = d[d['point_idx']==point]['experiment_time_s'].values[0]
        traces.loc[traces['point_idx']==point, 'color'] = palette[i]
        fits.loc[fits['point_idx']==point, 'color'] = palette[i]
        params.loc[params['point_idx']==point, 'color'] = palette[i]
        params.loc[params['point_idx']==point, 'power_density_nW'] = g
        params.loc[params['point_idx']==point, 'experiment_time_s'] = t

#%%
output = bokeh.io.output_file('../../figures/experiment_3_fit_explorer.html')
                              

# Define the data sources
trace_source = ColumnDataSource(traces)
fit_source = ColumnDataSource(fits)
sat_source = ColumnDataSource(params[params['parameter']=='saturation'])
sat_display = ColumnDataSource({'x':[], 'y':[], 'c':[]})
trace_display = ColumnDataSource({'x':[], 'y':[], 'c':[]})
fit_display = ColumnDataSource({'x':[], 'y1':[], 'y2':[], 'c':[]})
sat_display = ColumnDataSource({'x':[], 'y':[], 'c':[]})


# Set up the interactions
power_density_selector = Select(value='select', 
                                title='activation power density [nW/µm\u0082]',
                                options=list(np.sort(traces['power_density_nW'].unique()).astype(str)))

# set up the figure canvas. 
trace_plot = bokeh.plotting.figure(width=400, height=300,
                    x_axis_label='activation time [s]',
                    y_axis_label='background subtracted intensity [a.u.]')

trace_plot.y_range.range_padding_units='percent'
trace_plot.y_range.range_padding = 0.5 
sat_plot = bokeh.plotting.figure(width=400, height=300,
                                 x_axis_label='elapsed experiment time [s]',
                                 y_axis_label='inferred saturation intensity')
sat_plot.y_range.range_padding_units='percent'
sat_plot.y_range.range_padding = 1 

trace_plot.circle(x='x', y='y', color='c', source=trace_display,
                size=6, line_color='black', line_width=0.5)
sat_plot.line(x='x', y='y', color='black', source=sat_display,
                line_width=0.5)

sat_plot.circle(x='x', y='y', color='c', source=sat_display,
                size=6,  line_color='black', line_width=0.5)
trace_plot.varea(x='x', y1='y1', y2='y2', color='black', alpha=0.5,
                source=fit_display)

js = """
var density = power_density_select.value;
var trace_src = trace_source.data;
var trace_dsp = trace_display.data;
var fit_src = fit_source.data;
var fit_dsp = fit_display.data;
var sat_src = sat_source.data;
var sat_dsp = sat_display.data;

// Find indices of selected power density
var density_inds = getAllIndexes(trace_src['power_density_nW'], parseFloat(density));

// Update the display source. 
for (var i = 0; i < density_inds.length; i++) { 
    if (i == 0) { 
        trace_dsp['x'].length = 0;
        trace_dsp['y'].length = 0;
        trace_dsp['c'].length = 0;
    }

    trace_dsp['x'].push(trace_src['activation_time_s'][density_inds[i]]);
    trace_dsp['y'].push(trace_src['mch_median_sub'][density_inds[i]]);
    trace_dsp['c'].push(trace_src['color'][density_inds[i]]);
}
trace_display.change.emit();

var fit_inds = getAllIndexes(fit_src['power_density_nW'], parseFloat(density));
// Update the fit display source
for (var i = 0; i < fit_inds.length; i++) {
if (i == 0) { 
        fit_dsp['x'].length = 0;
        fit_dsp['y1'].length = 0;
        fit_dsp['y2'].length = 0;
        fit_dsp['c'].length = 0;
    }

    fit_dsp['x'].push(fit_src['activation_time_s'][fit_inds[i]]);
    fit_dsp['y1'].push(fit_src['hpd_min'][fit_inds[i]]);
    fit_dsp['y2'].push(fit_src['hpd_max'][fit_inds[i]]);
    fit_dsp['c'].push(fit_src['color'][fit_inds[i]])

}
fit_display.change.emit();


var sat_inds = getAllIndexes(sat_src['power_density_nW'], parseFloat(density));
console.log(sat_inds)
for (var i = 0; i < sat_inds.length; i++) {
if (i == 0) {
        sat_dsp['x'].length = 0;
        sat_dsp['y'].length = 0;
        sat_dsp['c'].length = 0;
    }
    sat_dsp['x'].push(sat_src['experiment_time_s'][sat_inds[i]]);
    sat_dsp['y'].push(sat_src['mean'][sat_inds[i]]);
    sat_dsp['c'].push(sat_src['color'][sat_inds[i]]);
}
sat_display.change.emit();

// Custom Function Definitions
function getAllIndexes(arr, val) {
    var indices = [], i = -1;
    while ((i = arr.indexOf(val, i+1)) != -1){
        indices.push(i);
    }
    return indices;
}
"""

# Load the callback and assign to the viz. 
cb = CustomJS(args={'power_density_select':power_density_selector,
                    'trace_source':trace_source, 'trace_display':trace_display, 
                    'fit_source': fit_source, 'fit_display': fit_display,
                    'sat_source': sat_source, 'sat_display': sat_display},
               code=js)

power_density_selector.js_on_change('value', cb)
plot_layout = bokeh.layouts.row(trace_plot, sat_plot)
lay = bokeh.layouts.column(power_density_selector, plot_layout)
bokeh.io.save(lay)

# %%
