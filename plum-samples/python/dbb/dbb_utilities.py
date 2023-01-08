#*******************************************************************************
# Licensed Materials - Property of IBM
# (c) Copyright IBM Corp. 2023. All Rights Reserved.
#
# Note to U.S. Government Users Restricted Rights:
# Use, duplication or disclosure restricted by GSA ADP Schedule
# Contract with IBM Corp.
#*******************************************************************************
import json
import yaml
import sys
import re

from plum_py.service.utilities import Utilities

class GitUtilities(object):
     
    @staticmethod
    def get_current_git_hash(git_dir: str):
        #cmd = f"git -C {git_dir} rev-list -1 --abbrev=8 HEAD {file_path}"
        cmd = f"git -C {git_dir} rev-parse --short=8 HEAD"
        rc, out, err = Utilities.run_command(cmd)
        if rc != 0:
            msgstr = f"*! Error executing Git command: {cmd} error: {err}"
            print(msgstr)
        return out.strip()
    
    @staticmethod
    def get_current_git_url(git_dir: str):
        cmd = f"git -C {git_dir} config --get remote.origin.url"
        rc, out, err = Utilities.run_command(cmd)
        if rc != 0:
            msgstr = f"*! Error executing Git command: {cmd} error: {err}"
            print(msgstr)
        return out.strip()
    
    @staticmethod
    def get_current_git_branch(git_dir: str):
        cmd = f"git -C {git_dir} rev-parse --abbrev-ref HEAD"
        rc, out, err = Utilities.run_command(cmd)
        if rc != 0:
            msgstr = f"*! Error executing Git command: {cmd} error: {err}"
            print(msgstr)
        return out.strip()
    
    @staticmethod
    def is_git_detached_head(git_dir: str):
        cmd = f"git -C {git_dir} status"
        rc, out, err = Utilities.run_command(cmd)
        if rc != 0:
            msgstr = f"*! Error executing Git command: {cmd} error: {err}"
            print(msgstr)
    
        return "HEAD detached at" in out.strip()

    @staticmethod
    def get_current_git_detached_branch(git_dir: str):
        cmd = f"git -C {git_dir} show -s --pretty=%D HEAD"
        rc, out, err = Utilities.run_command(cmd)
        if rc != 0:
            msgstr = f"*! Error executing Git command: {cmd} error: {err}"
            print(msgstr)
            
        git_branch_string = out.strip()
        git_branch_arr = git_branch_string.split(',')
        solution = ""
        for branch in git_branch_arr:
            if "origin/" in branch:
                solution = re.sub('.*?/', '', branch).strip()
        if solution == "":
            print(f"*! Error parsing branch name: {branch}")
        else:
            return solution

class DBBUtilities(object):
    
    @staticmethod
    def filter_deployable_records(record) -> bool:
        try:
            if (record['type'] == 'EXECUTE' or record['type'] == 'COPY_TO_PDS') and len(record['outputs']) > 0:
                for output in record['outputs']:
                    try:
                        if output['deployType']:
                            record['deployType']=output['deployType']
                            record['dataset']=output['dataset']
                            return True
                    except:
                        pass
        except:
            pass
        return False

    @staticmethod
    def read_build_result(read_build_result_file) -> dict:
        with open(read_build_result_file) as read_file:
            return dict(json.load(read_file))
        
        
    @staticmethod
    def get_copy_mode(deployType:str = "LOAD", **kwargs) -> str:
        if kwargs.get('copyModeProperties') != None:
            props = {}
            props_yaml_file = kwargs['copyModeProperties']
            try:
                with open(props_yaml_file, 'r') as stream:
                    props = dict (yaml.safe_load(stream))
                    if props.get(deployType) != None:
                        return props.get(deployType)
            except IOError as error: 
                print(error, file=sys.stderr)
                raise RuntimeError(f"!!! Couldn't open target environment file from: {props_yaml_file} !!!")
        if re.search('LOAD', deployType, re.IGNORECASE):
            return "LOAD"
        elif re.search('DBRM', deployType, re.IGNORECASE):
            return "BINARY"
        elif re.search('TEXT', deployType, re.IGNORECASE):
            return "TEXT"
        elif re.search('COPY', deployType, re.IGNORECASE):
            return "TEXT"
        elif re.search('OBJ', deployType, re.IGNORECASE):
            return "BINARY"
        elif re.search('DDL', deployType, re.IGNORECASE):
            return "TEXT"
        elif re.search('JCL', deployType, re.IGNORECASE):
            return "TEXT"
        else:
            return "TEXT"