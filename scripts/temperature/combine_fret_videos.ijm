first_pos=0
last_pos=13;
total_pos=14;
tube_width=700; // px
tube_length=1000; // px
order_flipped=false // whether first_pos goes to the leftmost or rightmost place
data_dir="D:\\Experiments\\Temperature_project\\03-01-24\\Video";
save_dir="D:\\Experiments\\Temperature_project\\03-01-24\\Video\\Combined";
save_name="10-ng-ul-mRNA"

for (pos=first_pos; pos<=last_pos; pos=pos+1){
	// Open Ratio video
	open(data_dir+"/Pos"+pos+"_Ratio.tif");
	// Resize
	frames = nSlices();
	run("Size...", "width=&tube_width height=&tube_length depth=&frames average interpolation=Bilinear");
	// Flip along the x-axis
	run("Flip Horizontally", "stack");
}
// Combine all videos
stack_counter=1
stack_str=""
for (pos=first_pos; pos<=last_pos; pos=pos+1){
	if (order_flipped){
		current_pos = last_pos - pos + first_pos;
	} else {
		current_pos = pos;
	}
	stack_str += "stack_" + stack_counter + "=Pos" + current_pos + "_Ratio.tif ";
	stack_counter += 1;
}
run("Multi Stack Montage...", stack_str + " rows=1 columns=&total_pos");
// Close all videos
for (pos=first_pos; pos<=last_pos; pos=pos+1){
	close("Pos" + pos + "_Ratio.tif");
}
selectImage("Montage of Stacks");
run("mpl-plasma");
// Save result
saveAs("Tiff", save_dir + "/" + save_name + ".tif");