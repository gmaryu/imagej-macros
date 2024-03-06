first_pos=15;
last_pos=29;
total_pos=15;
final_height=500 // px
final_width=1000; // px
order_flipped=false // whether first_pos goes to the leftmost or rightmost place
data_dir="Z:\\Users\\Franco\\Experiments\\01-19-24\\Kymograph\\Montage";
save_dir="Z:\\Users\\Franco\\Experiments\\01-19-24\\Kymograph";
save_name="2-uM-Wee1-Inh"

File.openSequence(data_dir, "virtual");
first_slice=first_pos + 1;
last_slice=last_pos + 1;
rename("Original montage");
run("Slice Keeper", "first=&first_slice last=&last_slice increment=1");
if (order_flipped){
	run("Reverse");
}
rename("Montage sequence");
run("Make Montage...", "columns=&total_pos rows=1 scale=1");
run("Rotate 90 Degrees Left");
run("Size...", "width=&final_width height=&final_height depth=1 average interpolation=Bilinear");
run("Flip Vertically");
close("Original montage");
close("Montage sequence");
saveAs("Tiff", save_dir + "/" + save_name + ".tif");