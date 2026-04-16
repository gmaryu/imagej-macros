import os

base_dir = r"\\biop-qiongy-nas.biop.lsa.umich.edu/qiongy-data/users/Gembu/data/20260330_dilution"

pos = 0

while True:
    pos_dir = os.path.join(base_dir, "Pos{}".format(pos))
    
    if not os.path.exists(pos_dir):
        print("Folder not found:", pos_dir)
        break
    
    print("Checking:", pos_dir)
    
    for fname in os.listdir(pos_dir):
        fpath = os.path.join(pos_dir, fname)
        
        if os.path.isfile(fpath) and "RFP-T" in fname:
            print("Deleting:", fpath)
            os.remove(fpath)
    
    pos += 1

print("Done.")