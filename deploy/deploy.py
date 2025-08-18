#!/usr/bin/env python

import os
import subprocess
import shutil


apache_conf_dir = "/mnt/apache2"
test_stands_dir = "/mnt/odoo-test-stands"
domain = "test.1vp.ru"
release_branch = "main"
apache_config_file_name = "branch.*.ssl.conf"
t_branch = "%%branch%%"
t_domain = "%%domain%%"
t_ip = "%%container_ip%%"
branch_name = os.environ['CI_COMMIT_BRANCH']
branch_name_prod = 'main'
skipped_names = ['.git', '.gitlab-ci.yml', '.gitignore', '.ruff.toml']


def copy_current_dir_to_destination(destination_dir):
    """
    Copies the contents of the current directory to the destination directory.
    The destination directory is cleared before copying.

    Args:
        destination_dir (str): Path to the destination directory.

    Example usage:
        copy_current_dir_to_destination("/path/to/destination")
    """
    # Ensure the destination directory exists
    os.makedirs(destination_dir, exist_ok=True)

    # Clear the destination directory
    for filename in os.listdir(destination_dir):
        file_path = os.path.join(destination_dir, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

    # Copy contents of the current directory to the destination directory
    current_dir = os.getcwd()
    for item in os.listdir(current_dir):
        if item in skipped_names:
            continue
        src_path = os.path.join(current_dir, item)
        dst_path = os.path.join(destination_dir, item)
        if os.path.isdir(src_path):
            shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
        else:
            shutil.copy2(src_path, dst_path)


def get_info(docker_object_id):
    command = [
        "docker",
        "inspect",
        "docker object id",
        "--format={{ printf \"%s\" .Name}}"
        " {{range .NetworkSettings.Networks}}{{.IPAddress}} {{end}}"
    ]
    # Use subprocess.run to execute the command
    output = subprocess.run(
            [*command[0:2], docker_object_id, command[-1]],
            capture_output=True,
            text=True,
            shell=False
        )
    if not output.stderr:
        return output.stdout.strip()[1:].split()


def clear_configs():
    """Remove all config files for test containers."""

    subprocess.run(
            [
                'rm',
                '-f',
                f"{apache_conf_dir}/sites-enabled/{apache_config_file_name}"
            ],
            capture_output=False,
            text=True,
            shell=False
        )


def create_config(branch, ip):
    """Create a config file for test container."""

    branch = branch.replace('/', '-').replace('.', '-')
    with open(
            f"{os.path.dirname(os.path.abspath(__file__))}/site-ssl.conf",
            'r'
    ) as conf:
        conf_text = conf.read()
        conf_text = conf_text.replace(t_branch, branch)
        conf_text = conf_text.replace(t_domain, domain)
        conf_text = conf_text.replace(t_ip, ip)
        file_name = apache_config_file_name.replace('*', branch)
        with open(
                f"{apache_conf_dir}/sites-enabled/{file_name}",
                'w'
        ) as w_conf:
            w_conf.write(conf_text)


def create_docker_compose_config():
    """Create a config file for starting test container."""

    with open(
            f"{test_stands_dir}/docker-compose.yml.template",
            'r'
    ) as conf:
        conf_text = conf.read()
        conf_text = conf_text.replace(t_branch, branch_name)
        with open(
                f"{test_stands_dir}/docker-compose.{branch_name}.yml",
                'w'
        ) as w_conf:
            w_conf.write(conf_text)

    return True


def main():
    if branch_name == branch_name_prod:
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

        used_ips = map(lambda x: get_info(x), docker_objects)

        if create_docker_compose_config():
            copy_current_dir_to_destination(f"{test_stands_dir}/{branch_name}")

        # Remove all test config files.
        clear_configs()

        # Create apache config files for running containers.
        doReload = False
        for container in used_ips:
            if container[0] == branch_name_prod:
                continue
            elif container[0].find('runner') == 0:
                continue

            create_config(*container)
            doReload = True
        # writing apache config files are done,

        if doReload:
            # Write a control file to reload apache.
            with open(apache_conf_dir + "/do.reload", "w") as file:
                file.write(
                        f"systemctl reload apache2;"
                        f" rm -f {apache_conf_dir}do.reload\n"
                    )


if __name__ == '__main__':
    main()
