## Set work directory
import os

def workdirectory():
#    work_dir = os.path.dirname(__file__)
    project_dir = "D:\\Projects\\2016_NFP73\\Framework"
    work_dir = os.path.join(project_dir, 'Cohort')
    data_dir = os.path.join(project_dir, 'Data')
    temp_dir = os.path.join(project_dir, 'Temp')
    os.chdir(work_dir)
    return [work_dir, project_dir, temp_dir, data_dir]

