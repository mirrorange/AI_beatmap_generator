import os
import zipfile

def zip_dir(dirname,zipfilename):
  filelist = []
  if os.path.isfile(dirname):
    filelist.append(dirname)
  else :
    for root, dirs, files in os.walk(dirname):
      for name in files:
        filelist.append(os.path.join(root, name))
  zf = zipfile.ZipFile(zipfilename, "w", zipfile.zlib.DEFLATED)
  for tar in filelist:
    arcname = tar[len(dirname):]
    zf.write(tar,arcname)
  zf.close()

for i in os.listdir("PreParedData"):
    dirpath = os.path.join("PreParedData",i)
    filepath = os.path.join("PreParedData",i + ".mcz")
    zip_dir(dirpath,filepath)
    print(filepath)