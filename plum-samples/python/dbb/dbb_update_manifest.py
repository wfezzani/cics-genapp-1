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

from pathlib import Path
import yaml
import re

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from python.dbb.dbb_utilities import DBBUtilities
from plum_py.service.utilities import Utilities
from python.dbb.dbb_utilities import GitUtilities

        
def dbb_update_manifest(**kwargs):
    dbb_build_result_file = kwargs['dbbBuildResult']
    source_folder = kwargs['sourceFolder']
    manifest_file = kwargs['manifest']

    print((f"** Update the manifest {manifest_file}"))
    buildResult = DBBUtilities.read_build_result(dbb_build_result_file)
    records = list(filter(lambda record: DBBUtilities().filter_deployable_records(record),buildResult['records']))
    
    with open(manifest_file, 'r') as stream:
        manifest_dic = dict (yaml.safe_load(stream))
        

    scm = {}
    scm['type'] = 'git'
    scm['uri'] = re.sub(r'\/.*@', '//', GitUtilities.get_current_git_url (source_folder))
    if GitUtilities.is_git_detached_head(source_folder):
        scm['branch'] = GitUtilities.get_current_git_detached_branch(source_folder)
    else:
        scm['branch'] = GitUtilities.get_current_git_branch (source_folder)
    scm['short_commit'] = GitUtilities.get_current_git_hash (source_folder)
    manifest_dic['metadata']['annotations']['scm'] = scm
        
    for record in buildResult['records']:
        if record.get('url') is not None:
            manifest_dic['metadata']['annotations']['dbb'] = {}
            manifest_dic['metadata']['annotations']['dbb']['build_result_uri'] = record.get('url')
            break
    
    #===========================================================================
    # zAppBuild not ready for that. Example if we delete a COBOL DB2 the related DBRM
    # will not be in the deletion list.  
    # # Handle deleted records
    # deleted_records = list(filter(lambda record: DBBUtilities().filter_deleted_records(record),buildResult['records']))
    # if len(deleted_records) > 0 :
    #     deleted_artifacts = []
    #     for artifact in manifest_dic['artifacts']:
    #         path_prop = list(filter(lambda prop: ('path' == prop['key']), artifact['properties']))
    #         path = path_prop[0]['value']
    #         dataset = path.replace('/', '(')[0:path.rindex('.')]+')'
    #         for deleted_record in deleted_records:
    #             if len(list(filter(lambda output: (output == dataset), deleted_record['deletedBuildOutputs']))) > 0:
    #                 if not artifact in deleted_artifacts:
    #                     deleted_artifacts.append(artifact)
    #     if len(deleted_artifacts) > 0:
    #         artifacts = manifest_dic['artifacts']
    #         for deleted_artifact in deleted_artifacts:
    #             artifacts.remove(deleted_artifact)
    #===========================================================================
    
    for record in records:
        dataset = record['dataset']
        deploy_type = record['deployType']
        parts = re.split('\\(|\\)',dataset)
        member_name = parts[1]
        pds_name = parts[0]
        
        for artifact in manifest_dic['artifacts']:
            if artifact['name'] == member_name:
                path_prop = list(filter(lambda prop: ('path' == prop['key']), artifact['properties']))
                if len(path_prop) > 0:
                    path = path_prop[0]['value']
                    parts = re.split('/',path)
                
                if parts[0] == pds_name:
                    copyMode = DBBUtilities.get_copy_mode(artifact['type'], **kwargs)
                        
                    if copyMode == 'LOAD':
                        fingerprint = Utilities.get_loadmodule_idrb(f"{pds_name}({artifact['name']})")
                    else:
                        fingerprint = artifact['hash']
                    
                    msgstr = f"** Register fingerprint for '{pds_name}({artifact['name']})':  {fingerprint}"
                    print(msgstr)
                    
                    fingerprint_prop = list(filter(lambda prop: ('fingerprint' == prop['key']), artifact['properties']))
                    if len(fingerprint_prop) > 0:
                        fingerprint_prop[0]['value'] = f"{fingerprint}"
                    else:
                        artifact['properties'].append(
                            {"key": "fingerprint",
                             "value": f"{fingerprint}"})
            
    Utilities.dump_to_yaml_file(manifest_dic, manifest_file)

    
def main(): 
    
        parser = argparse.ArgumentParser(description="DBB Update Manifest")
        parser.add_argument('-br', '--dbbBuildResult', required=True, help='The DBB build result file')
        parser.add_argument('-sf', '--sourceFolder', required=True, help='The path to the source folder')
        parser.add_argument('-m', '--manifest', help='The path to the manifest to update')
        
        if len(sys.argv[1:]) == 0:
            parser.print_help()
            return

        args = parser.parse_args()
        
        kwargs=vars(args)

        dbb_update_manifest (**kwargs)
        

if __name__ == '__main__':
    main()