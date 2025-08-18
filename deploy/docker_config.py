#!/usr/bin/env python

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import deploy


def main():
    # Deploy a testing stand.
    if deploy.create_docker_compose_config():
        deploy.copy_current_dir_to_destination(
            f"{deploy.test_stands_dir}/{deploy.branch_name}"
        )


if __name__ == '__main__':
    main()
