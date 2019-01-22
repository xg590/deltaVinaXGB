import os
import sys
import click
import pandas as pd

if sys.platform == "linux":
    from software_path_linux import path_python
    from software_path_linux import path_obabel
elif sys.platform == "darwin":
    from software_path_mac import path_python
    from software_path_mac import path_obabel
from convert_file import RF20_main
import run_features
from run_features import run_features
import run_models
from run_models import run_model
from run_models import get_output
import click




@click.command()
@click.option("--model", default = "model_allfeatures", show_default = True, help = "model name")
@click.option("--modeldir",default = "../Model", show_default = True, help = "absolute model directory")
@click.option("--datadir", default = "../Test_linux", show_default= True, help = "absolute data directory")
@click.option("--decoydatadir", default = None, show_default = True, help = "decoy datadir, if decoy == True, please provide decoydatadir, and datadir is the directory for reference file")
@click.option("--pdbid", default = "01", show_default = True, help = "pdbid, ligand input should be pdbid_ligand.mol2 or sdf,\nprotein input should be pdbid_protein_all.pdb")
@click.option("--outfile", default = "score.csv",show_default = True, help = "output filename")
@click.option("--runfeatures",is_flag = True, show_default = True, help = "run features calculation")
@click.option("--water", default = "rw", show_default = True, help = "water type")
@click.option("--opt", default = "wo", show_default = True, help = "opt type")
@click.option("--decoy", is_flag = True, help = "decoy flag, if True, water = 'n', opt = 'n'")
@click.option("--rewrite", is_flag = True, help = "rewrite protein_RW, ligand_opt, generated confs or not")
@click.option("--average",is_flag = True, help = "average for 10 models")
@click.option("--modelidx", default = "1", show_default = True, help = "model index")

def main(model, modeldir, datadir, decoydatadir,pdbid, outfile, runfeatures, water, opt, decoy, rewrite, average, modelidx):
    datadir = os.path.realpath(datadir)
    print("pdb index: " + pdbid  )
    print("file directory: " + datadir)
    if decoy:
        decoydatadir = os.path.realpath(decoydatadir)
        print("pdb index: " + pdbid  )
        print("ref directory: " + datadir)
        print("decoy directory: " + decoydatadir)
    
    print("output filename : " + outfile)
    olddir = os.getcwd()
    if runfeatures:
        run_features(datadir, decoydatadir, pdbid, water_type = water, opt_type = opt, rewrite = rewrite, decoy = decoy)
        os.chdir(olddir)



    if decoy:
        opt = "n"

    if opt == "wo":
        data_type = ["","_min","_min_RW"]
    elif opt == "o":
        data_type = ["","_min"]
    else:
        data_type = [""]
    
    if decoy:
        datadir = decoydatadir
        data_type_new = ["_decoys" + i for i in data_type]
    else:
        data_type_new = data_type
    out = []
    for idx, i in enumerate(data_type):
        inf = "Input" + data_type_new[idx] + ".csv"
        test_new = run_model(inf,datadir,i,model_dir = modeldir, model_name = model, average = average, model_index = modelidx, decoy = decoy)  
        outRF = "RF" + data_type_new[idx] + ".csv"
        RF20_main(datadir,inf,outRF, decoy)
        outRF_new = open(os.path.join(datadir,"RF" + data_type_new[idx] + "_new.csv"),"w")
        outRF_new.write("pdb,idx,RF20" + i + "\n")
       	lines = [line for line in open(os.path.join(datadir,outRF))]
        outRF_new.write("".join([pdbid + "," + ",".join(line.split(",")[1:]) for line in lines[1:]]))
        outRF_new.close()
        os.system("mv " + os.path.join(datadir,"RF" + data_type_new[idx] + "_new.csv") + " " + os.path.join(datadir, "RF" + data_type_new[idx] + ".csv"))
         
        out.append(test_new)
        if decoy:
            outRF = pd.read_csv(os.path.join(datadir,"RF" + data_type_new[idx] + ".csv"),dtype = {"pdb":str,"idx":str})
        else:
            outRF = pd.read_csv(os.path.join(datadir,"RF" + data_type_new[idx] + ".csv"),dtype = {"pdb":str})
        out.append(outRF)


    os.chdir(datadir)
    get_output(out,outfile,decoy)
    os.system("rm " +  "RF*")
    os.chdir(olddir)



if __name__ == "__main__":

    main()



