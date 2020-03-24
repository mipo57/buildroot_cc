#!/usr/bin/python3

import os
from functools import reduce
import json
import re
import argparse

parser = argparse.ArgumentParser(description='Creates a compile_commands.json from buildroot packages by hijacking make commands.')
parser.add_argument('-g', '--generate', action="store_true", help='Generates an example_conf.json configuration file')
parser.add_argument('-c', '--config', type=str, help='Path to the configuration file')
parser.add_argument('-d', '--dry', action="store_true", help='Only prints commands to be executed, does not execute them')
parser.add_argument('--stubs-hard', action="store_true", help="Fix for clang trying to use gnu/stubs-soft.h when gnu/stubs-hard.h is available")
args = parser.parse_args()

DRY = args.dry

if args.generate is None and args.config is None:
    print("You must either use a config or generate one. Exiting...")
    exit(1)

if args.generate:
    example_config = {
        "buildroot_path": "/home/user/buildroot",
        "workspace_path": "/home/project",

        "packages": {
            "wpeframework": "Thunder",
            "wpeframework-plugins": "ThunderNanoServices"
        }
    }

    with open("example_conf.json", "w") as f:
        json.dump(example_config, f, indent=4)

    exit(0)

with open(args.config, "r") as f:
    config = json.load(f)

BUILDROOT_PATH = config['buildroot_path']
WORKSPACE_DIRECTORY = config['workspace_path']
PACKAGES = config['packages']

def execute(command, dry_run=False):
    if dry_run:
        print(command)
    else:
        os.system(command)

os.chdir(BUILDROOT_PATH)
dirclean_command = reduce(lambda s, e: s + f" {e}-dirclean", PACKAGES.keys(), "make")
execute(dirclean_command, DRY)
try:
    execute("bear make", DRY)
except:
    pass # don't care at all...

execute(f"mv compile_commands.json {WORKSPACE_DIRECTORY}", DRY)

with open(f"{WORKSPACE_DIRECTORY}/compile_commands.json", "r") as f:
    compile_commands = json.load(f)

for entry in compile_commands:
    if args.stubs_hard:
        i = entry['arguments'].index("-c") + 2 # TODO: Make less hacky...
        entry['arguments'].insert(i, "-D__ARM_PCS_VFP")

    for buildroot_package, workspace_pakage in PACKAGES.items():
        entry['directory'] = re.sub(fr"{BUILDROOT_PATH}/.*?/{buildroot_package}-.*?/", f"{WORKSPACE_DIRECTORY}/{workspace_pakage}/", entry['directory'])

with open(f"{WORKSPACE_DIRECTORY}/compile_commands.json", "w") as f:
    json.dump(compile_commands, f, indent=4)

print("\n\n\n\n")
print("##############")
print("##   DONE   ##")
print("##############")