import gzip
import geopandas as gpd
import matplotlib.pyplot as plt

style = {
	"hv_circuits" : dict(color="r",linestyle="-",linewidth=0.3),
	"mv_circuits" : dict(color="b",linestyle="-",linewidth=0.2),
	"lv_circuits" : dict(color="k",linestyle="-",linewidth=0.1),
	"ram_circuits" : dict(color="g",linestyle=":",linewidth=0.1),
	"substations" : dict(color="b",marker=".",markersize=0.2),
}
plt.figure(figsize=(48,36),dpi=600)
ax = plt.gca()
for name in style:
	print("Processing",name,end="...",flush=True)
	data=gpd.read_file(gzip.GzipFile(f"SCE/{name}.geojson.gz","rb"))
	ax = data.plot(ax=ax,label=name.replace("_"," ").title(),**style[name])
	print("ok")
plt.grid()
plt.legend()
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.savefig("SCE/circuits.png")
