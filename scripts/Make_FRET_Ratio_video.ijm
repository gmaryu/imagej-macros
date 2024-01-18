// User inputs
Dialog.create("Make FRET Ratio video - Parameters");
Dialog.addMessage("Create FRET Ratio videos from imaging results. The script expects a folder \n" + 
				  "with subfolders corresponing to each microscope position. Please provide the \n" +
				  "following parameters:");
Dialog.addString("Full path to directory containing position folders", "");
Dialog.addString("Full path to directory where videos will be saved", "");
Dialog.addNumber("First position to analyze", 0);
Dialog.addNumber("Last position to analyze (For single position set this equal to first position)", 1);
Dialog.addNumber("First frame to be included in the video", 1);
Dialog.addNumber("Last frame to be included in the video", 10);
Dialog.addString("Name of the FRET channel (either 'FRET' or 'Custom')", "");
Dialog.addMessage("An AVI video will be created for each position with the following properties:");
Dialog.addNumber("FPS", 20);
Dialog.addNumber("Width in pixels", 576);
Dialog.addMessage("Script developed by the Yang Lab at the University of Michigan - 2024");
Dialog.show();

data_dir = Dialog.getString();
save_dir = Dialog.getString();
first_position = Dialog.getNumber();
last_position = Dialog.getNumber();
first_frame = Dialog.getNumber();
last_frame = Dialog.getNumber();
fret_name = Dialog.getString();

video_fps = Dialog.getNumber();
final_video_size = Dialog.getNumber();

// Output chosen parameters to log
print("---------- Parameters ----------");
print("Data directory:" + data_dir);
print("Save directory:" + save_dir);
print("Positions to analyze: " + first_position + " through " + last_position);
print("Frames to include: " + first_frame + " through " + last_frame);
print("FRET channel name: " + fret_name);
print("AVI video of " + final_video_size + "x" + final_video_size + " pixels at " + video_fps + " fps");


setBatchMode(true);

for (position=first_position; position<=last_position; position=position+1){
	// Position processing
	print("----------  Processing position: " + position + "  ----------");
	position_dir=data_dir+"/Pos"+position;
	// CFP stack
	print("Opening and resizing CFP images");
	File.openSequence(position_dir, "virtual filter=CFP");
	if (last_frame != nSlices) {
		run("Slice Remover", "first=" + (last_frame + 1) + 
						 " last=" + nSlices + 
						 " increment=1");
	}
	if (first_frame != 1) {
			run("Slice Remover", "first=1" + 
						 " last=" + (first_frame - 1) + 
						 " increment=1");
	}
	run("Size...", "width=" + final_video_size +
				   " height=" + final_video_size +
				   " depth=" + nSlices +
				   " constrain average interpolation=Bilinear");
	rename("CFP");
	
	// FRET 
	print("Opening and resizing FRET images");
	File.openSequence(position_dir, "virtual filter=" + fret_name);
	if (last_frame != nSlices) {
		run("Slice Remover", "first=" + (last_frame + 1) + 
						 " last=" + nSlices + 
						 " increment=1");
	}
	if (first_frame != 1) {
			run("Slice Remover", "first=1" + 
						 " last=" + (first_frame - 1) + 
						 " increment=1");
	}
	run("Size...", "width=" + final_video_size +
				   " height=" + final_video_size +
				   " depth=" + nSlices +
				   " constrain average interpolation=Bilinear");
	rename("FRET");
	
	// Create a mask highlighting where droplets are
	print("Creating droplet mask");
	selectWindow("FRET");
	run("Duplicate...", "duplicate");
	selectWindow("FRET-1");
	run("Auto Threshold", "method=Default white stack");
	run("32-bit");
	run("Divide...", "value=255 stack");
	rename("BINARY_MASK");
	
	// Apply mask to CFP and FRET
	imageCalculator("Multiply create 32-bit stack", "FRET", "BINARY_MASK");
	selectWindow("Result of FRET");
	rename("FRET_AFTER_MASK");
	
	imageCalculator("Multiply create 32-bit stack", "CFP", "BINARY_MASK");
	selectWindow("Result of CFP");
	rename("CFP_AFTER_MASK");
	
	// Close CFP and FRET stacks
	close("CFP");
	close("FRET");
	
	// Generate RATIO image
	print("Calculating FRET Ratio");
	imageCalculator("Divide create 32-bit stack", "FRET_AFTER_MASK","CFP_AFTER_MASK");
	selectWindow("Result of FRET_AFTER_MASK");
	rename("RATIO");
	run("physics");
	run("Enhance Contrast", "saturated=0.35"); // Intensity not comparable between positions
	
	// Close masked stacks
	close("CFP_AFTER_MASK");
	close("FRET_AFTER_MASK");
	
	// Make background black
	run("RGB Color");
	run("RGB Stack");
	run("Split Channels");
	selectWindow("C1-RATIO");
	run("32-bit");
	selectWindow("C2-RATIO");
	run("32-bit");
	selectWindow("C3-RATIO");
	run("32-bit");
	imageCalculator("Multiply stack", "C1-RATIO", "BINARY_MASK");
	selectWindow("C1-RATIO");
	rename("red");
	run("8-bit");
	imageCalculator("Multiply stack", "C2-RATIO", "BINARY_MASK");
	selectWindow("C2-RATIO");
	rename("green");
	run("8-bit");
	imageCalculator("Multiply stack", "C3-RATIO", "BINARY_MASK");
	selectWindow("C3-RATIO");
	rename("blue");
	run("8-bit");
	run("Merge Channels...", "c1=red c2=green c3=blue");
	
	// Close mask
	close("BINARY_MASK");
	
	// Rename and save
	print("Saving video");
	selectWindow("RGB");
	rename("FRET_Ratio_Pos" + position);
	run("AVI... ", "compression=JPEG frame=" + video_fps +
				   " save=" + save_dir + 
				   "/FRET_Ratio_Pos" + position + ".avi");
	close("FRET_Ratio_Pos" + position);
	print("Done!");
}