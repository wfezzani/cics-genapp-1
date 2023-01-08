#*******************************************************************************
# Licensed Materials - Property of IBM
# (c) Copyright IBM Corp. 2023. All Rights Reserved.
#
# Note to U.S. Government Users Restricted Rights:
# Use, duplication or disclosure restricted by GSA ADP Schedule
# Contract with IBM Corp.
#*******************************************************************************

import argparse
import sys
import os
import platform
import re

from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from plum_py.service.utilities import Utilities
from python.dbb.dbb_utilities import DBBUtilities

def copy_dbb_build_result_to_local_folder(**kwargs):
    dbb_build_result_file = kwargs['dbbBuildResult']
    working_folder = kwargs['workingFolder']
   
    # Units
    buildResult = DBBUtilities.read_build_result(dbb_build_result_file)
    
    records = list(filter(lambda record: DBBUtilities().filter_deployable_records(record),buildResult['records']))
    for record in records:
        dataset = record['dataset']
        deploy_type = record['deployType']
        parts = re.split('\\(|\\)',dataset)
        member_name = parts[1]
        pds_name = parts[0]
    
        # Build the local_folder from DBB Build Outputs
        msgstr = f"** Copy //'{dataset}' to {working_folder}/{pds_name}/{member_name}.{deploy_type}"
        print(msgstr)
        
        os.makedirs(f"{working_folder}/{pds_name}", exist_ok=True)
        copyMode = DBBUtilities.get_copy_mode(deploy_type, **kwargs)
        if copyMode == 'LOAD':
            cmd = f"cp -X //'{dataset}' {working_folder}/{pds_name}/{member_name}.{deploy_type}"

        elif copyMode == 'BINARY':
            cmd = f"cp -F bin //'{dataset}' {working_folder}/{pds_name}/{member_name}.{deploy_type}"
        else:
            cmd = f"cp //'{dataset}' {working_folder}/{pds_name}/{member_name}.{deploy_type}"

        if platform.system() == 'OS/390':
            rc, out, err = Utilities.run_command(cmd)
            if rc != 0:
                msgstr = f"*! Error executing command: {cmd} out: {out} error: {err}"
                print(msgstr)
                sys.exit(-1)
            cmd = f"chtag -b {working_folder}/{pds_name}/{member_name}.{deploy_type}"
            rc, out, err = Utilities.run_command(cmd)
            if rc != 0:
                msgstr = f"*! Error executing command: {cmd} out: {out} error: {err}"
                print(msgstr)
                sys.exit(-1)
    
def main(): 
    
        parser = argparse.ArgumentParser(description="DBB Prepare Package")
        parser.add_argument('-br', '--dbbBuildResult', required=True, help='The DBB build result file')
        parser.add_argument('-wf', '--workingFolder', required=True, help='The path to the working folder')
        parser.add_argument('-cp', '--copyModeProperties', help='The path to the file that contains copy mode properties')
        
        if len(sys.argv[1:]) == 0:
            parser.print_help()
            return

        args = parser.parse_args()
        
        kwargs=vars(args)

        copy_dbb_build_result_to_local_folder (**kwargs)
        

if __name__ == '__main__':
    main()