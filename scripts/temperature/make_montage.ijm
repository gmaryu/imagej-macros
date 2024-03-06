tot_pos=24;
data_dir="Z:\\Users\\Franco\\Experiments\\04-21-23\\Video";
save_dir="Z:\\Users\\Franco\\Experiments\\04-21-23\\Kymograph\\Montage"

for (pos=0; pos<tot_pos; pos=pos+1){
	// Open Ratio video
	open(data_dir+"/Pos"+pos+"_Ratio.tif");
	// Bin
	height = getHeight();
	run("Bin...", "x=1 y=&height z=1 bin=Average");
	// Make montage
	time_frames = nSlices();
	run("Make Montage...", "columns=1 rows=&time_frames scale=1");
	// Save
	saveAs("Tiff", save_dir+"/Pos"+pos+"_Montage.tif");
	close("*");
	
}
