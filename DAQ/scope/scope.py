import TeledyneLeCroyPy
import plotly.express as px
import pandas

o = TeledyneLeCroyPy.LeCroyWaveRunner('VICP::90.147.203.158')

print(o.idn) # Prings e.g. LECROY,WAVERUNNER9254M,LCRY4751N40408,9.2.0

o.set_tdiv('1NS')
o.set_vdiv(1,0.2) #amplitude in volts

print('Waiting for trigger...')
o.wait_for_single_trigger() # Halt the execution until there is a trigger.

data = {}
for n_channel in [1]:
    data[n_channel] = o.get_waveform(n_channel=n_channel)

wf = []
for n_channel in data:
    for i,_ in enumerate(data[n_channel]['waveforms']):
        df = pandas.DataFrame(_)
        df['n_segment'] = i
        df['n_channel'] = n_channel
        wf.append(df)
wf = pandas.concat(wf)

fig = px.line(
wf,
x = 'Time (s)',
y = 'Amplitude (V)',
color = 'n_segment',
facet_col = 'n_channel',
markers = True,
)

fig.write_html('deleteme.html') # Open this plot to visualize the waveform(s).