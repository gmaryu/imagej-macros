tot_pos=24;
data_dir="D:\\Experiments\\Temperature_project\\03-01-24\\Processed_Data";
save_dir="D:\\Experiments\\Temperature_project\\03-01-24\\Video";

for (pos=0; pos<tot_pos; pos=pos+1){
	// Open FRET images
	File.openSequence(data_dir+"/Pos"+pos+"/", "virtual filter=FRET");
	rename("Pos"+pos+"_FRET");
	// Open CFP images
	File.openSequence(data_dir+"/Pos"+pos+"/", "virtual filter=CFP");
	rename("Pos"+pos+"_CFP");
	// Divide FRET by CFP
	imageCalculator("Divide create 32-bit stack", "Pos"+pos+"_FRET","Pos"+pos+"_CFP");
	selectWindow("Result of Pos"+pos+"_FRET");
	run("16-bit");
	run("Enhance Contrast", "saturated=0.35");
	run("Apply LUT", "stack");
	run("8-bit");
	run("mpl-plasma");
	rename("Pos"+pos+"_Ratio");
	saveAs("Tiff", save_dir+"\\Pos"+pos+"_Ratio.tif");
	close("*");
}