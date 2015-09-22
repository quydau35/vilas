import os
from subprocess import call
from subprocess import check_output
from Utils import DataController
from Utils import CheckPoint


class GromacsMD(object):
  dataController = DataController() 
  # Get version of gromacs
  GroLeft = ''
  GroRight = ''
  GroVersion = ''
  GroOption = ''
  repeat_times = 0

  def mdrun(self):
    main_path = self.dataController.getdata('path ')
    runfolders = check_output('ls '+main_path+'/run/', shell = True).splitlines()


    for x in range(0,len(runfolders)):
      # Check point to show log
      CheckPoint.point = runfolders[x]
      run_path = main_path+'/run/'+runfolders[x]
      ligandCurrent = runfolders[x].split('_')[1] #A01

      groCmd = ''
      #Run em
      if os.path.isfile(run_path+'/em.gro') is False: 
        groCmd += self.GroLeft+'grompp'+self.GroRight+' -maxwarn 20 -f mdp/minim.mdp -c solv_ions.gro -p topol.top -o em.tpr \n'
        groCmd += self.GroLeft+'mdrun'+self.GroRight+' '+self.GroOption+' -v -deffnm em \n'
      
      #Run nvt
      if os.path.isfile(run_path+'/nvt.gro') is False: 
        groCmd += self.GroLeft+'grompp'+self.GroRight+' -maxwarn 20 -f mdp/nvt.mdp -c em.gro -p topol.top -n index.ndx -o nvt.tpr \n'
        groCmd += self.GroLeft+'mdrun'+self.GroRight+ ' '+self.GroOption+ ' -deffnm nvt -v \n'

      #Run npt
      if os.path.isfile(run_path+'/npt.gro') is False: 
        groCmd += self.GroLeft+'grompp'+self.GroRight+' -maxwarn 20 -f mdp/npt.mdp -c nvt.gro -t nvt.cpt -p topol.top -n index.ndx -o npt.tpr \n'
        groCmd += self.GroLeft+'mdrun'+self.GroRight+ ' '+self.GroOption+ ' -deffnm npt -v \n'

      #Run md
      if os.path.isfile(run_path+'/md.gro') is False:
        groCmd += self.GroLeft+'grompp'+self.GroRight+ ' -maxwarn 20 -f mdp/md.mdp -c npt.gro -t npt.cpt -p topol.top -n index.ndx -o md.tpr \n'
        groCmd += self.GroLeft+'mdrun'+self.GroRight+ ' '+self.GroOption+ ' -deffnm md -v \n'
      
      # if int(Method) == 1:
      if (int(self.repeat_times) == 1 or int(self.repeat_times) == 0 ):
        if(self.GroVersion >= 5):
          self.replaceLine('pull-group2-name', 'pull-group2-name     = '+ligandCurrent+'\n', run_path+'/mdp/md_pull_5.mdp')
          groCmd += self.GroLeft+'grompp'+self.GroRight+ ' -maxwarn 20 -f mdp/md_pull_5.mdp -c md.gro -t md.cpt -p topol.top -n index.ndx -o md_st.tpr \n'
        else:
          self.replaceLine('pull_group1', 'pull_group1     = '+ligandCurrent+'\n', run_path+'/mdp/md_pull.mdp')
          groCmd += self.GroLeft+'grompp'+self.GroRight+ ' -maxwarn 20 -f mdp/md_pull.mdp -c md.gro -t md.cpt -p topol.top -n index.ndx -o md_st.tpr \n'
        
        groCmd += self.GroLeft+'mdrun'+self.GroRight+ ' '+self.GroOption+ ' -px pullx.xvg -pf pullf.xvg -deffnm md_1 -v \n'
      else:
        # Repeat the steered for times
        if(self.GroVersion >= 5):
          self.CallCommand(run_path, 'cp mdp/md_pull_5.mdp mdp/md_pull_repeat.mdp')
          self.replaceLine('continuation', 'continuation  = no   ; Restarting after NPT\n', run_path+'/mdp/md_pull_repeat.mdp')
          self.replaceLine('gen_vel','gen_vel   = yes\ngen_temp = 300\ngen_seed = -1\n', run_path+'/mdp/md_pull_repeat.mdp')
          self.replaceLine('pull-group2-name', 'pull-group2-name     = '+ligandCurrent+'\n', run_path+'/mdp/md_pull_repeat.mdp')
        else:
          self.CallCommand(run_path, 'cp mdp/md_pull.mdp mdp/md_pull_repeat.mdp')
          self.replaceLine('continuation', 'continuation  = no   ; Restarting after NPT\n', run_path+'/mdp/md_pull_repeat.mdp')
          self.replaceLine('gen_vel','gen_vel   = yes\ngen_temp = 300\ngen_seed = -1\n', run_path+'/mdp/md_pull_repeat.mdp')
          self.replaceLine('pull_group1', 'pull_group1     = '+ligandCurrent+'\n', run_path+'/mdp/md_pull_repeat.mdp')
        
        for k in range(0,int(self.repeat_times)):
          if os.path.isfile(run_path+'/md_1_'+str(k)+'.gro') is False:
            groCmd += self.GroLeft+'grompp'+self.GroRight+ ' -maxwarn 20 -f mdp/md_pull_repeat.mdp -c md.gro -t md.cpt -p topol.top -n index.ndx -o md_st_'+str(k)+'.tpr \n'
            groCmd += self.GroLeft+'mdrun'+self.GroRight+ ' '+self.GroOption+ ' -px pullx_'+str(k)+'.xvg -pf pullf_'+str(k)+'.xvg -deffnm md_st_'+str(k)+' -v \n'
            groCmd += 'python2.7 parse_pull.py -x pullx_'+str(k)+'.xvg -f pullf_'+str(k)+'.xvg -o pullfx_'+str(k)+'.xvg\n'
        
      # elif int(Method) == 2:
      #   if os.path.isfile(run_path+'/md_2.gro') is False:
      #     groCmd += GroLeft+'grompp'+GroRight+ ' -maxwarn 20 -f mdp/md_md.mdp -c md.gro -t md.cpt -p topol.top -n index.ndx -o md_2.tpr \n'
      #     groCmd += GroLeft+'mdrun'+GroRight+ ' '+GroOption+ ' -deffnm md_2 -v \n'

      #   groCmd += 'export OMP_NUM_THREADS=4\n'
      #   groCmd += 'echo -e \"Receptor\\n'+ligandCurrent+'\\n\" | g_mmpbsa -f md_2.trr -b 100 -dt 20 -s md_2.tpr -n index.ndx -pdie 2 -decomp \n'
      #   groCmd += 'echo -e \"Receptor\\n'+ligandCurrent+'\\n\" | g_mmpbsa -f md_2.trr -b 100 -dt 20 -s md_2.tpr -n index.ndx -i mdp/polar.mdp -nomme -pbsa -decomp \n'
      #   groCmd += 'echo -e \"Receptor\\n'+ligandCurrent+'\\n\" | g_mmpbsa -f md_2.trr -b 100 -dt 20 -s md_2.tpr -n index.ndx -i mdp/apolar_sasa.mdp -nomme -pbsa -decomp -apol sasa.xvg -apcon sasa_contrib.dat \n'
      #   groCmd += 'python2.7 MmPbSaStat.py -m energy_MM.xvg -p polar.xvg -a sasa.xvg \n'

      self.CallCommand(run_path, groCmd)


  def setupOptions(self):
    gromacs_version = self.dataController.getdata('gromacs_version ')
    version_array = gromacs_version.split(' VERSION ')[1].split('.')
    mdrun_array = gromacs_version.split(' VERSION ')[0].split('mdrun')

    if int(version_array[0]) == 5:
      self.GroLeft = 'gmx '
      self.GroVersion = 5
    else:
      self.GroLeft = mdrun_array[0]
      self.GroVersion = 4
    GroRight = mdrun_array[1]

    # Set number of core or gpu
    check_gpu = check_output(gromacs_version.split(' VERSION ')[0]+" -version", shell=True, executable='/bin/bash').splitlines()
    if( [s for s in check_gpu if "GPU support:" in s][0].split(":")[1].replace(' ','') == 'enable'):
      self.GroOption = '-gpu_id 0'
    else:
      self.GroOption = ''

    #Repeat times 
    self.repeat_times = int(self.dataController.getdata('repeat_times '))

  def CallCommand(self, patch, command):
    call('cd '+patch+'; '+command, shell = True, executable='/bin/bash')

  def replaceLine(self, search, replace, myfile):
    f = open(myfile, "r")
    contents = f.readlines()
    f.close()

    contents[self.substring(search,contents)[0]] = replace

    f = open(myfile, "w")
    contents = "".join(contents)
    f.write(contents)
    f.close()

  def substring(self, mystr, mylist): 
    return [i for i, val in enumerate(mylist) if mystr in val]

if __name__ == '__main__':
  gromacsMD = GromacsMD()
  gromacsMD.setupOptions()
  gromacsMD.mdrun()