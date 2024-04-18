tot_pos=28;
min_ratio=0.40;
max_ratio=1.85;
data_dir="Z:\\Users\\Franco\\Experiments\\04-05-24\\Ratio";
save_dir="Z:\\Users\\Franco\\Experiments\\04-05-24\\Video";

for (pos=0; pos<tot_pos; pos=pos+1){
	// Open Ratio stack
	open(data_dir+"/Pos"+pos+"_Ratio.tif");
	// Normalize
	setMinAndMax(min_ratio, max_ratio);
	run("16-bit");
	run("Apply LUT", "stack");
	run("8-bit");
	run("mpl-plasma");
	rename("Pos"+pos+"_Ratio");
	saveAs("Tiff", save_dir+"\\Pos"+pos+"_Ratio.tif");
	close("*");
}