# @ImageJ IJ
import os
from ij import IJ
from ij import ImagePlus

# =========================================================
# User settings
# =========================================================
experiment_path = "/PATH_TO_EXPERIMENT_DATA_DIR" # This contains multiple positions
output_root = "/PATH_TO_OUTPUT_DIR" # New directories for each position will be generated

# Reference channel must be first
channels = ["2-CFP", "4-FRET", "5-YFP", "0-BF", "1-BFP"]

# Use all frames
# If None, automatically use all frames found for the reference channel
#frame_range = None
frame_range = (0, 399)

#positions = ["Pos0"]
positions = [pos for pos in os.listdir(experiment_path) if os.path.isdir(os.path.join(experiment_path, pos))]

transformation_mode = "[Rigid Body]"

# =========================================================
# Helper functions
# =========================================================
def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def close_image_safely(imp):
    if imp is not None:
        try:
            imp.changes = False
        except:
            pass
        try:
            imp.close()
        except:
            pass

def get_channel_file_list(position_path, channel):
    """
    Return sorted list of filenames for one channel in a position folder.
    Assumes 1 frame = 1 file, like img_000000123_2-CFP_000.tif
    """
    files = []
    for fn in os.listdir(position_path):
        if (channel in fn) and fn.lower().endswith(".tif"):
            files.append(fn)
    files.sort()
    return files

def get_effective_frame_range(position_path, ref_channel, frame_range):
    ref_files = get_channel_file_list(position_path, ref_channel)
    n_files = len(ref_files)

    if n_files == 0:
        raise IOError("No files found for reference channel '{}' in {}".format(ref_channel, position_path))

    if frame_range is None:
        return (1, n_files), (0, n_files - 1)

    start0, end0 = frame_range

    if start0 < 0 or end0 >= n_files or start0 > end0:
        raise ValueError("frame_range {} is invalid for {} files".format(frame_range, n_files))

    # For ImageJ
    start1 = start0 + 1
    end1   = end0 + 1

    return (start1, end1), (start0, end0)

def open_channel_sequence(position_path, channel, end_frame):
    """
    Open an image sequence for one channel from one position.
    """
    cmd = "open=[{}] number={} scale=100 file={} sort".format(
        position_path, end_frame, channel
    )
    IJ.run("Image Sequence...", cmd)
    imp = IJ.getImage()
    return imp

def subset_stack(stack, frame_range):
    start_frame, end_frame = frame_range
    total_frames = stack.getStackSize()
    if start_frame < 1 or end_frame > total_frames or start_frame > end_frame:
	    raise ValueError("Frame range {} is out of bounds for stack with {} frames.".format(frame_range, total_frames))
    IJ.selectWindow(stack.getTitle())
    IJ.run(stack, "Make Substack...", "slices={}-{}".format(start_frame, end_frame))
    substack = IJ.getImage()
    return substack

def save_registered_stack_as_individual_files(stack, output_path, original_filenames):
    """
    Save each slice of stack using the original filenames into one output folder.
    """
    ensure_dir(output_path)

    n_slices = stack.getStackSize()
    if n_slices != len(original_filenames):
    	raise ValueError("Number of slices ({}) does not match number of filenames ({})".format(n_slices, len(original_filenames)))

    for i in range(1, n_slices + 1):
        ip = stack.getStack().getProcessor(i).duplicate()
        single_imp = ImagePlus(original_filenames[i - 1], ip)

        out_name = original_filenames[i - 1]
        out_path = os.path.join(output_path, out_name)

        IJ.saveAs(single_imp, "Tiff", out_path)
        close_image_safely(single_imp)

# =========================================================
# Core registration
# =========================================================
def register_stack(position_path, output_path, channels, frame_range):
    ensure_dir(output_path)
	
    ref_channel = channels[0]
    tf_path = os.path.join(output_path, "TransformationMatrices.txt")

    #print("--------------------------------------------------")
    #print("Processing position: " + position_path)
    #print("Reference channel: " + ref_channel)
    
    (effective_frame_range, zero_based_range) = get_effective_frame_range(position_path, ref_channel, frame_range)
    start1, end1 = effective_frame_range
    start0, end0 = zero_based_range
    
	#print("Using frames (0-based): {}-{}".format(start0, end0))
	#print("Using frames (ImageJ): {}-{}".format(start1, end1))

    ref_files_all = get_channel_file_list(position_path, ref_channel)
    ref_files_subset = ref_files_all[start0:end0 + 1]

    # -----------------------------------------------------
    # 1) Open reference channel and calculate transformations
    # -----------------------------------------------------
    ref_full = None
    ref_sub = None
    ref_registered = None

    try:
        ref_full = open_channel_sequence(position_path, ref_channel, end1)
        ref_sub  = subset_stack(ref_full, (start1, end1))
        ref_sub.show()

        IJ.run(
            ref_sub,
            "MultiStackReg",
            "action_1=Align "
            "file_1=[{}] "
            "stack_2=None "
            "action_2=Ignore "
            "file_2=[{}] "
            "transformation={} "
            "save".format(tf_path, tf_path, transformation_mode)
        )

        ref_registered = IJ.getImage()
        save_registered_stack_as_individual_files(ref_registered, output_path, ref_files_subset)
        print("Saved registered reference channel.")

    finally:
        if ref_registered is not None and ref_registered != ref_sub:
            close_image_safely(ref_registered)
        close_image_safely(ref_sub)
        close_image_safely(ref_full)

    # -----------------------------------------------------
    # 2) Apply the same transforms to all channels
    # -----------------------------------------------------
    for channel in channels:
        print("Applying transform to channel: " + channel)
        start_frame, end_frame = frame_range
        ch_files_all = get_channel_file_list(position_path, channel)
        if len(ch_files_all) < end_frame:
            raise IOError("Channel '{}' has fewer files ({}) than required end_frame ({})".format(channel, len(ch_files_all), end_frame))
        
        ch_files_subset = ch_files_all[start0:end0 + 1]
        ch_full = None
        ch_sub = None
        ch_registered = None

        try:
            ch_full = open_channel_sequence(position_path, channel, end1)
            ch_sub  = subset_stack(ch_full, (start1, end1))
            ch_sub.show()

            IJ.run(
                ch_sub,
                "MultiStackReg",
                "action_1=[Load Transformation File] "
                "file_1=[{}] "
                "stack_2=None "
                "action_2=Ignore "
                "file_2=[{}] "
                "transformation={}".format(tf_path, tf_path, transformation_mode)
            )

            ch_registered = IJ.getImage()
            save_registered_stack_as_individual_files(ch_registered, output_path, ch_files_subset)
            print("Saved channel: " + channel)

        finally:
            if ch_registered is not None and ch_registered != ch_sub:
                close_image_safely(ch_registered)
            close_image_safely(ch_sub)
            close_image_safely(ch_full)

# =========================================================
# Batch runner
# =========================================================
def batch_register_positions(experiment_path, output_root, positions, channels, frame_range):
    for pos in positions:
        position_path = os.path.join(experiment_path, pos)
        output_path   = os.path.join(output_root, pos)

        if not os.path.isdir(position_path):
            print("Skipping missing position folder: " + position_path)
            continue

        try:
            register_stack(position_path, output_path, channels, frame_range)
        except Exception as e:
            print("Error processing {}: {}".format(pos, str(e)))

# =========================================================
# Run
# =========================================================
batch_register_positions(experiment_path, output_root, positions, channels, frame_range)
print("Done.")