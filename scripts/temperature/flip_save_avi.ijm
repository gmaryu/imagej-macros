tot_pos=24;
data_dir="D:\\Experiments\\Temperature_project\\03-01-24\\Video";
save_dir="D:\\Experiments\\Temperature_project\\03-01-24\\Video\\AVIs"

for (pos=0; pos<tot_pos; pos=pos+1){
	// Open Ratio video
	open(data_dir+"/Pos"+pos+"_Ratio.tif");
	// Flip along the x-axis
	run("Flip Horizontally", "stack");
	// Save AVI
	run("AVI... ", "compression=JPEG frame=20 save="+save_dir+"\\Pos"+pos+"_Ratio_vid.avi");
	close("*");
}