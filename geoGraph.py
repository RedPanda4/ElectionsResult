import geopandas as gpd
import get_data
import pandas_bokeh

fp = "DATA/Mapa_admistrativo_portugal1.1.shp"
data = gpd.read_file(fp)
data = data.merge(get_data.get_results, on='Dicofre')
file_out = 'OUT/{0}.html'
d = get_data.get_partie_acronym[15:]
print(d)
print(list(data.head()))
for i in d:
	#pandas_bokeh.output_notebook()
	pandas_bokeh.output_file(file_out.format(i))
	data.plot_bokeh(
		figsize=(1600,900),
		simplify_shapes=10,
		dropdown=[i, ],
		colormap="RdYlBu",
		hovertool_columns=['Freguesia','Concelho', 'Distrito', i],
		colormap_uselog=True,
		line_color = 'black',
		line_alpha = 0,
	)
