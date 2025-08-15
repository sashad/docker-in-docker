#!/usr/bin/env python

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import deploy
import subprocess


def main():
    if deploy.branch_name == deploy.branch_name_prod:
        # Deploy to production.
        pass
    else:
        # Deploy as test branch.

        # output = subprocess.run(
        #         ['git', 'branch'],
        #         capture_output=True,
        #         text=True
        # )
        # branches = map(
        #         lambda y: y.split(' ')[-1],
        #         filter(lambda x: x, output.stdout.split("\n"))
        #     )
        # print(f"Start {list(branches)=}")

        docker_objects = filter(
                lambda x: x,
                subprocess.run(
                    ['docker', 'ps', '-q'],
                    capture_output=True,
                    text=True
                    ).stdout.split("\n")
                )

        used_ips = map(lambda x: deploy.get_info(x), docker_objects)

        # Remove all test config files.
        deploy.clear_configs()

        # Create apache config files for running containers.
        doReload = False
        for container in used_ips:
            if container[0] == deploy.branch_name_prod:
                continue
            elif container[0].find('runner') == 0:
                continue

            deploy.create_config(*container)
            doReload = True
        # writing apache config files are done,

        if doReload:
            # Write a control file to reload apache.
            with open(deploy.apache_conf_dir + "/do.reload", "w") as file:
                file.write("systemctl reload apache2")


if __name__ == '__main__':
    main()
