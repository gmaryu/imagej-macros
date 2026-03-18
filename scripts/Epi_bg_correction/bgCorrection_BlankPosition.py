#@ String input_root
#@ String output_root

import os
from ij import IJ
from ij.plugin import ImageCalculator
from ij.io import FileSaver

# ============================================================
# Settings
# ============================================================

background_pos_name = "Pos0"
allowed_ext = ".tif"
process_only_pos_folders = True

# true -> negative values to 0 and save as 16-bit image
clip_to_16bit = True

# ============================================================
# Helper functions
# ============================================================

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def is_target_file(fname):
    return fname.lower().endswith(allowed_ext)

def should_process_pos_folder(folder_name):
    if folder_name == background_pos_name:
        return False
    if not process_only_pos_folders:
        return True
    return folder_name.startswith("Pos")

# ============================================================
# Main
# ============================================================

input_root = os.path.abspath(input_root)
output_root = os.path.abspath(output_root)
bg_dir = os.path.join(input_root, background_pos_name)

if not os.path.isdir(input_root):
    raise Exception("Input root does not exist: " + input_root)

if not os.path.isdir(bg_dir):
    raise Exception("Background folder not found: " + bg_dir)

ensure_dir(output_root)

calc = ImageCalculator()

print("Input root:  " + input_root)
print("Output root: " + output_root)
print("Background:  " + bg_dir)

n_processed = 0
n_skipped = 0
n_missing_bg = 0

for current_dir, subdirs, files in os.walk(input_root):

    folder_name = os.path.basename(current_dir)

    if folder_name == background_pos_name:
        continue

    if not should_process_pos_folder(folder_name):
        continue

    tif_files = [f for f in files if is_target_file(f)]
    if len(tif_files) == 0:
        continue

    rel_dir = os.path.relpath(current_dir, input_root)
    out_dir = os.path.join(output_root, rel_dir)
    ensure_dir(out_dir)

    for fname in tif_files:
        sample_path = os.path.join(current_dir, fname)
        bg_path = os.path.join(bg_dir, fname)

        if not os.path.exists(bg_path):
            print("[Missing background] " + bg_path)
            n_missing_bg += 1
            n_skipped += 1
            continue

        sample_imp = IJ.openImage(sample_path)
        bg_imp = IJ.openImage(bg_path)

		# skip bright field images
        if any(x in fname for x in ["4-BF", "0-BF"]):
        	out_path = os.path.join(out_dir, fname)
        	FileSaver(sample_imp).saveAsTiff(out_path)
    		sample_imp.close()
    		continue

        if sample_imp is None:
            print("[Failed to open sample] " + sample_path)
            n_skipped += 1
            continue

        if bg_imp is None:
            print("[Failed to open background] " + bg_path)
            sample_imp.close()
            n_skipped += 1
            continue

        # check if processing single-frame image
        if sample_imp.getNSlices() != 1 or bg_imp.getNSlices() != 1:
            print("[Skipped: stack detected] " + sample_path)
            sample_imp.close()
            bg_imp.close()
            n_skipped += 1
            continue

        if (sample_imp.getWidth() != bg_imp.getWidth()) or (sample_imp.getHeight() != bg_imp.getHeight()):
            print("[Size mismatch] sample: {} bg: {}".format(sample_path, bg_path))
            sample_imp.close()
            bg_imp.close()
            n_skipped += 1
            continue


        result_imp = calc.run("Subtract create", sample_imp, bg_imp)

        if result_imp is None:
            print("[Subtraction failed] " + sample_path)
            sample_imp.close()
            bg_imp.close()
            n_skipped += 1
            continue

        if clip_to_16bit:
            IJ.run(result_imp, "Min...", "value=0")
            IJ.run(result_imp, "16-bit", "")

        out_path = os.path.join(out_dir, fname)
        ok = FileSaver(result_imp).saveAsTiff(out_path)

        if ok:
            print("[Saved] " + out_path)
            n_processed += 1
        else:
            print("[Save failed] " + out_path)
            n_skipped += 1

        sample_imp.close()
        bg_imp.close()
        result_imp.close()

print("===================================")
print("Done")
print("Processed:   {}".format(n_processed))
print("Skipped:     {}".format(n_skipped))
print("Missing bg:  {}".format(n_missing_bg))
print("===================================")